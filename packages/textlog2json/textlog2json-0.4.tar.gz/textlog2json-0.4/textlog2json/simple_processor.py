import json

import sys
from textlog2json.cluster_store_sync import ClusterStoreSync
from multiprocessing import Queue, JoinableQueue, Event
from queue import Empty
from time import sleep, time
from random import randint
from threading import Thread, Lock
from random import seed, SystemRandom


class SimpleProcessor:
    """ A simple processor that only uses one process and works on windows. """
    """ DB sync can only occur after a line has been read.  """
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
        input_format
    ):
        self._sync_period = sync_period
        self._sync_jitter = sync_jitter
        self._message_field = message_field
        self._input_file = input_file
        self._output_file = output_file

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

    def _process_message(self, line):
        """ Process messages on the input queue, write the result to the output queue. """
        try:
            if self._input_format == "text":
                msg_dict = {}
                self.cs.processMsg(line, msg_dict)
                return json.dumps(msg_dict)
            elif self._input_format == "json":
                msg_dict = json.loads(line)
                if not self._message_field in msg_dict:
                    raise Exception("found no message field '%s' in input line '%s'" % (self._message_field, line))

                msg = msg_dict[self._message_field]
                self.cs.processMsg(msg, msg_dict)
                return json.dumps(msg_dict)
            else:
                raise Exception('invalid input format "%s" has to be text or json' % (self._input_format))
        except:
            self.logger.exception('failed to process line "%s": %s' % (line, sys.exc_info()[0]))

    def run(self):
        """ The main coordination process """

        next_sync_time = 0
        try:
            line = self._input_file.readline()
            while line:
                if int(time()) >= next_sync_time:
                    seconds_till_sync = self._sync_period + randint(-self._sync_jitter, +self._sync_jitter)
                    next_sync_time = int(time()) + seconds_till_sync

                    self._doDbSync()

                msg = self._process_message(line)
                if msg is not None:
                    self._output_file.write(msg + '\n')

                line = self._input_file.readline()
        finally:
            self._input_file.close()
            self._output_file.close()

            self._doDbSync()
