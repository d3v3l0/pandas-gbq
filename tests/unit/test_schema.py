import datetime

import pandas
import pytest


@pytest.fixture
def module_under_test():
    import pandas_gbq.schema

    return pandas_gbq.schema


def test_schema_is_subset_passes_if_subset(module_under_test):
    # Issue #24 schema_is_subset indicates whether the schema of the
    # dataframe is a subset of the schema of the bigquery table
    table_schema = {
        "fields": [
            {"name": "A", "type": "FLOAT"},
            {"name": "B", "type": "FLOAT"},
            {"name": "C", "type": "STRING"},
        ]
    }
    tested_schema = {
        "fields": [
            {"name": "A", "type": "FLOAT"},
            {"name": "B", "type": "FLOAT"},
        ]
    }
    assert module_under_test.schema_is_subset(table_schema, tested_schema)


def test_schema_is_subset_fails_if_not_subset(module_under_test):
    table_schema = {
        "fields": [
            {"name": "A", "type": "FLOAT"},
            {"name": "B", "type": "FLOAT"},
            {"name": "C", "type": "STRING"},
        ]
    }
    tested_schema = {
        "fields": [
            {"name": "A", "type": "FLOAT"},
            {"name": "C", "type": "FLOAT"},
        ]
    }
    assert not module_under_test.schema_is_subset(table_schema, tested_schema)


@pytest.mark.parametrize(
    "dataframe,expected_schema",
    [
        (
            pandas.DataFrame(data={"col1": [1, 2, 3]}),
            {"fields": [{"name": "col1", "type": "INTEGER"}]},
        ),
        (
            pandas.DataFrame(data={"col1": [True, False]}),
            {"fields": [{"name": "col1", "type": "BOOLEAN"}]},
        ),
        (
            pandas.DataFrame(data={"col1": [1.0, 3.14]}),
            {"fields": [{"name": "col1", "type": "FLOAT"}]},
        ),
        (
            pandas.DataFrame(data={"col1": [u"hello", u"world"]}),
            {"fields": [{"name": "col1", "type": "STRING"}]},
        ),
        (
            pandas.DataFrame(data={"col1": [datetime.datetime.now()]}),
            {"fields": [{"name": "col1", "type": "TIMESTAMP"}]},
        ),
        (
            pandas.DataFrame(
                data={
                    "col1": [datetime.datetime.now()],
                    "col2": [u"hello"],
                    "col3": [3.14],
                    "col4": [True],
                    "col5": [4],
                }
            ),
            {
                "fields": [
                    {"name": "col1", "type": "TIMESTAMP"},
                    {"name": "col2", "type": "STRING"},
                    {"name": "col3", "type": "FLOAT"},
                    {"name": "col4", "type": "BOOLEAN"},
                    {"name": "col5", "type": "INTEGER"},
                ]
            },
        ),
    ],
)
def test_generate_bq_schema(module_under_test, dataframe, expected_schema):
    schema = module_under_test.generate_bq_schema(dataframe)
    assert schema == expected_schema


@pytest.mark.parametrize(
    "schema_old,schema_new,expected_output",
    [
        (
            {"fields": [{"name": "col1", "type": "INTEGER"}]},
            {"fields": [{"name": "col2", "type": "TIMESTAMP"}]},
            # Ignore fields that aren't in the DataFrame.
            {"fields": [{"name": "col1", "type": "INTEGER"}]},
        ),
        (
            {"fields": [{"name": "col1", "type": "INTEGER"}]},
            {"fields": [{"name": "col1", "type": "BOOLEAN"}]},
            # Update type for fields that are in the DataFrame.
            {"fields": [{"name": "col1", "type": "BOOLEAN"}]},
        ),
        (
            {
                "fields": [
                    {"name": "col1", "type": "INTEGER"},
                    {"name": "col2", "type": "INTEGER"},
                ]
            },
            {
                "fields": [
                    {"name": "col2", "type": "BOOLEAN"},
                    {"name": "col3", "type": "FLOAT"},
                ]
            },
            {
                "fields": [
                    {"name": "col1", "type": "INTEGER"},
                    {"name": "col2", "type": "BOOLEAN"},
                ]
            },
        ),
    ],
)
def test_update_schema(
    module_under_test, schema_old, schema_new, expected_output
):
    output = module_under_test.update_schema(schema_old, schema_new)
    assert output == expected_output
