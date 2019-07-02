import mxnet as mx
import cv2

import os

# https://github.com/deepinsight/insightface/wiki/Dataset-Zoo#asian-celeb-94k-ids28m-images8-recommend

record = mx.recordio.MXIndexedRecordIO('/Users/visualcamp/Development/tf/GazeCapture/dataset/faces_glintasia/train.idx', '/Users/visualcamp/Development/tf/GazeCapture/dataset/faces_glintasia/train.rec', 'r')

os.makedirs('imgs', exist_ok=True)

for i in range(100):
  item = record.read()

  if not item:
    break

  header, img = mx.recordio.unpack_img(item)

  label = header.label[0]
  label_str = str(int(label)).zfill(5)
  filename = str(header.id) + '.jpg'

  os.makedirs(os.path.join('imgs', label_str), exist_ok=True)

  cv2.imwrite(os.path.join('imgs', label_str, filename), img)
