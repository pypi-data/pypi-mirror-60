from textlog2json.cluster_storage import ClusterStorage, Cluster

import sqlalchemy
import socket
from os import getpid
from threading import get_ident
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from textlog2json.pattern_format import pattern_deserialize

tables_metadata = sqlalchemy.MetaData()

cluster_table = sqlalchemy.Table('cluster', tables_metadata,
    sqlalchemy.Column('guid', sqlalchemy.String(32), primary_key=True, nullable=False),
    sqlalchemy.Column('name', sqlalchemy.String(128), nullable=True),
    sqlalchemy.Column('count', sqlalchemy.BigInteger, nullable=False),
    sqlalchemy.Column('utime', sqlalchemy.DateTime, server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(), nullable=False),
    sqlalchemy.Column('pattern', sqlalchemy.TEXT, nullable=False),
    sqlalchemy.Column('pattern_hash', sqlalchemy.String(32), nullable=False),
    sqlalchemy.Column('deleted_flag', sqlalchemy.Boolean, nullable=False, default=False),
)

regexp_table = sqlalchemy.Table('regexps', tables_metadata,
    sqlalchemy.Column('regexp', sqlalchemy.String(256), nullable=False),
    sqlalchemy.Column('guid', sqlalchemy.String(32), nullable=False)
)

lock_table = sqlalchemy.Table('locks', tables_metadata,
    sqlalchemy.Column('name', sqlalchemy.String(128), primary_key=True, nullable=False),
    sqlalchemy.Column('hostname', sqlalchemy.String(256)),
    sqlalchemy.Column('process_id', sqlalchemy.BigInteger),
    sqlalchemy.Column('thread_id', sqlalchemy.BigInteger),
    sqlalchemy.Column('comment', sqlalchemy.String(256)),
    sqlalchemy.Column('time', sqlalchemy.DateTime, server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(), nullable=False),
)

