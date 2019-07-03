import numpy as np

class Face():
  def __init__(self, rect, conf):
    self.available = True
    self.init = True
    self.tracked = False
    self.rect = rect
    self.conf = conf

  def compute_face_distance(self, rect):
    return np.linalg.norm(np.array(rect)[:4] - np.array(self.rect)[:4])