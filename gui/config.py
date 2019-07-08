
WINDOW_SIZE = (1280, 960)

# CAM_SIZE = (1920, 1080)

CAM_RESIZED = (640, 640)

COLOR_SCHEME = {
  'bg': '#FFFFFF',
  'font': '#00171F',
  'blue1': '#00A8E8',
  'blue2': '#007EA7',
  'blue3': '#003459'
}

FACE_RECOGNITION_THRESHOLD = 1.0
FACE_DETECTION_THRESHOLD = 0.7
FACE_TRACK_THRESHOLD = 0.35
FACE_DISTANCE_THRESHOLD = 100
MIN_FACE_SIZE = 100

FACE_INPUT_SIZE = 112

DEVICE = 'cpu' # torch.device("cuda:0")
USE_FLIP = True
MODEL_PATH = 'pretrained/backbone_ir50_asia.pth'

USER_TASTES = {
  'Cheese': False,
  'Tomato': False,
  'Bacon': False,
  'Corn': False,
  'Mushroom': False
}