class DBSync():
    def __init__(self, cs: ClusterStorage, engine):
        self.cs = cs
        self.last_synced = None
        self.engine = engine
        tables_metadata.create_all(self.engine)

        # For sqlite we always want to use exclusive transactions.
        # See http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html.
        if self.engine.dialect.name.startswith("sqlite"):
            @event.listens_for(self.engine, "connect")
            def do_connect(dbapi_connection, connection_record):
                dbapi_connection.isolation_level = None

            @event.listens_for(self.engine, "begin")
            def do_begin(conn):
                conn.execute("BEGIN EXCLUSIVE")

        with self.engine.connect() as conn:
            for lock_name in ['cluster']:
                trans = conn.begin()
                try:
                    ins = lock_table.insert().values(name=lock_name)
                    conn.execute(ins)
                    trans.commit()
                except IntegrityError:
                    trans.rollback()
                    pass

    def sync(self):
        """ Sync with db """
        with self.engine.connect() as conn:
            trans = conn.begin()
            try:
                self._acquire_db_lock(conn, "cluster", "textlog2json sync")
                self._fetch_regexps(conn)
                self._fetch_updates(conn)
                self._upload_new_clusters(conn)
                self._update_modified_clusters(conn)
                self._send_deletes(conn)

                # Sync time
                query = sqlalchemy.sql.select([sqlalchemy.func.now()])
                result_set = conn.execute(query)
                try:
                    row = result_set.fetchone()
                    if not row:
                        raise Exception('failed to synchronize time with sql server')
                    self.last_synced = str(row[0])
                finally:
                    result_set.close()

                trans.commit()
            except:
                trans.rollback()
                raise

    def _acquire_db_lock(self, conn, name, comment):

        # Make sure we acquire a read and a write lock.
        select = lock_table.select(lock_table.c.name == name, for_update=True)
        result_set = conn.execute(select)
        result_set.close()

        upd = lock_table.update().values(
            name=name,
            hostname=socket.gethostname(),
            process_id=getpid(),
            thread_id=get_ident(),
            comment=comment
        ).where(lock_table.c.name == name)
        conn.execute(upd)

    def _fetch_regexps(self, conn):
        """ Download the list of regexps and combine them into one big regexp """

        query = sqlalchemy.sql.select([regexp_table])
        result_set = conn.execute(query)
        regexps = []
        for row in result_set:
            if not (('guid' in row) and (type(row['guid']) is str) and (row['guid'] != "")):
                raise Exception('malformed regex row: invalid guid')

            if not (('regexp' in row) and (type(row['regexp']) is str) and (row['regexp'] != "")):
                raise Exception('malformed regex row: invalid regexp')

            regexps.append((row['guid'], row['regexp']))

        self.cs.set_manual_matches_regexp(regexps)

    def _fetch_updates(self, conn):
        """ Get all clusters since last sync and merge them into the current cluster list """

        query = sqlalchemy.sql.select([cluster_table])

        if self.last_synced != None:
            query = query.where(cluster_table.c.utime > self.last_synced)

        result_set = conn.execute(query)
        try:
            for row in result_set:
                if not (('guid' in row) and (type(row['guid']) is str) and (row['guid'] != "")):
                    raise Exception('malformed cluster row')

                if ('deleted_flag' in row) and row['deleted_flag']:
                    c = Cluster(None)
                    c.guid = row['guid']
                    self.cs.deleteCluster(c)
                    try:
                        self.cs.cluster_deleted.pop(c.guid)
                    except KeyError:
                        pass
                    continue

                if not (
                        ('guid' in row) and (type(row['guid']) is str) and (row['guid'] != "")
                        and ('name' in row) and ((row['name'] == None) or (type(row['name']) is str))
                        and ('pattern' in row) and (type(row['pattern']) is str)
                        and ('pattern_hash' in row) and (type(row['pattern_hash']) is str)
                ):
                    raise Exception('malformed cluster row')

                pattern = pattern_deserialize(row['pattern'])
                cluster = Cluster(pattern)
                cluster.name = row['name']
                cluster.guid = row['guid']
                cluster.pattern_hash = row['pattern_hash']

                if row['guid'] in self.cs.cluster_dict:
                    self.cs.mergeClusters(cluster, self.cs.cluster_dict[row['guid']])
                    self.cs.mark_as_modified(cluster)
                else:
                    keyword_count = self.cs.get_keyword_count(cluster)
                    found_cluster = self.cs.find(cluster, keyword_count)
                    if not found_cluster is None:
                        self.cs.mergeClusters(cluster, found_cluster)
                        self.cs.deleteCluster(found_cluster)
                        self.cs.mark_as_modified(cluster)
                    else:
                        self.cs.cluster_dict[cluster.guid] = cluster
                    self.cs.keywords_index(cluster, keyword_count)

        finally:
            result_set.close()

    def _send_deletes(self, conn):
        """ Mark deleted clusters as deleted, on remote """

        for guid in self.cs.cluster_deleted:
            upd = cluster_table.update().values(
                deleted_flag=True,
            ).where(cluster_table.c.guid == guid)
            conn.execute(upd)
        self.cs.cluster_deleted = {}

    def _upload_new_clusters(self, conn):
        """ Upload all newly created clusters  """

        for guid in self.cs.new_clusters:
            cluster = self.cs.new_clusters[guid]
            pattern_json = cluster.serializePattern()
            ins = cluster_table.insert().values(
                guid=cluster.guid,
                count=cluster.counter,
                pattern=pattern_json,
                pattern_hash=cluster.pattern_hash,
                name=cluster.name
            )
            conn.execute(ins)

            cluster.counter = 0

        self.cs.new_clusters = {}

    def _update_modified_clusters(self, conn):
        """ Update all modified clusters """

        for guid in self.cs.cluster_modified:
            cluster = self.cs.cluster_modified[guid]
            old_pattern_hash = cluster.pattern_hash
            pattern_json = cluster.serializePattern()
            if old_pattern_hash != cluster.pattern_hash:
                upd = cluster_table.update().values(
                    count=cluster_table.c.count + cluster.counter,
                    pattern=pattern_json,
                    pattern_hash=cluster.pattern_hash,
                    name=cluster.name
                ).where(cluster_table.c.guid == cluster.guid)
                conn.execute(upd)
            else:
                upd = cluster_table.update().values(
                    count=cluster_table.c.count + cluster.counter,
                    name=cluster.name
                ).where(cluster_table.c.guid == cluster.guid)
                conn.execute(upd)

        self.cs.cluster_modified = {}
