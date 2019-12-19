import pandas as pd
from dask import dataframe as dd

import featuretools as ft
from featuretools.entityset import EntitySet, Relationship


def test_hackathon():
    df = pd.read_csv('./featuretools/tests/entityset_tests/hackathon_users_data.csv')
    es = EntitySet(id='es')
    es.entity_from_dataframe(
        entity_id="users",
        dataframe=df,
        index="RESPID",
    )

    primitives_list = ['cum_sum', 'diff', 'absolute', 'is_weekend', 'year', 'day', 'num_characters', 'num_words']
    primitives_list = ['absolute', 'is_weekend', 'year', 'day', 'num_characters', 'num_words']

    fm, _ = ft.dfs(entityset=es,
                   target_entity="users",
                   trans_primitives=primitives_list)

    df_dd = dd.from_pandas(df, npartitions=4)
    dask_es = EntitySet(id="dask_es")
    dask_es.entity_from_dataframe(
        entity_id="users",
        dataframe=df_dd,
        index="RESPID",
    )

    dask_fm, _ = ft.dfs(entityset=dask_es,
                        target_entity="users",
                        trans_primitives=primitives_list)

    assert es == dask_es
    # Account for difference in index and column ordering when making comarisons
    assert es['users'].df.reset_index(drop=True).equals(dask_es['users'].df.compute())
    # Use the same columns and make sure both are sorted on index values
    assert fm.sort_index().equals(dask_fm.set_index('RESPID')[fm.columns].compute())


def test_create_entity_from_dask_df(es):
    log_dask = dd.from_pandas(es["log"].df, npartitions=2)
    es = es.entity_from_dataframe(
        entity_id="log_dask",
        dataframe=log_dask,
        index="id",
        time_index="datetime",
        variable_types=es["log"].variable_types
    )
    assert es["log"].df.equals(es["log_dask"].df.compute())


def test_single_table_dask_entityset():
    primitives_list = ['cum_sum', 'diff', 'absolute', 'is_weekend', 'year', 'day', 'num_characters', 'num_words']

    dask_es = EntitySet(id="dask_es")
    df = pd.DataFrame({"id": [0, 1, 2, 3],
                       "values": [1, 12, -34, 27],
                       "dates": [pd.to_datetime('2019-01-10'),
                                 pd.to_datetime('2019-02-03'),
                                 pd.to_datetime('2019-01-01'),
                                 pd.to_datetime('2017-08-25')],
                       "strings": ["I am a string",
                                   "23",
                                   "abcdef ghijk",
                                   ""]})
    values_dd = dd.from_pandas(df, npartitions=2)
    dask_es.entity_from_dataframe(entity_id="data",
                                  dataframe=values_dd,
                                  index="id",
                                  variable_types={"strings": ft.variable_types.Text})

    dask_fm, _ = ft.dfs(entityset=dask_es,
                        target_entity="data",
                        trans_primitives=primitives_list)

    es = ft.EntitySet(id="es")
    es.entity_from_dataframe(entity_id="data",
                             dataframe=df,
                             index="id",
                             variable_types={"strings": ft.variable_types.Text})

    fm, _ = ft.dfs(entityset=es,
                   target_entity="data",
                   trans_primitives=primitives_list)

    # Use the same columns and make sure both are sorted on index values
    assert fm.sort_index().equals(dask_fm.set_index('id')[fm.columns].compute())


def test_single_table_dask_entityset_ids_not_sorted():
    primitives_list = ['cum_sum', 'diff', 'absolute', 'is_weekend', 'year', 'day', 'num_characters', 'num_words']

    dask_es = EntitySet(id="dask_es")
    df = pd.DataFrame({"id": [2, 0, 1, 3],
                       "values": [1, 12, -34, 27],
                       "dates": [pd.to_datetime('2019-01-10'),
                                 pd.to_datetime('2019-02-03'),
                                 pd.to_datetime('2019-01-01'),
                                 pd.to_datetime('2017-08-25')],
                       "strings": ["I am a string",
                                   "23",
                                   "abcdef ghijk",
                                   ""]})
    values_dd = dd.from_pandas(df, npartitions=2)
    dask_es.entity_from_dataframe(entity_id="data",
                                  dataframe=values_dd,
                                  index="id",
                                  variable_types={"strings": ft.variable_types.Text})

    dask_fm, _ = ft.dfs(entityset=dask_es,
                        target_entity="data",
                        trans_primitives=primitives_list)

    es = ft.EntitySet(id="es")
    es.entity_from_dataframe(entity_id="data",
                             dataframe=df,
                             index="id",
                             variable_types={"strings": ft.variable_types.Text})

    fm, _ = ft.dfs(entityset=es,
                   target_entity="data",
                   trans_primitives=primitives_list)

    # Use the same columns and make sure both are sorted on index values
    assert fm.sort_index().equals(dask_fm.set_index('id')[fm.columns].compute())


