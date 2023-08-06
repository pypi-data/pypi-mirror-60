# cython: language_level=3

import functools
from libc.stdlib cimport free
import time
import warnings

cimport interface

interface.initialize()


class Error(Exception):
    pass


class UnsupportedError(Error):
    pass


cdef exception_from_error_code(int error_code):
    if interface.INCONSISTENT_COLUMN_TYPE==error_code:
        return UnsupportedError("Column values have several types")
    elif interface.NULL_IN_INT_COLUMN==error_code:
        return UnsupportedError("NULL value in int column")

cdef class Results:
    cdef void** data
    cdef int size

    @staticmethod
    cdef Results create():
        cdef Results results = Results.__new__(Results)
        return results

    def __cinit__(self):
        self.data = NULL
        self.size = 0

    def free(self):
        free(self.data)
        self.data = NULL
        self.size = 0


cdef class ResultProxy:
    cdef interface.Query _query

    @staticmethod
    cdef ResultProxy execute(str sql, interface.sqlite3* db):
        # Call to __new__ bypasses __init__ constructor
        cdef ResultProxy proxy = ResultProxy.__new__(ResultProxy)
        cdef int ret
        ret = interface.prepare(db, &proxy._query, sql.encode())
        if ret!=interface.OK:
            raise Error(f"Error while preparing query {sql}")
        with nogil:
            ret = interface.execute(db, &proxy._query)!=interface.OK
        if ret!=interface.OK:
            raise Error(f"Error while executing query {sql}")
        return proxy

    def __del__(self):
        self.close()

    def fetchall(self):
        cdef dict arrays = {}
        cdef int read_size
        cdef int size_increment = 100
        cdef int i
        cdef Results results = Results.create()
        if not self._query.statement:
            raise Error(f"Proxy already closed")

        try:
            read_size = self.alloc_and_read(results, size_increment)
            while read_size==size_increment:
                # exponential allocation strategy to amortize the reallocation
                size_increment = int(0.5*results.size)
                read_size = self.alloc_and_read(results, size_increment)
            # free unused memory at the end of results due to exponential memory
            # allocation strategy
            results.data = interface.alloc_results(
                &self._query,
                results.data,
                results.size
            )
            for i in range(self._query.column_count):
                column_name = self._query.column_names[i].decode()
                arrays[column_name] = interface.create_numpy_array(
                    results.data[i],
                    results.size,
                    self._query.column_types[i]
                )
        finally:
            results.free()
            self.close()
        return arrays

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def fetchmany(self, int count):
        cdef Results results = Results.create()
        cdef dict arrays = {}
        cdef int i
        if not self._query.statement:
            raise Error(f"Proxy already closed")
        try:
            self.alloc_and_read(results, count)
            # free potential unused memory at the end of results
            results.data = interface.alloc_results(
                &self._query,
                results.data,
                results.size
            )
            for i in range(self._query.column_count):
                column_name = self._query.column_names[i].decode()
                arrays[column_name] = interface.create_numpy_array(
                    results.data[i],
                    results.size,
                    self._query.column_types[i]
                )
        finally:
            results.free()
            if results.size<count:
                self.close()
        return arrays

    @property
    def closed(self) -> bool:
        return self._query.column_names==NULL

    def close(self):
        interface.finalize(&self._query, 0)

    cdef inline int alloc_and_read(self, Results results, int size_increment) except -1:
        cdef int read_size
        with nogil:
            results.data = interface.alloc_results(
                &self._query,
                results.data,
                results.size + size_increment
            )
        if results.data==NULL:
            raise UnsupportedError("Unknown value type in query")
        with nogil:
            read_size = interface.read_chunk(
                &self._query,
                results.data,
                results.size,
                size_increment
            )
        if read_size<0:
            interface.free_results(&self._query, results.data)
            raise exception_from_error_code(read_size)
        results.size += read_size
        return read_size


cdef class Database:
    cdef interface.sqlite3 *_db

    if interface.SQLITE_MISUSE==interface.sqlite3_config(
        interface.SQLITE_CONFIG_MULTITHREAD
    ):
        warnings.warn("Couldn't setup sqlite to multi-threaded mode")

    def __cinit__(self, path):
        if interface.sqlite3_open(path.encode(), &self._db)!=interface.SQLITE_OK:
            raise Error(f"Error opening database file {path}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @property
    def closed(self) -> bool:
        return self._db == NULL

    def close(self) -> None:
        interface.sqlite3_close(self._db)
        self._db = NULL

    def execute(self, sql_statement):
        assert not self.closed, "Cannot execute, database has been closed"
        return ResultProxy.execute(sql_statement, self._db)

    def load_extension(self, name):
        interface.sqlite3_load_extension(self._db, name.encode(), NULL, NULL)
