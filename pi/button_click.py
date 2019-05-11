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

GPIO.setmode(GPIO.BCM) # use pin number printed on shield (ie no.s after GPIO at https://raspberrypi.stackexchange.com/a/12967))
GPIO_BUTTON_PIN = 15
GPIO_LED_PIN    = 14

# loggin config {{{
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(sys.argv[0])
coloredlogs.install(level='DEBUG', logger=log)
pp = pprint.PrettyPrinter(indent=4)  # USED?
#}}}


def main():
    log.info("Starting "+sys.argv[0])
    GPIO.setup(GPIO_BUTTON_PIN, GPIO.IN,    pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(GPIO_LED_PIN,    GPIO.OUT,   initial=GPIO.LOW)

    try:  
        while True: # Run forever
            GPIO.output(GPIO_LED_PIN, GPIO.LOW)  # Turn LED off
            if GPIO.input(GPIO_BUTTON_PIN) == GPIO.HIGH:
                log.info("Button %s was pushed!"%(GPIO_BUTTON_PIN))
                GPIO.output(GPIO_LED_PIN, GPIO.HIGH) # Turn LED on
      
    except KeyboardInterrupt:  
        log.warn("Caught ^C, and exiting")
    except:  
        log.exception("Unexpected exception occurred! ")
    finally:  
        log.debug("Cleaning up GPIO.")
        GPIO.cleanup() # this ensures a clean exit  



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__": main()
#//EOF
