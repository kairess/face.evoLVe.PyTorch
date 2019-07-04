import numpy as np
import sqlite3, os, datetime, json

conn = sqlite3.connect('./db/data.db', detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

c.execute('SELECT * FROM users WHERE id = 7')
a = c.fetchone()
a = np.frombuffer(a[-1], np.float32)

c.execute('SELECT * FROM users WHERE id = 8')
b = c.fetchone()
b = np.frombuffer(b[-1], np.float32)

print(np.linalg.norm([a - b]))