def test_single_table_dask_entityset_with_instance_ids():
    primitives_list = ['cum_sum', 'diff', 'absolute', 'is_weekend', 'year', 'day', 'num_characters', 'num_words']
    instance_ids = [0, 1, 3]

    dask_es = EntitySet(id="dask_es")
    df = pd.DataFrame({"id": [0, 1, 2, 3],
                       "values": [1, 12, -34, 27],
                       "dates": [pd.to_datetime('2019-01-10'),
                                 pd.to_datetime('2019-02-03'),
                                 pd.to_datetime('2019-01-01'),
                                 pd.to_datetime('2017-08-25')],
                       "strings": ["I am a string",
                                   "23",
                                   "abcdef ghijk",
                                   ""]})

    values_dd = dd.from_pandas(df, npartitions=2)
    dask_es.entity_from_dataframe(entity_id="data",
                                  dataframe=values_dd,
                                  index="id",
                                  variable_types={"strings": ft.variable_types.Text})

    dask_fm, _ = ft.dfs(entityset=dask_es,
                        target_entity="data",
                        trans_primitives=primitives_list,
                        instance_ids=instance_ids)

    es = ft.EntitySet(id="es")
    es.entity_from_dataframe(entity_id="data",
                             dataframe=df,
                             index="id",
                             variable_types={"strings": ft.variable_types.Text})

    fm, _ = ft.dfs(entityset=es,
                   target_entity="data",
                   trans_primitives=primitives_list,
                   instance_ids=instance_ids)

    # Use the same columns and make sure both are sorted on index values
    assert fm.sort_index().equals(dask_fm.set_index('id')[fm.columns].compute())


def test_single_table_dask_entityset_single_cutoff_time():
    primitives_list = ['cum_sum', 'diff', 'absolute', 'is_weekend', 'year', 'day', 'num_characters', 'num_words']

    dask_es = EntitySet(id="dask_es")
    df = pd.DataFrame({"id": [0, 1, 2, 3],
                       "values": [1, 12, -34, 27],
                       "dates": [pd.to_datetime('2019-01-10'),
                                 pd.to_datetime('2019-02-03'),
                                 pd.to_datetime('2019-01-01'),
                                 pd.to_datetime('2017-08-25')],
                       "strings": ["I am a string",
                                   "23",
                                   "abcdef ghijk",
                                   ""]})
    values_dd = dd.from_pandas(df, npartitions=2)
    dask_es.entity_from_dataframe(entity_id="data",
                                  dataframe=values_dd,
                                  index="id",
                                  variable_types={"strings": ft.variable_types.Text})

    dask_fm, _ = ft.dfs(entityset=dask_es,
                        target_entity="data",
                        trans_primitives=primitives_list,
                        cutoff_time=pd.Timestamp("2019-01-05 04:00"))

    es = ft.EntitySet(id="es")
    es.entity_from_dataframe(entity_id="data",
                             dataframe=df,
                             index="id",
                             variable_types={"strings": ft.variable_types.Text})

    fm, _ = ft.dfs(entityset=es,
                   target_entity="data",
                   trans_primitives=primitives_list,
                   cutoff_time=pd.Timestamp("2019-01-05 04:00"))

    # Use the same columns and make sure both are sorted on index values
    assert fm.sort_index().equals(dask_fm.set_index('id')[fm.columns].compute())


def test_single_table_dask_entityset_cutoff_time_df():
    primitives_list = ['cum_sum', 'diff', 'absolute', 'is_weekend', 'year', 'day', 'num_characters', 'num_words']

    dask_es = EntitySet(id="dask_es")
    df = pd.DataFrame({"id": [0, 1, 2],
                       "values": [1, 12, -34],
                       "dates": [pd.to_datetime('2019-01-10'),
                                 pd.to_datetime('2019-02-03'),
                                 pd.to_datetime('2019-01-01')],
                       "strings": ["I am a string",
                                   "23",
                                   "abcdef ghijk"]})
    values_dd = dd.from_pandas(df, npartitions=2)
    dask_es.entity_from_dataframe(entity_id="data",
                                  dataframe=values_dd,
                                  index="id",
                                  variable_types={"strings": ft.variable_types.Text})
    ids = [0, 1, 2, 0]
    times = [pd.Timestamp("2019-01-05 04:00"),
             pd.Timestamp("2019-01-05 04:00"),
             pd.Timestamp("2019-01-05 04:00"),
             pd.Timestamp("2019-01-15 04:00")]
    labels = [True, False, True, False]
    cutoff_times = pd.DataFrame({"id": ids, "time": times, "labels": labels})
    cutoff_times_dask = dd.from_pandas(cutoff_times, npartitions=values_dd.npartitions)

    dask_fm, _ = ft.dfs(entityset=dask_es,
                        target_entity="data",
                        trans_primitives=primitives_list,
                        cutoff_time=cutoff_times_dask)

    es = ft.EntitySet(id="es")
    es.entity_from_dataframe(entity_id="data",
                             dataframe=df,
                             index="id",
                             variable_types={"strings": ft.variable_types.Text})

    fm, _ = ft.dfs(entityset=es,
                   target_entity="data",
                   trans_primitives=primitives_list,
                   cutoff_time=cutoff_times)

    # Use the same columns and make sure both are sorted on index values
    assert fm.sort_index().equals(dask_fm.set_index('id')[fm.columns].compute())


