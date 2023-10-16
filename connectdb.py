import sqlite3


def select_from_db(sql):
    connect = sqlite3.connect('./erpdata.db')  # Connect to the SQLite database file 'erp.db'
    cursor = connect.cursor()  # Use cursor() to get a cursor
    cursor.execute(sql)  # Execute the SQL statement
    results = cursor.fetchall()  # Get all results

    for result in results:
        result = list(result)

    connect.commit()
    cursor.close()
    connect.close()
    return results