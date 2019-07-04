import cv2
import numpy as np
import torch

from backbone.model_irse import IR_50
from .config import *

class Recognizer():
  def __init__(self):
    torch.set_grad_enabled(False)

    print('[*] Load face recognition model...')
    self.backbone = IR_50([FACE_INPUT_SIZE, FACE_INPUT_SIZE])
    self.backbone.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    self.backbone.to(DEVICE)
    self.backbone.eval()

  def l2_norm(self, input, axis=1):
    norm = torch.norm(input, 2, axis, True)
    output = torch.div(input, norm)
    return output

  def compute_emb(self, img):
    # preprocess
    resized = cv2.resize(img, (128, 128))

    # center crop image
    a=int((128-FACE_INPUT_SIZE)/2) # x start
    b=int((128-FACE_INPUT_SIZE)/2+FACE_INPUT_SIZE) # x end
    c=int((128-FACE_INPUT_SIZE)/2) # y start
    d=int((128-FACE_INPUT_SIZE)/2+FACE_INPUT_SIZE) # y end
    cropped = resized[a:b, c:d] # center crop the image
    cropped = cropped[...,::-1] # BGR to RGB

    # flip image horizontally
    flipped = cv2.flip(cropped, 1)

    # load numpy to tensor
    cropped = cropped.swapaxes(1, 2).swapaxes(0, 1)
    cropped = np.reshape(cropped, [1, 3, FACE_INPUT_SIZE, FACE_INPUT_SIZE])
    cropped = np.array(cropped, dtype = np.float32)
    cropped = (cropped - 127.5) / 128.0
    cropped = torch.from_numpy(cropped)

    flipped = flipped.swapaxes(1, 2).swapaxes(0, 1)
    flipped = np.reshape(flipped, [1, 3, FACE_INPUT_SIZE, FACE_INPUT_SIZE])
    flipped = np.array(flipped, dtype = np.float32)
    flipped = (flipped - 127.5) / 128.0
    flipped = torch.from_numpy(flipped)

    # compute
    emb = self.backbone(cropped.to(DEVICE)).cpu()
    emb_flipped = self.backbone(flipped.to(DEVICE)).cpu()

    # features = self.l2_norm(emb)
    features_sum = self.l2_norm(emb + emb_flipped)

    features_sum = features_sum.numpy()

    return features_sum