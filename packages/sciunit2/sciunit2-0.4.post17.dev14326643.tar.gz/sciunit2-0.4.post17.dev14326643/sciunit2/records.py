#Note: Converted
# Module bsddb3 cannot be installed on this machine, other machines are fine
from __future__ import absolute_import

from sciunit2.exceptions import CommandError, MalformedExecutionId
from sciunit2 import timestamp

import os
import fcntl
import json
import re
import sqlite3

from sqlite3 import Error
from contextlib import closing
from tempfile import NamedTemporaryFile


class Metadata(object):
    __slots__ = '__d'

    def __init__(self, args):
        if isinstance(args, list):
            self.__d = {'cmd': args, 'started': str(timestamp.now())}
        else:
            self.__d = json.loads(args)

    def __str__(self):
        return json.dumps(self.__d, separators=(',', ':'))

    @classmethod
    def fromstring(cls, s):
        return cls(s)

    @property
    def cmd(self):
        return self.__d['cmd']

    @property
    def started(self):
        return timestamp.fromstring(self.__d['started'])

    @property
    def size(self):
        return self.__d['size']

    @size.setter
    def size(self, val):
        self.__d['size'] = val


class ExecutionManager(object):
    __slots__ = ['__f', '__c', '__pending', '__fn']

    def __init__(self, location):
        self.__fn = os.path.join(location, 'sciunit.db')
        
        # check if db already exists
        new_db = not os.path.exists(self.__fn)

        self.__f = sqlite3.connect(self.__fn)
        self.__c = self.__f.cursor()

        # if the db is new, we need to init the schema for the db
        if new_db:
            self.__f.executescript("""
            create table revs (
                id      integer primary key autoincrement not null,
                data    text not null
            );
            """)

            self.__f.commit()

    def close(self):
        self.__f.close()

    def exclusive(self):
        #fcntl.flock(self.__f.db.fd(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return closing(self)

    def shared(self):
        #fcntl.flock(self.__f.db.fd(), fcntl.LOCK_SH | fcntl.LOCK_NB)
        return closing(self)

    def add(self, args):
        script = "select max(id) from revs"
        last_id = 1
        try:
            last_row_id = self.__c.execute(script).fetchone()[0]

            if last_row_id != None:
                last_id = last_row_id + 1    

        except Error as e:
            print(e)
        
        self.__pending = (last_id, Metadata(args))
        return self.__to_rev(last_id)

    def commit(self, size):
        k, v = self.__pending
        v.size = size
        
        script = """
            insert into revs (data)
            values (
                '""" + str(v) + """'

                );
                """ 

        self.__c.executescript(script)
        self.__f.commit()

        return (self.__to_rev(k), v)

    def get_last_id(self):
        script = "select max(id) from revs"
        last_row_id = self.__c.execute(script).fetchone()[0]

        if last_row_id != None:
            return last_row_id
        else:
            return 1

    def get(self, rev):
        return Metadata.fromstring(self.__get(self.__to_id(rev)))

    def __get(self, i):
        script = "select * from revs where id = " + str(i)

        row = self.__c.execute(script).fetchone()

        if row != None:
            return row[1]
        else:
            raise CommandError('execution %r not found' % self.__to_rev(i))

    def last(self):
        last_id = self.get_last_id()
        last_data = self.__get(last_id)

        return (self.__to_rev(last_id), Metadata.fromstring(last_data))

    def delete(self, rev):
        script = "delete from revs where id = " + str(self.__to_id(rev))

        # delete record
        self.__c.execute(script)
        self.__f.commit()
        
    def delete_id(self, id):
        script = "delete from revs where id = " + str(id)

        # delete record
        self.__c.execute(script)
        self.__f.commit()

    def deletemany(self, revrange):     
        bounds = self.__to_id_range(revrange)

        for ida in bounds:
            self.delete_id(ida)
        
        for idb in range(bounds[0], bounds[1]):
            self.delete_id(idb)
            

    def sort(self, revls):
        print(revls)
        # todo
        pass

    def __for_upto(self, last, f):
        # todo
        pass

    def __for_from(self, first, f):
        # todo
        pass

    @staticmethod
    def __to_rev(id_):
        return 'e%d' % id_

    @staticmethod
    def __to_id(rev):
        if not re.match(r'^e[1-9]\d*$', rev):
            raise MalformedExecutionId
        return int(rev[1:])

    @staticmethod
    def __to_id_range(revrange):
        r = re.match(r'^e([1-9]\d*)-([1-9]\d*)?$', revrange)
        if not r:
            raise MalformedExecutionId
        return tuple(int(x) if x is not None else x for x in r.groups())

    def list(self):
        #fetch all the executions
        script = "select * from revs"

        rows = self.__c.execute(script).fetchall()

        for row in rows:
            yield self.__to_rev(row[0]), Metadata(row[1])