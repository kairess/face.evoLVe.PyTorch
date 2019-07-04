from appJar import gui
from PIL import Image, ImageTk
import numpy as np

from Camera import Camera
from config import *

import time

camera = Camera(device=0, resize=CAM_RESIZED)

# main gui
print('[*] Creating UI...')
app = gui('CRAIMS - Customer Relationship AI Management System') # , '%sx%s' % WINDOW_SIZE
app.setBg(COLOR_SCHEME['bg'])
app.setFg(COLOR_SCHEME['font'])
app.setFont(14)

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

    def capture_face():
      print('capture_face')

    def recognize():
      print('recognize')

    with app.frame('CAMERA_CONTROL', row=3, column=0, stretch='COLUMN'):
      app.addButtons(['Capture Face', 'Find Face'], [capture_face, recognize])

    with app.frame('MENU_CONTROL', row=3, column=1, stretch='COLUMN'):
      app.addButtons(['Submit2', 'Cancel2'], press)

  ''' TAB 2 '''
  with app.tab('TAB2'):
    app.addLabel('tab2_label', 'tab2')
    img_tk = ImageTk.PhotoImage(Image.fromarray(np.zeros((224, 224, 3), np.uint8), 'RGB'))
    app.addImageData('biggest_face', img_tk, fmt='PhotoImage')

# threading camera
print('[*] Initializing camera thread...')
app.thread(camera.thread, app)

# exit
def check_stop():
  ok = app.yesNoBox('종료 확인', '프로그램을 종료합니다')
  if ok:
    print('[*] Terminating...')
    camera.destroy()
  return ok

app.setStopFunction(check_stop)

print('[*] App has been started successfully!')
app.go()
