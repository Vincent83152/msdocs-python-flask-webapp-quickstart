import sqlite3
conn = sqlite3.connect("restaurant.db")

SQL_DROPTABLE = '''
        DROP TABLE IF EXISTS RESTAURANT
'''

SQL_CREATETABLE = '''
        CREATE TABLE IF NOT EXISTS RESTAURANT(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
'''

conn.execute(SQL_DROPTABLE)
conn.execute(SQL_CREATETABLE)
conn.commit()
conn.close()