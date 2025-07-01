import pyodbc
import pandas as pd
import concurrent.futures
from src.config.db import conn_string
from src.utils.cache import cache


@cache.memoize()
def run_query(item):
    key, query = item
    conn = pyodbc.connect(conn_string)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return key, df

def run_queries(queries, workers = 5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        results = dict(executor.map(run_query, queries.items()))
    response = {}
    for key in queries.keys():
        response[key] = results[key]    
    return response