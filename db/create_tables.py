import sqlite3, os, datetime, json
import numpy as np

db_list = ['data']

for db_name in db_list:
  if not os.path.exists('./db/%s.db' % (db_name)):
    open('./db/%s.db' % (db_name), 'w').close()

conn = sqlite3.connect('./db/data.db', detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

c.execute('''CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  date TIMESTAMP,
  name TEXT,
  gender INTEGER,
  age INTEGER,
  tastes TEXT,
  emb TEXT
)''')

c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)', (
  None,
  datetime.datetime.now(),
  '이태희',
  0,
  30,
  json.dumps({'abc': True, 'bcd': False}),
  np.ones((1, 512), np.float32)
))

conn.commit()

c.execute('SELECT * FROM users')

users = c.fetchall()

print(users)

print(json.loads(users[0][5]))
