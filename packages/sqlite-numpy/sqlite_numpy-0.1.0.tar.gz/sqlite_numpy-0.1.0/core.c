#include <assert.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef C_ONLY
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#endif
#include <sqlite3.h>

#include "core.h"

void finalize(Query *query, int keep_statement)
{
    free(query->column_types);
    query->column_types = NULL;
    free(query->column_names);
    query->column_names = NULL;
    if (query->statement != NULL)
    {
        if (!keep_statement)
        {
            sqlite3_finalize(query->statement);
            query->statement = NULL;
        }
        else
            sqlite3_reset(query->statement);
    }
}

int prepare(sqlite3 *db, Query *query, const char *sql)
{
    query->statement = NULL;
    query->column_count = 0;
    query->column_types = NULL;
    query->column_names = NULL;

    if (sqlite3_prepare_v2(db, sql, -1, &query->statement, NULL) != SQLITE_OK)
    {
        finalize(query, 0);
        return PREPARE_ERROR;
    }
    return OK;
}

int execute(sqlite3 *db, Query *query)
{
    assert(query->statement != NULL);
    if (SQLITE_ROW != sqlite3_step(query->statement))
    {
        finalize(query, 0);
        return NO_ROW;
    }
    query->column_count = sqlite3_column_count(query->statement);
    query->column_types = (char *)malloc(query->column_count);
    query->column_names = (const char **)malloc(query->column_count * sizeof(const char *));
    for (int i = 0; i < query->column_count; ++i)
    {
        query->column_types[i] = sqlite3_column_type(query->statement, i);
        query->column_names[i] = sqlite3_column_name(query->statement, i);
    }
    return OK;
}

int read_chunk(Query *query, void **results, int offset, int row_count)
{
    void *column;
    int row = 0;
    int last_step_result = SQLITE_ROW;
    int i;
    sqlite3_value *value;
    int value_type;
    while (row < row_count && SQLITE_ROW == last_step_result)
    {
        for (i = 0; i < query->column_count; ++i)
        {
            column = results[i];
            value = sqlite3_column_value(query->statement, i);
            value_type = sqlite3_value_type(value);
            switch (query->column_types[i])
            {
            case SQLITE_FLOAT:
                ((double *)(column))[offset + row] = (SQLITE_NULL == value_type ? NAN : sqlite3_value_double(value));
                break;
            case SQLITE_INTEGER:
                if (SQLITE_NULL == value_type)
                    return NULL_IN_INT_COLUMN;
                ((sqlite3_int64 *)(column))[offset + row] = sqlite3_value_int64(value);
                break;
            case SQLITE_NULL:
                if (SQLITE_INTEGER == value_type)
                    return NULL_IN_INT_COLUMN;
                query->column_types[i] = value_type;
                ((double *)(column))[offset + row] = (SQLITE_NULL == value_type ? NAN : sqlite3_value_double(value));
            }
        }
        ++row;
        last_step_result = sqlite3_step(query->statement);
    };
    return row;
}

inline int get_value_size(int column_type)
{
    int value_size = -1;
    switch (column_type)
    {
    case SQLITE_FLOAT:
    case SQLITE_NULL:
        value_size = sizeof(double);
        break;
    case SQLITE_INTEGER:
        value_size = sizeof(sqlite3_int64);
        break;
    }
    assert(value_size > 0);
    return value_size;
}

void **alloc_results(Query *query, void **results, int count)
{
    if (NULL == results)
    {
        results = (void **)malloc(query->column_count * sizeof(void *));
        memset(results, 0, query->column_count * sizeof(void *));
    }
    int value_size;
    for (int i = 0; i < query->column_count; ++i)
    {
        value_size = get_value_size(query->column_types[i]);
        if (value_size < 0)
        {
            for (int j = 0; j < i; ++j)
                PyDataMem_FREE(results[j]);
            free(results);
            return NULL;
        }
        results[i] = PyDataMem_RENEW(results[i], value_size * count);
    }
    return results;
}

void free_results(Query *query, void **results)
{
    for (int i = 0; i < query->column_count; ++i)
    {
        PyDataMem_FREE(results[i]);
        results[i] = NULL;
    }
}

#ifndef C_ONLY
void initialize()
{
    import_array();
}

PyObject *create_numpy_array(void *data, int rows, int column_type)
{
    const npy_intp dims = rows;
    int npy_type = -1;
    switch (column_type)
    {
    case SQLITE_FLOAT:
        npy_type = NPY_DOUBLE;
        break;
    case SQLITE_INTEGER:
        npy_type = NPY_INT64;
        break;
    }
    PyArrayObject *array = (PyArrayObject *)PyArray_SimpleNewFromData(1, &dims, npy_type, data);
    assert(array != NULL);
    PyArray_ENABLEFLAGS(array, NPY_ARRAY_OWNDATA);
    return (PyObject *)array;
}
#endif