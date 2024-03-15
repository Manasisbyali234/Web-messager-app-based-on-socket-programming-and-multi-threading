import sqlite3

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

# cursor.execute('''
#       CREATE TABLE users (
#           id INTEGER PRIMARY KEY AUTOINCREMENT,
#           email TEXT,
#           password TEXT,
#           role TEXT
#       )
#   ''')

# # conn.commit()
#
# cursor.execute('''
#           CREATE TABLE IF NOT EXISTS message (
#               id INTEGER PRIMARY KEY AUTOINCREMENT,
#               message TEXT NOT NULL
#           )
#           ''')
# # cursor.execute('DROP TABLE messages')
# cursor.execute('ALTER TABLE message')
# conn.commit()

#
cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_response TEXT
        )
    ''')
conn.commit()


# create_table()


