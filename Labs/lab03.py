import RPi.GPIO as GPIO
import time
import serial

BUZZ_PIN = 16  
LED_PIN = 12
brightness = 0
pitches = {
    'c': 262,
    'd': 294,
    'e': 330,
    'f': 349,
    'g': 392,
    'a': 440,
    'b': 493
}

GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUZZ_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

# Setup PWM for buzzer and LED
pwm_buzz = GPIO.PWM(BUZZ_PIN, 440)  
pwm_led = GPIO.PWM(LED_PIN, 1000)  

pwm_buzz.start(0)
pwm_led.start(0)

# Serial setup (adjust the port and baudrate as needed)
ser = serial.Serial('/dev/ttyAMA5', baudrate=9600,
parity=serial.PARITY_NONE,
stopbits=serial.STOPBITS_ONE,
bytesize=serial.EIGHTBITS
)


def set_buzzer_frequency(note):
    if note in pitches:
        freq =int( pitches[note])
        pwm_buzz.ChangeDutyCycle(50)  # Set volume
        pwm_buzz.ChangeFrequency(freq)
        print(f"Buzzer playing {note} at {freq} Hz")
    elif note == 'z':
        pwm_buzz.ChangeDutyCycle(0)  # Stop sound
        print("Buzzer stopped")

def adjust_led_brightness(change):
    try:
        global brightness
        #change = int(change)
        if -100 <= change <= 100:
            # Adjust the brightness
            brightness = max(0, min(100, change +brightness))
            pwm_led.ChangeDutyCycle(brightness)
            print(f"LED brightness set to {brightness}%")
        else:
            print("Invalid brightness value. Should be in range [-100, 100].")
    except ValueError:
        print("Brightness value should be an integer.")

try:
    while True:
        input_line = ser.readline().decode('utf-8').strip()
        #data = ser.readline()
        print(input_line)
        #ser.write(data)
        ser.flushInput()
        time.sleep(0.1)

        if input_line.startswith("play"):
            note = input_line[4]  # Extract the note character after 'play'
            set_buzzer_frequency(note)
        if input_line.startswith("b"):
            brightness_change =int( input_line[1:])  # Extract brightness percentage
            adjust_led_brightness(brightness_change)
except KeyboardInterrupt:
    print("\nKeyboardInterrupt")
finally:
    pwm_buzz.stop()
    pwm_led.stop()
    #　GPIO.cleanup()
