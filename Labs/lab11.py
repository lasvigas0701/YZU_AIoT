import argparse
from gtts import gTTS
import subprocess
import tempfile
import speech_recognition as sr
import RPi.GPIO as GPIO

LED_PIN = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

#obtain audio from the microphone
recognizer = sr.Recognizer()

while True:
    with sr.Microphone(sample_rate = 16000) as source:
        print("Please wait. Calibrating microphone...")
        #listen for 1 seconds and create the ambient noise energy level
        # recognizer.adjust_for_ambient_noise(source, duration=1)
        # recognizer.energy_threshold = 4000
        print("Say something!")
        audio = recognizer.listen(source, phrase_time_limit=5)

    # recognize speech using Google Speech Recognition
        try:
            results = recognizer.recognize_google(audio, language='zh-TW')
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as temp_file:
                temp_path = temp_file.name
            
            if "開燈" in results:
                tts = gTTS(text="燈已開啟", lang='zh-TW')
                tts.save(temp_path)
                GPIO.output(LED_PIN, GPIO.HIGH)
                subprocess.run(
                    ['vlc', '--play-and-exit', temp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif "關燈" in results:
                tts = gTTS(text="燈已關閉", lang='zh-TW')
                tts.save(temp_path)
                GPIO.output(LED_PIN, GPIO.LOW)
                subprocess.run(
                    ['vlc', '--play-and-exit', temp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            print(results)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("No response from Google Speech Recognition service: {0}".format(e))
    

# # Set up argument parser with default values
# parser = argparse.ArgumentParser(description="Generate speech and play it.")
# parser.add_argument('text', type=str, nargs='?', default="hello", help="Text to convert to speech")
# parser.add_argument('lang', type=str, nargs='?', default="en", help="Language for the speech (e.g., 'en' for English)")

# # Parse arguments
# args = parser.parse_args()

# # Generate temporary file with delete=True
# with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as temp_file:
#     temp_path = temp_file.name
#     tts = gTTS(text=args.text, lang=args.lang)
#     tts.save(temp_path)

#     # Play the MP3 file
#     try:
#         subprocess.run(
#             ['vlc', '--play-and-exit', temp_path],
#             stdout=subprocess.DEVNULL,
#             stderr=subprocess.DEVNULL
#         )
#     except FileNotFoundError:
#         print("VLC is not installed or not found in the PATH.")
