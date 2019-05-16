#!/usr/bin/env python3
#
#  auth: rbw
#  date: 20190511
#  desc: 
#       https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import os,configparser
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import pygame 
import logging,coloredlogs,sys,pprint,traceback 
from picamera import PiCamera

GPIO.setmode(GPIO.BCM) # use pin number printed on shield (ie no.s after GPIO at https://raspberrypi.stackexchange.com/a/12967))
GPIO_BUTTON_PIN = 15
GPIO_LED_PIN    = 14


MP3_PROCESSING_FILENAME = os.path.dirname(os.path.abspath(__file__)) +'/replace_me.mp3'
CAPTURED_PIC_FILENAME   = os.path.dirname(os.path.abspath(__file__)) +'/img/photobooth.jpg'

# loggin config {{{
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(sys.argv[0])
coloredlogs.install(level='DEBUG', logger=log)
pp = pprint.PrettyPrinter(indent=4)  # USED?
#}}}

processing = False
def button_callback(channel):
    global processing
    log.info("Button %s was pushed!"%(GPIO_BUTTON_PIN))
    if processing:
        log.warn("Still processing")
        return

    processing = True

    log.info("Taking picture..")
    burp = pygame.mixer.Sound(MP3_PROCESSING_FILENAME)
    camera.capture(CAPTURED_PIC_FILENAME)

    processing = False


def main():
    log.info("Starting "+sys.argv[0])

    try:  
        camera =PiCamera()
        camera.vflip = True 
        camera.start_preview()

        pygame.init() 
        pygame.mixer.init() 

        GPIO.setup(GPIO_BUTTON_PIN, GPIO.IN,    pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(GPIO_LED_PIN,    GPIO.OUT,   initial=GPIO.LOW)

        # Setup event on rising edge
        GPIO.add_event_detect(GPIO_BUTTON_PIN, GPIO.RISING, callback=button_callback) 

        while True:
            a=1
            #:message = input("Press ENTER to quit: ")
      
    except KeyboardInterrupt:  
        log.warning("Caught ^C, and exiting")
    except:  
        log.exception("Unexpected exception occurred! ")
    finally:  
        camera.stop_preview()
        log.debug("Cleaning up GPIO.")
        GPIO.cleanup() # this ensures a clean exit  



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__": main()
#//EOF
