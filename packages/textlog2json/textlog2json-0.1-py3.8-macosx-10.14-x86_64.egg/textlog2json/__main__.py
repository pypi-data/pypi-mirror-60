import click
import os
from textlog2json.processor import Processor
from textlog2json.simple_processor import SimpleProcessor
from logging import getLogger
from textlog2json.cluster_storage import ClusterStorage
from logging.config import fileConfig
from sqlalchemy import create_engine
from textlog2json.db_sync import DBSync
from multiprocessing import cpu_count

@click.command()
@click.option('--distance-treshold', 'distance_treshold',
              default=0.5,
              help='Maximum distance up to which messages go into one cluster, defaults to 0.')
@click.option('--db', 'db',
              default="sqlite:///:memory:",
              help='Sqlalchemy url to database where the knowledge base is stored in, defaults to an in memory db.')
@click.option('--in', 'input_file',
              default="-",
              type=click.File('r'),
              help='File to write messages to, defaults to stdout.')
@click.option('--out', 'output_file',
              default="-",
              type=click.File('w'),
              help='File to read messages from, defaults to stdin.')
@click.option('--in-format', 'input_format',
              default='text',
              help='can be json or text (line seperated log files)')
@click.option('--message-field', 'message_field',
              default='message',
              help='The field containing the message, only used with in-format=json')
@click.option('--sync-period', 'sync_period',
              default=300,
              help='Sync with db every n seconds, defaults to 300.')
@click.option('--sync-jitter', 'sync_jitter',
              default=60,
              help='Maximum number of seconds to randomly add or delete from sync period.')
@click.option('--logging.config', 'logging_config',
              default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'logging_config.ini'),
              help='Path to logging configuration file.')
@click.option('--processes', 'num_processors',
              default=cpu_count(),
              help='Number of processes to use. Only works on unix with standard processor.')
@click.option('--processor', 'processor_type',
              default='standard',
              help='Processor to use. "simple" only uses one process and works on windows. Standard uses multiple processes.')
def cli(distance_treshold, db, sync_period, sync_jitter, logging_config, message_field, input_file, output_file, num_processors, input_format, processor_type):
    """Automatically transform unstructured log messages into structured JSON.
    Reads messages from a json stream and outputs messages with the additional extracted information to a json stream.
    Continuously learns from input and synchronises its knowledge base with a remote db."""

    if processor_type != 'standard' and processor_type != 'simple':
        raise ValueError('Invalid value for argument processor must be "simple" or "standard"')

    fileConfig(logging_config)
    logger = getLogger()

    if os.name != 'posix' and processor_type != 'simple':
        logger.warning('On non posix systems only the "simple" processor is supported, falling back to simple processor')
        processor_type = 'simple'

    engine = create_engine(db, strategy='threadlocal')
    cluster_storage = ClusterStorage(distance_treshold)
    db_sync = DBSync(cluster_storage, engine)

    if processor_type == 'standard':
        processor = Processor(cluster_storage, db_sync, sync_period, sync_jitter, logger, message_field, input_file, output_file, num_processors, input_format)
    else:
        processor = SimpleProcessor(cluster_storage, db_sync, sync_period, sync_jitter, logger, message_field, input_file, output_file, input_format)
    processor.run()

if __name__ == '__main__':
    cli()
