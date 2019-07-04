import cv2

from .config import *

import datetime, json

class User():
  def __init__(self):
    self.id = None
    self.name = None
    self.gender = None
    self.age = None
    self.tastes = USER_TASTES
    self.emb = None

  def create(self, conn, name, gender, age, tastes, emb, img):
    c = conn.cursor()

    c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)', (
      None, datetime.datetime.now(), name, gender, age, json.dumps(tastes), emb
    ))

    conn.commit()

    self.name = name
    self.gender = gender
    self.age = age
    self.tastes = tastes
    self.emb = emb
    self.id = c.lastrowid

    cv2.imwrite('db/face_imgs/%d.jpg' % (self.id,), img)
