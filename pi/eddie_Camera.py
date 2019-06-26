#!/usr/bin/env python3
import os,sys,configparser
from mcpi.minecraft import Minecraft
from picamera import PiCamera
from time import sleep
from upload_file_to_S3 import *

img_path = os.path.dirname(os.path.abspath(__file__)) +'/img/photobooth.jpg'

def upload(img): #{{{
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(AWS_CREDS_FILE))

    file = open(img, 'rb+')
    key = FOLDER_PREFIX+os.path.basename(file.name)
    print("Uploading %s to AWS S3> %s:%s..." % (img, BUCKET, key))

    if upload_to_s3(
            config[AWS_CREDS_SECTION]['aws_access_key_id'], 
            config[AWS_CREDS_SECTION]['aws_secret_access_key'], 
            file, 
            BUCKET, 
            key):
        print('  It worked!')
    else:
        print('  The upload failed...')
#}}}

upload(img_path)
exit()


#Eddie's code from here: 
#------------------------

mc = Minecraft.create()
camera =PiCamera()
camera.hflip = True 

mc.postToChat("Hello Eddie")


while True:
    x,y,z,=mc.player.getPos()

    sleep(3)

    if x >=-0.3 and y ==2.0 and z == 1.3:
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
#//EOF
