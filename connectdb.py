import sqlite3


async def select_from_db(sql):
    connect = sqlite3.connect('./erpdata.db')  # Connect to the SQLite database file 'erp.db'
    cursor = connect.cursor()  # Use cursor() to get a cursor
    cursor.execute(sql)  # Execute the SQL statement
    results = cursor.fetchall()  # Get all results


    connect.commit()
    cursor.close()
    connect.close()
    return results


def select_from_db_init(sql):
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
