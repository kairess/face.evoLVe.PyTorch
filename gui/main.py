from appJar import gui
from PIL import Image, ImageTk
import time
import numpy as np

from Camera import Camera

# CAM_SIZE = (1920, 1080)
CAM_RESIZED = (640, 360)

camera = Camera(device=0, resize=CAM_RESIZED)

# main gui
app = gui('Login Window', '640x480')
app.setBg('orange')
app.setFont(18)

app.addLabel('title', 'Welcome to appJar')
app.setLabelBg('title', 'red')

app.addLabelEntry('Username')
app.addLabelSecretEntry('Password')
app.setFocus('Username')

img_tk = ImageTk.PhotoImage(Image.fromarray(np.zeros((CAM_RESIZED[1], CAM_RESIZED[0], 3), np.uint8), 'RGB'))
app.addImageData('pic', img_tk, fmt='PhotoImage')

# threading camera
app.thread(camera.thread, app)

# app.text('log', scroll=True)


def press(button):
  if button == 'Cancel':
    app.stop()
  else:
    usr = app.getEntry('Username')
    pwd = app.getEntry('Password')
    print('User:', usr, 'Pass:', pwd)

app.addButtons(['Submit', 'Cancel'], press)


# exit
def check_stop():
  ok = app.yesNoBox('종료 확인', '프로그램을 종료합니다')
  if ok:
    camera.cap.release()
    time.sleep(2)
  return ok

app.setStopFunction(check_stop)

app.go()



# data = [["Homer", "Simpson", "America", 40],
#         ["Marge", "Simpson", "America", 38],
#         ["Lisa", "Simpson", "America", 12],
#         ["Maggie", "Simpson", "America", 4], 
#         ["Bart", "Simpson", "America", 14]]

# with gui("Updating Labels") as app:
#     with app.tabbedFrame("Address Book"):
#         for pos in range(len(data)):
#             with app.tab(data[pos][0]):
#                 app.entry(str(pos)+"fName", data[pos][0], label="First Name")
#                 app.entry(str(pos)+"lName", data[pos][1], label="Last Name")
#                 app.entry(str(pos)+"country", data[pos][2], label="Country")
#                 app.entry(str(pos)+"age", data[pos][3], kind='numeric', label="Age")