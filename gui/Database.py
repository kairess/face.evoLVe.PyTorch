import numpy as np
import cv2

import json, sqlite3, datetime

class Database():
  def __init__(self):
    print('[*] Connecting to database...')
    self.conn = sqlite3.connect('./db/data.db')
    self.conn.row_factory = self.dict_factory

  def dict_factory(self, cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
      d[col[0]] = row[idx]
    return d

  def get_users(self):
    c = self.conn.cursor()

    c.execute('SELECT * FROM users')
    users = c.fetchall()

    for i, user in enumerate(users):
      users[i]['tastes'] = json.loads(user['tastes'])
      users[i]['emb'] = np.frombuffer(user['emb'], np.float32)

    return users

  def create_user(self, name, gender, age, tastes, emb, img):
    c = self.conn.cursor()

    c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)', (
      None, datetime.datetime.now(), name, gender, age, json.dumps(tastes), emb
    ))

    self.conn.commit()

    last_id = c.lastrowid

    cv2.imwrite('db/face_imgs/%d.jpg' % (last_id,), img)