import json


def xgb2sql(xgb_booster, table_name, index_list=[], sql_type=None):
    """
    Takes in an XGB Booster and converts it to a SQL query. 
    Look, I'm not saying you should use this, but I'm saying it now exists.
    I imagine any sort of tree based model could be relatively easily converted to a SQL query using this.
    
    Parameters
    ----------
    xgb_booster: xgboost.core.Booster
        https://xgboost.readthedocs.io/en/latest/tutorials/model.html
    table_name: str
        The name of the SQL table to query from. Obviously this table must be the same as the model inputs or else it won't work.
    index_list : list
        Anything in the list will be passed through as a column in your final output. Everything is converted to string.
        Useful for joining back onto data source.
        Otherwise you're stuck merging on index which is probably okay unless data is being shuffled.
    sql_type : str
        If there's a better way native to the sql_type to generate the code, it will be used. 
        Otherwise defaults to PostgreSQL compliant code. 
    """

    def _psql_eval(index_list, leaf_list):
        leaf_string = "\n\t+ ".join(leaf_list)
        if len(index_list) > 0:
            query = f"""SELECT
            {', '.join(index_list)},       
            1 / ( 1 + EXP ( - (
            {leaf_string}) ) ) AS score
    FROM booster_output"""
        else:
            query = f"""SELECT 
            1 / ( 1 + EXP ( - ( 
            {leaf_string} ) ) ) AS score
    FROM booster_output"""

        return query

    def _bq_eval(index_list):
        def _dumb_func(index_list):
            a = ["'" + i + "'" for i in index_list]
            return ",".join(a)

        if len(index_list) > 0:
            index_string = ", ".join(index_list)
            query = f""",
            
json_collapsed AS (
    SELECT
        {index_string},
        TO_JSON_STRING(booster_output) AS json_text
    FROM booster_output
),

unnested AS (
    SELECT
        {index_string},
        REGEXP_REPLACE(SUBSTR(pairs, 1, STRPOS(pairs, ':') - 1), '^"|"$', '') AS variable_name,
        REGEXP_REPLACE(SUBSTR(pairs, STRPOS(pairs, ':') + 1, LENGTH(pairs)), '^"|"$', '') AS value
    FROM json_collapsed, UNNEST(SPLIT(REGEXP_REPLACE(json_text, '^{{|}}$', ''), ',"')) pairs
)

SELECT
    {index_string},
    1 / ( 1 + EXP ( - SUM ( CAST ( value AS FLOAT64 ) ) ) ) AS score
FROM unnested
WHERE variable_name NOT IN (
    {dumb_func(index_list)}
)
GROUP BY {index_string}
            """

        else:
            query = f""",
    
json_collapsed AS (
    SELECT
        TO_JSON_STRING(branching) AS json_text
    FROM booster_output
),

unnested AS (
    SELECT
        REGEXP_REPLACE(SUBSTR(pairs, 1, STRPOS(pairs, ':') - 1), '^"|"$', '') AS variable_name,
        REGEXP_REPLACE(SUBSTR(pairs, STRPOS(pairs, ':') + 1, LENGTH(pairs)), '^"|"$', '') AS value
    FROM json_collapsed, UNNEST(SPLIT(REGEXP_REPLACE(json_text, '^{{|}}$', ''), ',"')) pairs
)

SELECT
    1 / ( 1 + EXP ( - SUM ( CAST ( value AS FLOAT64 ) ) ) ) AS score
FROM unnested
"""
        return query

    def _extract_values(obj, key):
        """
        Pull all values of specified key from nested JSON.
        I'm pretty sure I can do all of these in one big dict but I'm a coward so
        """
        key_dict = {}
        arr = []
        child_dict = {}
        info_dict = {}

        def _extract(obj, arr, key, prev=None):
            """Recursively search for values of key in JSON tree."""
            if isinstance(obj, dict):
                try:
                    info_dict.update(
                        {
                            obj["nodeid"]: {
                                "split_column": obj["split"],
                                "split_number": obj["split_condition"],
                                "if_less_than": obj["yes"],
                                "if_greater_than": obj["no"],
                                "if_null": obj["missing"],
                            }
                        }
                    )

                except:
                    info_dict.update({obj["nodeid"]: {}})

                child_dict.update({obj["nodeid"]: prev})
                prev = obj["nodeid"]

                for k, v in obj.items():
                    if isinstance(v, (dict, list)):
                        _extract(v, arr, key, prev)
                    elif k == key:
                        key_dict.update({obj["nodeid"]: v})
            elif isinstance(obj, list):
                for item in obj:
                    _extract(item, arr, key, prev)
            return key_dict

        results = _extract(obj, arr, key)
        return results, child_dict, info_dict

    def _recurse_backwards(first_node):
        query_list = []

        def _recurse(x):
            prev_node = x
            next_node = child_dict[prev_node]
            # The 'yes' is always the < one, that is NOT inclusive
            try:
                node = splits[next_node]
                if (node["if_less_than"] == prev_node) & (
                    node["if_less_than"] == node["if_null"]
                ):
                    text = f"(({node['split_column']} < {node['split_number']}) OR ({node['split_column']} IS NULL))"
                    query_list.insert(0, text)
                    _recurse(next_node)
                elif node["if_less_than"] == prev_node:
                    text = f"({node['split_column']} < {node['split_number']})"
                    query_list.insert(0, text)
                    _recurse(next_node)
                elif (node["if_greater_than"] == prev_node) & (
                    node["if_greater_than"] == node["if_null"]
                ):
                    text = f"(({node['split_column']} >= {node['split_number']}) OR ({node['split_column']} IS NULL))"
                    query_list.insert(0, text)
                    _recurse(next_node)
                elif node["if_greater_than"] == prev_node:
                    text = f"({node['split_column']} >= {node['split_number']})"
                    query_list.insert(0, text)
                    _recurse(next_node)
            except:
                pass

        _recurse(first_node)

        s = "\n\t\t\tAND "

        return s.join(query_list)

    ret = xgb_booster.get_dump(dump_format="json")

    json_string = "[\n"
    for i, _ in enumerate(ret):
        json_string = json_string + ret[i]
        if i < len(ret) - 1:
            json_string = json_string + ",\n"
    json_string = json_string + "\n]"

    tree_json = json.loads(json_string)

    index_list = [str(i) for i in index_list]
    index_string = ",\n".join(index_list)

    # Each one is one case when statement
    leaf_list = []
    counter = 0
    for i in range(0, len(tree_json)):
        leaves, child_dict, splits = _extract_values(tree_json[i], "leaf")
        column_list = []
        for base_leaf in leaves:
            leaf_query = (
                "\t\t\tWHEN "
                + _recurse_backwards(base_leaf)
                + f"\n\t\tTHEN {leaves[base_leaf]}"
            )
            column_list.append(leaf_query)
        column_list = (
            "\t\tCASE\n" + ("\n").join(column_list) + f"\n\t\tEND AS column_{counter}"
        )
        leaf_list.append(column_list)
        counter += 1

    if sql_type == "bigquery":
        output = bq_eval(index_list)
    else:
        output = psql_eval(index_list, leaf_list)

    query = (
        "booster_output AS (\n\tSELECT\n"
        + ", \n".join((index_list + leaf_list))
        + f"\n\tFROM {table_name}\n)"
        + f"{output}"
    )

    return query
