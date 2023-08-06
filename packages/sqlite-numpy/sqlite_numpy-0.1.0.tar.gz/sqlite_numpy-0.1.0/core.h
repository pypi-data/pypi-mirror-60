#ifndef SQLITE_NUMPY_H
#define SQLITE_NUMPY_H 1
#include <sqlite3.h>

typedef enum
{
    OK = 0,
    PREPARE_ERROR = -1,
    NO_ROW = -2,
    NULL_IN_INT_COLUMN = -3,
    INCONSISTENT_COLUMN_TYPE = -4,
} ReturnCode;

typedef struct
{
    int column_count;
    char *column_types;
    const char **column_names;
    sqlite3_stmt *statement;
} Query;

int prepare(sqlite3 *db, Query *query, const char *sql);
int execute(sqlite3 *db, Query *query);
void finalize(Query *query, int keep_statement);
int read_chunk(Query *query, void **results, int offset, int row_count);
void **alloc_results(Query *query, void **results, int count);
void free_results(Query *query, void **results);
#ifndef C_ONLY
void initialize();
PyObject *create_numpy_array(void *results, int rows, int column_type);
#endif
#endif