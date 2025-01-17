import cv2
from flask import Flask, render_template, Response
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
BTN_PIN = 12
WAIT_TIME = 0.2
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
previousTime = time.time()
currentTime = None

GPIO.cleanup()
class Camera(object):
    def __init__(self):
        if cv2.__version__.startswith('2'):
            PROP_FRAME_WIDTH = cv2.cv.CV_CAP_PROP_FRAME_WIDTH
            PROP_FRAME_HEIGHT = cv2.cv.CV_CAP_PROP_FRAME_HEIGHT
        elif cv2.__version__.startswith('3') or cv2.__version__.startswith('4'):
            PROP_FRAME_WIDTH = cv2.CAP_PROP_FRAME_WIDTH
            PROP_FRAME_HEIGHT = cv2.CAP_PROP_FRAME_HEIGHT
        self.video = cv2.VideoCapture(0 , cv2.CAP_V4L)
    #self.video = cv2.VideoCapture(1)
    #self.video.set(PROP_FRAME_WIDTH, 640)
    #self.video.set(PROP_FRAME_HEIGHT, 480)
        self.video.set(PROP_FRAME_WIDTH, 320)
        self.video.set(PROP_FRAME_HEIGHT, 240)
    def __del__(self):
        self.video.release()
    def get_frame(self):
        success, img = self.video.read()
        #img = cv2.imread("cat.jpg")
        rows, cols = img.shape[:2]
        M = cv2.getRotationMatrix2D((cols/2, rows/2), 45, 1)
        img = cv2.warpAffine(img, M, (cols, rows))
        #cv2.imshow('Rotation', rotation)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        ret, jpeg = cv2.imencode('.jpg', img)
        return jpeg.tostring()

app = Flask(__name__)
@app.route('/')
def index():
    return render_template('stream.html')
def gen(camera):
    try:
        prev = None
        while True:
            input = GPIO.input(BTN_PIN)
            if input == GPIO.LOW and prev == GPIO.HIGH and (currentTime - previousTime) > WAIT_TIME:
                previousTime = currentTime
                frame = camera.get_frame()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
                time.sleep(0.5)
            prev = input
    except KeyboardInterrupt:
        print("end")
    finally:
        GPIO.cleanup()

@app.route('/video_feed')
def video_feed():
    return Response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)
