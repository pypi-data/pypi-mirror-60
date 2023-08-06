cdef extern from "core.h":
    ctypedef struct Query:
        int column_count
        char *column_types
        const char**column_names
        sqlite3_stmt *statement
    void finalize(Query *query, int keep_statement) nogil
    int execute(sqlite3 *db, Query *query) nogil
    int prepare(sqlite3 *db, Query *query, const char* sql) nogil
    int read_chunk(Query *query, void **results, int offset, int row_count) nogil
    void **alloc_results(Query *query, void **results, int count) nogil
    void free_results(Query *query, void** results)
    object create_numpy_array(void *data, int rows, int column_type)
    void initialize()
    int OK
    int PREPARE_ERROR
    int NO_ROW
    int NULL_IN_INT_COLUMN
    int INCONSISTENT_COLUMN_TYPE

cdef extern from "Python.h":
    ctypedef struct PyObject:
        pass

cdef extern from "sqlite3.h":
    ctypedef struct sqlite3:
        pass
    ctypedef struct sqlite3_stmt:
        pass
    int SQLITE_OK
    int SQLITE_MISUSE
    int SQLITE_CONFIG_MULTITHREAD
    int sqlite3_open(const char *filename, sqlite3 **ppDb)
    int sqlite3_close(sqlite3*)
    int sqlite3_config(int)
    int sqlite3_load_extension(
        sqlite3*db,
        const char *zFile,
        const char *zProc,
        char **pzErrMsg
    )
