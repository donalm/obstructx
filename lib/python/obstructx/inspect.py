#!/usr/bin/env python

queries={}

queries["list_databases"] = """
SELECT
    datname
FROM
    pg_database
WHERE
    datistemplate = false"""

queries["list_tables"] = """
SELECT
    table_name
FROM
    information_schema.tables
WHERE
    table_schema='public'
AND
    table_type='BASE TABLE'
order by
    table_name
"""


queries["list_foreign_keys"] = """
SELECT "table",
       array_agg(columns) AS columns,
       "foreign table",
       array_agg("foreign columns") AS "foreign columns"
  FROM ( SELECT conrelid::regclass AS "table",
                a.attname as columns,
                confrelid::regclass as "foreign table",
                af.attname as "foreign columns"
           FROM pg_attribute AS af,
                pg_attribute AS a,
                ( SELECT conrelid,
                         confrelid,
                         conkey[i] AS conkey,
                         confkey[i] as confkey
                    FROM ( SELECT conrelid,
                                  confrelid,
                                  conkey,
                                  confkey,
                                  generate_series(1, array_upper(conkey, 1)) AS i
                             FROM pg_constraint
              WHERE contype = 'f'
                  ) AS ss
                ) AS ss2
          WHERE af.attnum = confkey
            AND af.attrelid = confrelid
            AND a.attnum = conkey
            AND a.attrelid = conrelid
       ) AS ss3
  GROUP BY "table",
           "foreign table"
"""
queries["list_table_fields"] = """
SELECT
    table_name,
    column_name,
    column_default,
    character_maximum_length,
    numeric_precision,
    numeric_precision_radix,
    numeric_scale,
    data_type,
    is_nullable
FROM
    information_schema.columns
WHERE
    table_name = '%s';
"""

queries["list_table_indexes"] = """
select
    t.relname as table_name,
    i.relname as index_name,
    ix.indisunique as unique,
    array_agg(a.attname) as column_names
from
    pg_class t,
    pg_class i,
    pg_index ix,
    pg_attribute a
where
    t.oid = ix.indrelid
    and i.oid = ix.indexrelid
    and a.attrelid = t.oid
    and a.attnum = ANY(ix.indkey)
    and t.relkind = 'r'
    and t.relname = '%s'
group by
    t.relname,
    i.relname,
    ix.indisunique
order by
    t.relname,
    i.relname;
"""

if __name__ == '__main__':
    import json
    fh = open("./output.json", "w")
    res = json.dump(queries, fh, indent=4)
    fh.close()
