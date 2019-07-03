import cv2
import numpy as np
from PIL import Image, ImageTk

import time

class Camera():
  def __init__(self, device=0, resize=(640, 360)):
    print('[*] Trying to find camera device...')
    self.cap = cv2.VideoCapture(device)
    self.resize = resize

    time.sleep(2)

    if not self.cap.isOpened():
      print('[!] Camera is not connected!')
      exit()

    ret, img = self.cap.read()
    h, w, _ = img.shape

    self.cam_size = (w, h)

  def thread(self, app):
    while self.cap.isOpened():
      ret, img = self.cap.read()

      if not ret:
        print('[!] Cannot receive frame data from camera')
        break

      img = cv2.resize(img, self.resize)
      img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

      img_tk = ImageTk.PhotoImage(Image.fromarray(img, 'RGB'))

      # app.queueFunction(app.setImageData, 'pic', img_tk, fmt='PhotoImage') # slow
      app.setImageData('pic', img_tk, fmt='PhotoImage')

    print('[!] Disconnected to camera')
    return False