def test_single_table_dask_entityset_dates_not_sorted():
    dask_es = EntitySet(id="dask_es")
    df = pd.DataFrame({"id": [0, 1, 2, 3],
                       "values": [1, 12, -34, 27],
                       "dates": [pd.to_datetime('2019-01-10'),
                                 pd.to_datetime('2019-02-03'),
                                 pd.to_datetime('2019-01-01'),
                                 pd.to_datetime('2017-08-25')]})

    primitives_list = ['cum_sum', 'diff', 'absolute', 'is_weekend', 'year', 'day']
    values_dd = dd.from_pandas(df, npartitions=1)
    dask_es.entity_from_dataframe(entity_id="data",
                                  dataframe=values_dd,
                                  index="id",
                                  time_index="dates")

    dask_fm, _ = ft.dfs(entityset=dask_es,
                        target_entity="data",
                        trans_primitives=primitives_list,
                        max_depth=1)

    es = ft.EntitySet(id="es")
    es.entity_from_dataframe(entity_id="data",
                             dataframe=df,
                             index="id",
                             time_index="dates")

    fm, _ = ft.dfs(entityset=es,
                   target_entity="data",
                   trans_primitives=primitives_list,
                   max_depth=1)

    # Use the same columns and make sure both are sorted on index values
    assert fm.sort_index().equals(dask_fm.set_index('id')[fm.columns].compute())


def test_build_es_from_scratch_and_run_dfs():
    es = ft.demo.load_mock_customer(return_entityset=True)
    data = ft.demo.load_mock_customer()

    transactions_df = data["transactions"].merge(data["sessions"]).merge(data["customers"])
    transactions_dd = dd.from_pandas(transactions_df, npartitions=4)
    products_dd = dd.from_pandas(data["products"], npartitions=4)
    dask_es = EntitySet(id="transactions")
    dask_es.entity_from_dataframe(entity_id="transactions",
                                  dataframe=transactions_dd,
                                  index="transaction_id",
                                  time_index="transaction_time",
                                  variable_types={"product_id": ft.variable_types.Categorical,
                                                  "zip_code": ft.variable_types.ZIPCode,
                                                  "device": ft.variable_types.Categorical})
    dask_es.entity_from_dataframe(entity_id="products",
                                  dataframe=products_dd,
                                  index="product_id",
                                  variable_types={"brand": ft.variable_types.Categorical})

    new_rel = Relationship(dask_es["products"]["product_id"],
                           dask_es["transactions"]["product_id"])

    dask_es = dask_es.add_relationship(new_rel)

    dask_es = dask_es.normalize_entity(base_entity_id="transactions",
                                       new_entity_id="sessions",
                                       index="session_id",
                                       make_time_index="session_start",
                                       additional_variables=["device",
                                                             "customer_id",
                                                             "zip_code",
                                                             "session_start",
                                                             "join_date",
                                                             "date_of_birth"])

    dask_es = dask_es.normalize_entity(base_entity_id="sessions",
                                       new_entity_id="customers",
                                       index="customer_id",
                                       make_time_index="join_date",
                                       additional_variables=["zip_code", "join_date", "date_of_birth"])

    primitives_list = ['cum_sum', 'diff', 'absolute', 'is_weekend', 'year', 'day', 'num_characters', 'num_words']

    fm, _ = ft.dfs(entityset=es,
                   target_entity="customers",
                   trans_primitives=primitives_list,
                   agg_primitives=[],
                   max_depth=2)

    dask_fm, _ = ft.dfs(entityset=dask_es,
                        target_entity="customers",
                        trans_primitives=primitives_list,
                        agg_primitives=[],
                        max_depth=2)

    # Use the same columns and make sure both are sorted on index values
    assert fm.sort_index().equals(dask_fm.set_index('customer_id')[fm.columns].compute())
