import asyncio
import sqlite3
mutex_for_store = asyncio.Lock()


async def select_from_db(sql):
    connect = sqlite3.connect('./erpdata.db')  # Connect to the SQLite database file 'erp.db'
    cursor = connect.cursor()  # Use cursor() to get a cursor
    cursor.execute(sql)  # Execute the SQL statement
    results = cursor.fetchall()  # Get all results

    connect.commit()
    cursor.close()
    connect.close()
    return results


async def exec_sql(sql):
    connect = sqlite3.connect('./erpdata.db')  # Connect to the SQLite database file 'erp.db'
    cursor = connect.cursor()  # Use cursor() to get a cursor
    cursor.execute(sql)  # Execute the SQL statement

    connect.commit()
    cursor.close()
    connect.close()
    return


async def get_supply_available():
    supply_available = []
    sql_res = await select_from_db("""select DISTINCT inventory."父物料名称" from inventory""")
    for item in sql_res:
        if item[0] != "" and item[0] is not None:
            supply_available.append(item)
    return supply_available


async def get_store_available():
    return await select_from_db("""select * from store""")
