import cv2
import threading
import os
import time
import random
import numpy as np
import tflite_runtime.interpreter as tflite
import configparser
from tools import CustomVideoCapture, preprocess, parse_output

import zipfile
from azure.storage.blob import BlobServiceClient

# Azure Blob Storage connection string
config = configparser.ConfigParser()
config.read('config.ini')
storage_connection_string = config['AzureStorage']['STORAGE_CONNECTION_STRING']
blob_service_client = BlobServiceClient.from_connection_string(storage_connection_string)
container_name = 'videos'

def compress_file(file_list, zip_path):
    """
    Compress all files in file_list into a zip file at zip_path.
    """
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for f in file_list:
            if os.path.exists(f):
                zipf.write(f, os.path.basename(f))
    print(f"Files have been compressed to {zip_path}")

def upload_to_blob(file_path, blob_name):
    """
    Upload file_path to Azure Blob as blob_name.
    """
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        with open(file_path, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"File {blob_name} successfully uploaded to {container_name}!")
    except Exception as e:
        print(f"Upload failed: {e}")

actionState = []

def validate(P):
    return str.isdigit(P) or P == ''

def main():
    """
    1. Start the camera and begin cheating detection.
    2. Record the video while saving detection logs to a text file.
    3. After completion, compress the video and log files, upload them to Azure, and clean up local files.
    """
    interpreter = tflite.Interpreter(model_path="model_unquant.tflite")
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    with open("labels.txt", 'r') as f:
        labels = [line.strip().split()[1] for line in f.readlines()]

    actionState = ['normal1', 'cheating-right1', 'cheating-left1']

    vid = CustomVideoCapture()
    vid.set_title('Cheating Detection')
    vid.start_stream()

    # Prepare video recording (using mp4v codec)
    time_tag = time.strftime("%Y%m%d-%H%M%S", time.localtime())
    video_filename = f"cheating_detection_{time_tag}.mp4"
    first_frame = None
    while True:
        ret_test, frame_test = vid.get_current_frame()
        if ret_test and frame_test is not None:
            first_frame = frame_test
            break
        else:
            time.sleep(0.05)
    height, width, _ = first_frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_filename, fourcc, 20.0, (width, height))

    # Prepare the log file
    cheating_log_file = f"cheating_log_{time_tag}.txt"
    log_file = open(cheating_log_file, "w")

    first_detect = False
    past_time = time.localtime()
    prev = "normal1"

    print("=== Cheating detection in progress, recording video ===")
    print("=== Close the window or press ESC to exit ===")

    try:
        while not vid.isStop:
            ret, frame = vid.get_current_frame()
            if not ret or frame is None:
                continue

            out.write(frame)

            data = preprocess(frame, resize=(224, 224), norm=True)
            interpreter.set_tensor(input_details[0]['index'], data)
            interpreter.invoke()

            prediction = interpreter.get_tensor(output_details[0]['index'])[0]
            trg_id, trg_class, trg_prob = parse_output(prediction, labels)

            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

            if 'cheating' in trg_class and trg_prob > 0.8 and trg_class != prev:
                if not first_detect:
                    log_message = f"Detected cheating: {current_time}"
                    print(log_message)
                    log_file.write(log_message + "\n")
                    first_detect = True
                    past_time = time.localtime()
                else:
                    if (time.mktime(time.localtime()) - time.mktime(past_time)) > 5:
                        log_message = f"Detected cheating: {current_time}"
                        print(log_message)
                        log_file.write(log_message + "\n")
                        past_time = time.localtime()

            prev = trg_class
            if trg_class == 'normal1':
                vid.info = f'normal, Now: {current_time}'
            else:
                vid.info = f'cheating, Now: {current_time}'

    finally:
        out.release()
        log_file.close()
        vid.stop_stream()

    print("=== Detection complete, compressing files and uploading to Azure ===")

    zip_filename = f"cheating_package_{time_tag}.zip"
    compress_file([video_filename, cheating_log_file], zip_filename)
    upload_to_blob(zip_filename, zip_filename)

    print("Recording, compression, and upload to Azure complete.")
    while True:
        print ("\n=== Do you want to delete the local files? ===")
        print ("1. Yes\n2. No")
        P = input("Please enter your choice: ")
        if P == '1':
            if os.path.exists(video_filename):
                os.remove(video_filename)
            if os.path.exists(cheating_log_file):
                os.remove(cheating_log_file)
            if os.path.exists(zip_filename):
                os.remove(zip_filename)
            print("Files have been deleted.\n")
            break
        elif P == '2':
            print("Files have not been deleted.\n")
            break
        else:
            print("Invalid input.\n")
    print("-" * 30)
    print(f'Video stream thread closed: {not vid.t.is_alive()}')
    print('End of detection')