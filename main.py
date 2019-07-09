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
app.setLogLevel('ERROR')

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
      app.showSubWindow('Create User Window')

    def button_recognize():
      global users

      img_A = camera.biggest_face_img.copy()
      emb_A = recognizer.compute_emb(img_A)

      nearest_user, nearest_dist = recognizer.find_nearest_user(emb_A, users)

      if nearest_user is None:
        app.warningBox('wb_no_matched_user', '일치하는 사람이 없습니다!')
        return False

      app.setImage('recognized_user_face', 'db/face_imgs/%d.jpg' % (nearest_user['id'],))

      img_tk = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(img_A, cv2.COLOR_BGR2RGB), 'RGB'))
      app.setImageData('current_user_face', img_tk, fmt='PhotoImage')

      app.setLabel('l_dist', nearest_dist)
      app.setLabel('l_user_name', nearest_user['name'])
      app.setLabel('l_user_gender', '남' if nearest_user['gender'] == 0 else '여')
      app.setLabel('l_user_age', '%d대' % nearest_user['age'])
      app.setLabel('l_user_tastes', nearest_user['tastes'])

      app.showSubWindow('Recognize User Window')

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
Create user sub window
'''
app.startSubWindow('Create User Window', modal=True)

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
    app.warningBox('wb_similar_face_exist', '비슷한 사람이 있습니다!\nid:%s - %s' % (nearest_user['id'], nearest_dist))
    return False

  db.create_user(name=user_name, gender=user_gender, age=user_age, tastes=user_tastes, emb=emb, img=user_face_img)

  users = db.get_users()

  reset_user_inputs()
  app.hideSubWindow('Create User Window')

def button_cancel_close():
  reset_user_inputs()
  app.hideSubWindow('Create User Window')

app.addButtons(['등록', '취소'], [button_create_user, button_cancel_close])

app.stopSubWindow()

'''
Recognize user sub window
'''
app.startSubWindow('Recognize User Window', modal=True)

app.addLabel('l_fcu', '카메라')
img_tk = ImageTk.PhotoImage(Image.fromarray(np.zeros((128, 128, 3), np.uint8), 'RGB'))
app.addImageData('current_user_face', img_tk, fmt='PhotoImage')

app.addLabel('l_ruf', '인식결과')
img_tk = ImageTk.PhotoImage(Image.fromarray(np.zeros((128, 128, 3), np.uint8), 'RGB'))
app.addImageData('recognized_user_face', img_tk, fmt='PhotoImage')

app.addLabel('l_dist', 'Label 1')
app.addLabel('l_user_name', 'Label 1')
app.addLabel('l_user_gender', 'Label 1')
app.addLabel('l_user_age', 'Label 1')
app.addLabel('l_user_tastes', 'Label 1')

def button_select_user():
  print('button_select_user')

def button_close_user():
  app.hideSubWindow('Recognize User Window')

app.addButtons(['선택', '취소2'], [button_select_user, button_close_user])

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
