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
import os,sys,boto3,configparser
from mcpi.minecraft import Minecraft
from picamera import PiCamera
from time import sleep

import coloredlogs, logging                     #
log = logging.getLogger(__name__)               # https://coloredlogs.readthedocs.io/en/latest/readme.html#usage
coloredlogs.install(level='DEBUG', logger=log)  #  

POS_X           = -6.5
POS_Y           =  2.0
POS_Z           =  5.5
Z_VARIANCE      =  0.2
BUCKET          = 'rbw-pi-camera-uploads-01'
FOLDER_PREFIX   = 'uploads/'  #trailing '/'

img_path = os.path.dirname(os.path.abspath(__file__)) +'/img/photobooth.jpg'

def upload(img): #{{{
    file = open(img, 'rb+')
    s3  = boto3.client('s3')
    key = FOLDER_PREFIX+os.path.basename(file.name)
    log.debug("Uploading %s to AWS S3> %s:%s..." % (img, BUCKET, key))
    s3.upload_fileobj(file, BUCKET, key)
    log.debug  ('  Upload worked!')
#}}}

def main():
    log.info("Starting "+sys.argv[0])
    log.debug("Will detect player(x,y,z) at: (%.2f, %.2f, %.2f)"%(POS_X, POS_Y, POS_Z))

    try:
        # setup camera:
        camera =PiCamera()
        #camera.hflip = True 
        log.debug("Camera connected.")

        # setup mincraft:
        mc = Minecraft.create()
        log.debug("Connected to Minecraft.")
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

            if (( x >= POS_X) and (y == POS_Y) and ((POS_Z - Z_VARIANCE) <= z <= (POS_Z + Z_VARIANCE)) ):
                mc.postToChat("Welcome to the photobooth")
                sleep(1)
                mc.postToChat("Smile! :-)")
                sleep(1)
                camera.start_preview()
                sleep(3)
                log.debug("Saving image to: %s "%img_path)
                camera.capture(img_path)
                camera.stop_preview()
                mc.postToChat("SNAP! Uploading to AWS for processing...")

                log.debug("Uploading img (%s) to AWS S3... "%img_path)
                upload(img_path)
                mc.postToChat("Upload complete.")
                sleep(5)  # pause to let user get out of the way

    except KeyboardInterrupt:  
        log.warning("Caught ^C, and exiting")
        mc.postToChat("Photobooth script disconnected")
    except:  
        log.exception("Unexpected exception occurred! ")

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__": main()
print ("Done.")
#//EOF
