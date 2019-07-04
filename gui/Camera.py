import cv2
import numpy as np
from PIL import Image, ImageTk

from Face import Face
from config import *

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
    self.cam_size = (img.shape[1], img.shape[0])

    img = self.center_crop(img)
    self.cam_size_resized = (img.shape[1], img.shape[0])

    print('[*] Load face detection model...')
    self.facenet = cv2.dnn.readNetFromTensorflow(
      'face_models/opencv_face_detector_uint8.pb',
      'face_models/opencv_face_detector.pbtxt'
    )

    self.faces = []

  def center_crop(self, img):
    h, w, _ = img.shape
    img = img[:, int((w-h)/2):int(w-(w-h)/2), :]

    if img.shape[0] != img.shape[1]:
      img = cv2.resize(img, (img.shape[0], img.shape[0]))

    return img

  def thread(self, app):
    while self.cap.isOpened():
      ret, img = self.cap.read()

      if not ret:
        print('[!] Cannot receive frame data from camera')
        break

      img = self.center_crop(img)

      img_vis = img.copy()

      # detect faces
      self.detect_faces(img)

      self.biggest_face_img = None

      # visualize and get biggest face image
      for face in self.faces:
        x1, y1, x2, y2 = face.rect

        if face.biggest:
          self.biggest_face_img = img[y1:y2, x1:x2]

        rect_color = (0, 0, 255)
        if face.biggest:
          rect_color = (0, 255, 0)

        cv2.rectangle(img_vis, pt1=(x1, y1), pt2=(x2, y2), color=rect_color, thickness=2)

      img_vis = cv2.resize(img_vis, self.resize)
      img_vis = cv2.cvtColor(img_vis, cv2.COLOR_BGR2RGB)

      img_tk = ImageTk.PhotoImage(Image.fromarray(img_vis, 'RGB'))
      # app.queueFunction(app.setImageData, 'pic', img_tk, fmt='PhotoImage') # slow
      app.setImageData('cam', img_tk, fmt='PhotoImage')

      # biggest face image is not exist or has 0-length, pass this frame
      if self.biggest_face_img is None or self.biggest_face_img.shape[0] == 0 or self.biggest_face_img.shape[1] == 0:
        continue

      self.biggest_face_img = cv2.resize(self.biggest_face_img, (224, 224))
      img_tk = ImageTk.PhotoImage(Image.fromarray(self.biggest_face_img, 'RGB'))
      app.setImageData('biggest_face', img_tk, fmt='PhotoImage')

    print('[!] Disconnected to camera')
    return False

  def detect_faces(self, img):
    blob = cv2.dnn.blobFromImage(img, scalefactor=1.0, size=(300, 300), mean=[104, 117, 123], swapRB=False, crop=False)
    self.facenet.setInput(blob)
    dets = self.facenet.forward()

    for i in range(dets.shape[2]):
      conf = dets[0, 0, i, 2]
      if conf < FACE_TRACK_THRESHOLD:
        continue

      track_face_found = False

      x1 = dets[0, 0, i, 3] * self.cam_size_resized[0]
      y1 = dets[0, 0, i, 4] * self.cam_size_resized[1]
      x2 = dets[0, 0, i, 5] * self.cam_size_resized[0]
      y2 = dets[0, 0, i, 6] * self.cam_size_resized[1]

      face_length = max(x2 - x1, y2 - y1)
      cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

      x1 = int(cx - face_length / 2)
      y1 = int(cy - face_length / 2)
      x2 = int(cx + face_length / 2)
      y2 = int(cy + face_length / 2)

      rect = [x1, y1, x2, y2]

      if face_length < MIN_FACE_SIZE:
        continue

      for face in self.faces:
        if not face.available or face.tracked:
          continue

        fdist = face.compute_face_distance(rect)

        if fdist < FACE_DISTANCE_THRESHOLD: # same face
          track_face_found = True
          face.init = False
          face.tracked = True
          face.rect = rect
          face.conf = conf
          break

      if conf > FACE_DETECTION_THRESHOLD and not track_face_found: # new face
        self.faces.append(Face(rect, conf))

    # check unavailable faces and find biggest face
    face_idx = 0
    biggest_idx, biggest_face_width = None, 0

    for i, face in enumerate(self.faces):
      if face.available and not face.init and not face.tracked:
        face.available = False
        del self.faces[i]
        continue

      face.init = False
      face.tracked = False
      face.biggest = False

      x1, y1, x2, y2 = face.rect

      if x2 - x1 > biggest_face_width:
        biggest_idx = face_idx
        biggest_face_width = x2 - x1

      face_idx += 1

    if biggest_idx is not None:
      self.faces[biggest_idx].biggest = True

  def destroy(self):
    print('[*] Release camera...')
    self.cap.release()