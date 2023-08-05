import json

from textlog2json.cluster_store_sync import ClusterStoreSync
from os import fork, pipe, _exit, urandom
from multiprocessing import Queue, JoinableQueue, Event
from queue import Empty
from time import sleep, time
from random import randint
from threading import Thread, Lock
from random import seed, SystemRandom

class Processor:
    def __init__(
        self,
        cluster_store,
        db_sync,
        sync_period,
        sync_jitter,
        logger,
        message_field,
        input_file,
        output_file,
        num_processors,
        input_format
    ):
        self._sync_period = sync_period
        self._sync_jitter = sync_jitter
        self._message_field = message_field
        self._input_file = input_file
        self._output_file = output_file
        self._num_processors = num_processors

        self._worker_pids = []
        self._input_queue = JoinableQueue(maxsize=10)
        self._output_queue = JoinableQueue(maxsize=10)
        self._cluster_store_deltas = Queue()
        self._stop_workers = Event()
        self._stop_output = Event()
        self._input_finished = Event()

        self._batch_size = 100
        self._flush_after_seconds = 3

        self.logger = logger

        self.cs = cluster_store
        self._dbSync = db_sync
        self._cluster_store_sync = ClusterStoreSync(self.cs)

        self._input_format = input_format

    def _doDbSync(self):
        try:
            self._dbSync.sync()
        except Exception as e:
            self.logger.exception(e)

    def _process_messages(self):
        """ Process messages on the input queue, write the result to the output queue. """

        while not self._stop_workers.is_set():
            try:
                lines = self._input_queue.get(True, 0.1)
                try:
                    output_lines = []
                    for line in lines:
                        try:
                            if self._input_format == "text":
                                msg_dict = {}
                                self.cs.processMsg(line, msg_dict)
                                output_lines.append(json.dumps(msg_dict))
                            elif self._input_format == "json":
                                msg_dict = json.loads(line)
                                if not self._message_field in msg_dict:
                                    self.logger.error("found no message field '%s' in input line '%s'" % (self._message_field, line))
                                    continue

                                msg = msg_dict[self._message_field]
                                self.cs.processMsg(msg, msg_dict)
                                output_lines.append(json.dumps(msg_dict))
                            else:
                                raise Exception('invalid input format "%s" has to be text or json' % (self._input_format))
                        except:
                            self.logger.exception('failed to process line "%s"' % (line))
                    self._output_queue.put(output_lines)
                finally:
                    self._input_queue.task_done()
            except Empty:
                continue

    def _dump_modifications(self):
        """ Send information about the modifications this worker has made to the cluster storage back to the main process. """

        (modified_clusters, new_clusters) = self.cs.getDelta()
        size = max(len(modified_clusters), len(new_clusters))
        i = 0
        while i < size:
            next = i + self._batch_size
            m = modified_clusters[i:next]
            n = new_clusters[i:next]
            self._cluster_store_deltas.put((m,n))
            i = next

    def _line_reader_process(self):
        """ Read in lines from the input file and send them to the input queue """

        lines = []
        lines_lock = Lock()
        last_flushed = time()

        def flush():
            nonlocal last_flushed
            nonlocal lines

            if len(lines) > 0:
                with lines_lock:
                    last_flushed = time()
                    self._input_queue.put(lines)
                    lines = []

        # Flush buffers after 3 seconds.
        def flush_thread_func():
            nonlocal last_flushed

            while not self._input_finished.is_set():
                sleep(1)
                if (time() - last_flushed) >= self._flush_after_seconds:
                    flush()

        flush_thread = Thread(target=flush_thread_func)
        flush_thread.start()

        try:
            line = self._input_file.readline()
            while line:
                with lines_lock:
                    lines.append(line)
                if (len(lines) >= self._batch_size):
                    flush()
                line = self._input_file.readline()
            flush()
        finally:
            self._input_file.close()
            self._input_finished.set()
            flush_thread.join()

    def run(self):
        """ The main coordination process """

        pid = fork()
        if pid == 0:
            self._line_reader_process()
            _exit(0)
        else:
            self._input_file.close()
            self._line_reader_process_pid = pid

        pid = fork()
        if pid == 0:
            self._writer_process()
            _exit(0)
        else:
            self._output_file.close()
            self._writer_process_pid = pid

        self._manage_workers()
        self._output_queue.join()
        self._stop_output.set()

    def _manage_workers(self):
        seed(SystemRandom().getrandbits(128))
        while not self._input_finished.is_set():
            self._join_workers()
            self._doDbSync()
            self._spawn_workers()

            seconds_till_sync = self._sync_period + randint(-self._sync_jitter, +self._sync_jitter)
            for i in range(seconds_till_sync):
                if self._input_finished.is_set():
                    break
                sleep(1)

        self._input_queue.join()
        self._join_workers()
        self._doDbSync()

    def _worker_process(self):
        """ The worker process that process messages """

        seed(SystemRandom().getrandbits(128))

        try:
            self._process_messages()
        finally:
            try:
                self._dump_modifications()  # Send info about modifications back to main process.
            finally:
                self._cluster_store_deltas.put(None)
        return


    def _writer_process(self):
        """ Process that writes messages from the output queue to the output file """

        try:
            while not self._stop_output.is_set():
                try:
                    msgs = self._output_queue.get(True, 0.1)
                    try:
                        for msg in msgs:
                            self._output_file.write(msg + '\n')
                        self._output_file.flush()
                    finally:
                        self._output_queue.task_done()
                except Empty:
                    continue
        finally:
            self._output_file.close()


    def _spawn_workers(self):
        """ Fork worker processes """

        for i in range(self._num_processors):
            pid = fork()
            if pid == 0:
                self._worker_process()
                self._cluster_store_deltas.close()
                self._cluster_store_deltas.join_thread()
                _exit(0)
            else:
                self._worker_pids.append(pid)


    def _join_workers(self):
        """ Stop workers and join their modifications into the main process """

        self._stop_workers.set()

        # Sync with all workers.
        try:
            counter = len(self._worker_pids)
            while counter != 0:
                delta = self._cluster_store_deltas.get()
                if delta == None:
                    counter = counter -1
                else:
                    self._cluster_store_sync.sync(delta)
        except Empty:
            pass

        self._stop_workers.clear()
        self._worker_pids = []
