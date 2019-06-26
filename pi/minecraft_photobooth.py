#!/usr/bin/env python3
#
#  auth: rbw
#  date: 20190626
#  desc: 
#   This script detects a minecraft user at a particular location, and takes a
#   picture of them, using the picamera, and uploads it to AWS S3
#
#   based on Eddie's original code
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import os,sys,configparser
from mcpi.minecraft import Minecraft
from picamera import PiCamera
from time import sleep
from upload_file_to_S3 import *
import coloredlogs, logging                     #
log = logging.getLogger(__name__)               # https://coloredlogs.readthedocs.io/en/latest/readme.html#usage
coloredlogs.install(level='DEBUG', logger=log)  #  

POS_X = -0.3
POS_Y =  2.0
POS_Z =  1.3

img_path = os.path.dirname(os.path.abspath(__file__)) +'/img/photobooth.jpg'


def main():
    log.info("Starting "+sys.argv[0])
    log.debug("Will detect player(x,y,z) at: (%.2f, %.2f, %.2f)"%(POS_X, POS_Y, POS_Z))

    try:
        # setup camera:
        camera =PiCamera()
        camera.hflip = True 
        log.debug("Camera connected.")

        # setup mincraft:
        mc = Minecraft.create()
        mc.postToChat("Hi! Photobooth script is connected (y)")
    except:  
        log.exception("Either camera or minecraft error; pls check stacktrace. ")
        log.error("Will exit program.")
        sys.exit()


    try:

        log.info("Starting to listen  (^C to stop)...")
        while True:
            x,y,z,=mc.player.getPos()

            sleep(3)

            if (( x >= POS_X) and (y == POS_Y) and (z == POS_Z)):
                mc.postToChat("welcome to the photobooth")
                sleep(2)
                mc.postToChat("Smile! :-)")
                sleep(1)
                camera.start_preview()
                sleep(3)
                print("Saving image to: %s "%img_path)
                camera.capture(img_path)
                camera.stop_preview()

                print("Uploading img (%s) to AWS S3... "%img_path)
                upload(img_path)

    except KeyboardInterrupt:  
        log.warning("Caught ^C, and exiting")
    except:  
        log.exception("Unexpected exception occurred! ")

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__": main()
print ("Done.")
#//EOF
