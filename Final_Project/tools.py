# Customized Video Capture Program
import cv2
import threading
import os
import time
import random
import numpy as np
import platform as plt

class CustomVideoCapture():

    # Initialize with the default camera device as 0
    def __init__(self, dev=0):
        self.cap = cv2.VideoCapture(dev)
        self.ret = ''
        self.frame = []     
        self.win_title = 'Modified with set_title()'
        self.info = ''
        self.isStop = False
        self.t = threading.Thread(target=self.video, name='stream')

    # Start the thread using this function
    def start_stream(self):
        self.t.start()
    
    # Stop the thread and release the camera
    def stop_stream(self):
        self.isStop = True
        self.cap.release()
        cv2.destroyAllWindows()

    # Get the most recent frame
    def get_current_frame(self):
        return self.ret, self.frame
    
    # Set the display window title
    def set_title(self, txt):
        self.win_title = txt

    # Main function running in the thread
    def video(self):
        global close_thread
        close_thread = 0

        while not self.isStop:
            self.ret, self.frame = self.cap.read()

            if self.info != '':
                cv2.putText(self.frame, self.info, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.namedWindow(self.win_title)
                cv2.imshow(self.win_title, self.frame)
                cv2.resizeWindow(self.win_title, 640, 480)

            if cv2.waitKey(1) == 27:
                break
            if close_thread == 1:
                break

        self.stop_stream()

# Program for preprocessing data
def preprocess(frame, resize=(224, 224), norm=True):
    '''
    Configure format (1, 224, 224, 3), resize, normalize, insert data, and return the correctly formatted data
    '''
    height, width, _ = frame.shape
    crop_size = min(width, height)
    x_start = (width - crop_size) // 2
    y_start = (height - crop_size) // 2
    cropped_image = frame[y_start:y_start + crop_size, x_start:x_start + crop_size]
    input_format = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    frame_resize = cv2.resize(cropped_image, resize)
    frame_norm = ((frame_resize.astype(np.float32) / 127.0) - 1) if norm else frame_resize
    input_format[0] = frame_norm
    return input_format

# Load the pre-trained model
def load_engine(engine_path):
    if trt_found:
        TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
        trt_runtime = trt.Runtime(TRT_LOGGER)
        
        with open(engine_path, 'rb') as f:
            engine_data = f.read()
        engine = trt_runtime.deserialize_cuda_engine(engine_data)
        return engine
    else:
        print("Cannot load engine because the TensorRT module is not found")
        exit(1)

# Parse the output information
def parse_output(preds, label) -> 'return ( class id, class name, probability) ':
    preds = preds[0] if len(preds.shape) == 4 else preds
    trg_id = np.argmax(preds)
    trg_name = label[trg_id]
    trg_prob = preds[trg_id]
    return (trg_id, trg_name, trg_prob)
