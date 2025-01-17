import RPi.GPIO as GPIO
import time

time_pre = 0
wait = [0.5, 1, 2]
wait_time = wait[0]

def ButtonPressed(btn):
    global time_pre, wait_time
    time_pre += 1
    wait_time = wait[time_pre % 3] 
    print("Button pressed @", time.ctime())

GPIO.setmode(GPIO.BOARD)
BTN_PIN = 16
LED_PIN = 15
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


GPIO.add_event_detect(BTN_PIN, GPIO.FALLING, callback=ButtonPressed, bouncetime=200)

try:
    while True:
        print("LED is on.")
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(wait_time)
        print("LED is off.")
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(wait_time)
except KeyboardInterrupt:
    print("Exception: KeyboardInterrupt")
finally:
    GPIO.cleanup()
