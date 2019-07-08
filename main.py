#-*- coding: utf-8 -*-

from appJar import gui
from PIL import Image, ImageTk
import numpy as np
import cv2

from gui.Camera import Camera
from gui.User import User
from gui.Recognizer import Recognizer
from gui.config import *
from gui.Database import Database

import time, sqlite3

db = Database()
users = db.get_users()

camera = Camera(device=0, resize=CAM_RESIZED)
recognizer = Recognizer()

'''
Main GUI
'''
print('[*] Creating UI...')
app = gui('CRAIMS - Customer Relationship AI Management System') # , '%sx%s' % WINDOW_SIZE
app.setBg(COLOR_SCHEME['bg'])
app.setFg(COLOR_SCHEME['font'])
app.setFont(size=14) #, family='Nanum Gothic')

with app.tabbedFrame('TABS'):
  with app.tab('MAIN'):
    with app.frame('CAMERA', row=0, column=0, stretch='COLUMN', rowspan=3):
      img_tk = ImageTk.PhotoImage(Image.fromarray(np.zeros((CAM_RESIZED[1], CAM_RESIZED[0], 3), np.uint8), 'RGB'))
      app.addImageData('cam', img_tk, fmt='PhotoImage')

    with app.frame('TITLE', row=0, column=1, stretch='COLUMN'):
      app.addLabel('menu_title', 'MENU')

      app.addEmptyMessage('selected_menu')
      app.setMessage('selected_menu', '1.abcdefghijklmnopqrstuvwxyz\n2.abcdefghijklmnopqrstuvwxyz\n3.abcdefghijklmnopqrstuvwxyz\n4.abcdefghijklmnopqrstuvwxyz')

    def press(button_idx):
      print(int(button_idx))

    with app.frame('MENU1', row=1, column=1, stretch='COLUMN', sticky='NEW'):
      app.addButtons([
        ['0', '1', '2', '3', '4'],
        ['5', '6', '7', '8', '9']
      ], press)

    with app.frame('MENU2', row=2, column=1, stretch='COLUMN', sticky='NEW'):
      app.addButtons([
        ['10', '11', '12', '13', '14'],
        ['15', '16', '17', '18', '19']
      ], press)

    def button_capture_face():
      camera.captured_face_img = camera.biggest_face_img.copy()

      img_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(camera.captured_face_img, cv2.COLOR_BGR2RGB), 'RGB'))
      app.setImageData('biggest_face', img_tk, fmt='PhotoImage')
      app.showSubWindow('User Window')

    def button_recognize():
      print('button_recognize')

    with app.frame('CAMERA_CONTROL', row=3, column=0, stretch='COLUMN'):
      app.addButtons(['Capture Face', 'Find Face'], [button_capture_face, button_recognize])

    with app.frame('MENU_CONTROL', row=3, column=1, stretch='COLUMN'):
      app.addButtons(['Submit2', 'Cancel2'], press)

  ''' TAB 2 '''
  with app.tab('TAB2'):
    app.addLabel('tab2_label', 'tab2')

# threading camera
print('[*] Initializing camera thread...')
app.thread(camera.thread, app)

'''
Select user sub window
'''
app.startSubWindow('User Window', modal=True)

img_tk = ImageTk.PhotoImage(Image.fromarray(np.zeros((128, 128, 3), np.uint8), 'RGB'))
app.addImageData('biggest_face', img_tk, fmt='PhotoImage')

app.addEntry('user_name')
# app.addValidationEntry('user_name')
# app.setEntryDefault('user_name', '김폭풍')

app.addRadioButton('user_gender', '여')
app.addRadioButton('user_gender', '남')

app.addLabelOptionBox('user_age', [10, 20, 30, 40, 50, 60, 70, 80])
app.setOptionBox('user_age', 2, value=False, callFunction=False)

app.addProperties('user_tastes', USER_TASTES)

app.setFocus('user_name')

def reset_user_inputs():
  img_tk = ImageTk.PhotoImage(Image.fromarray(np.zeros((128, 128, 3), np.uint8), 'RGB'))
  app.setImageData('biggest_face', img_tk, fmt='PhotoImage')

  app.setEntry('user_name', '', callFunction=False)
  app.setRadioButton('user_gender', '여', callFunction=False)
  app.setOptionBox('user_age', 2, value=False, callFunction=False)
  app.resetProperties('user_tastes', callFunction=False)

def button_create_user():
  global users

  if camera.captured_face_img is None:
    reset_user_inputs()
    print('[!] Error: button_create_user()')
    return False

  user_name = app.getEntry('user_name')
  user_gender = 0 if app.getRadioButton('user_gender') == '남' else 1
  user_age = int(app.getOptionBox('user_age'))
  user_tastes = app.getProperties('user_tastes')

  if user_name is None or user_name == '':
    # app.setEntryInvalid('user_name')
    app.setFocus('user_name')
    return False

  user_face_img = camera.captured_face_img.copy()

  emb = recognizer.compute_emb(user_face_img)

  # check same faces
  nearest_user, nearest_dist = recognizer.find_nearest_user(emb, users)

  if nearest_user is not None:
    print('[!] Similar user exist!', nearest_user, nearest_dist)
    return False

  db.create_user(name=user_name, gender=user_gender, age=user_age, tastes=user_tastes, emb=emb, img=user_face_img)

  users = db.get_users()

  reset_user_inputs()
  app.hideSubWindow('User Window')

def button_cancel_close():
  reset_user_inputs()
  app.hideSubWindow('User Window')

app.addButtons(['등록', '취소'], [button_create_user, button_cancel_close])

app.stopSubWindow()
'''
Exit
'''
def check_stop():
  ok = app.yesNoBox('종료 확인', '프로그램을 종료합니다')
  if ok:
    print('[*] Terminating...')
    camera.destroy()
  return ok

app.setStopFunction(check_stop)

print('[*] App has been started successfully!')
app.go()
