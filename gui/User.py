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
  
