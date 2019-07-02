import torch
import cv2
import numpy as np

from backbone.model_irse import IR_50
from util.utils_test import *

import time, os, glob, random

IMG_SIZE = 112
DEVICE = 'cpu' # torch.device("cuda:0")
USE_FLIP = True
MODEL_PATH = 'pretrained/backbone_ir50_asia.pth'

# load model
backbone = IR_50([IMG_SIZE, IMG_SIZE])
backbone.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
backbone.to(DEVICE)
backbone.eval()

img_list = glob.glob('imgs/*/*.jpg')
random.shuffle(img_list)

for img_path_A in img_list:
  img_path_B = random.sample(img_list, k=1)[0]

  _, subject_A, id_A = img_path_A.split('/')
  _, subject_B, id_B = img_path_B.split('/')

  img_A = cv2.imread(img_path_A, cv2.IMREAD_COLOR)
  img_B = cv2.imread(img_path_B, cv2.IMREAD_COLOR)

  cropped_A, flipped_A = preprocess_input(img_A, img_size=IMG_SIZE)
  cropped_B, flipped_B = preprocess_input(img_B, img_size=IMG_SIZE)

  # inference
  with torch.no_grad():
    # compute A
    emb_A = backbone(cropped_A.to(DEVICE)).cpu()
    emb_A_flipped = backbone(flipped_A.to(DEVICE)).cpu()

    features_A = l2_norm(emb_A)
    features_A_sum = l2_norm(emb_A + emb_A_flipped)
    
    # compute B
    emb_B = backbone(cropped_B.to(DEVICE)).cpu()
    emb_B_flipped = backbone(flipped_B.to(DEVICE)).cpu()

    features_B = l2_norm(emb_B)
    features_B_sum = l2_norm(emb_B + emb_B_flipped)

    # compute distance of features
    dist = np.linalg.norm(features_A_sum - features_B_sum)

    print(subject_A, subject_B, dist)

    # show result
    cv2.imshow('AB', np.concatenate([img_A, img_B], axis=1))
    if cv2.waitKey(0) == ord('q'):
      break
