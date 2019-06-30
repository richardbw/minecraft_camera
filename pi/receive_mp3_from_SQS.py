#!/usr/bin/env python3
#
#  auth: rbw
#  date: 20190508
#  desc: 
#	https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import boto3,re,time,sys,os
import pygame

import coloredlogs, logging                     #
log = logging.getLogger(__name__)               # https://coloredlogs.readthedocs.io/en/latest/readme.html#usage
coloredlogs.install(level='DEBUG', logger=log)  #  

queue_url = 'https://sqs.us-east-1.amazonaws.com/688142363120/rbw-pi-ml-face-recog-generated-mp3'

REGEX_GENERATED_MP3_STR = re.compile(r"MP3> ([a-z0-9-]+):([a-z0-9-\/\.]+.mp3)")
POLL_SLEEP=5


# Create SQS client
sqs = boto3.client('sqs')
s3  = boto3.client('s3')



def process_response(response): #{{{
    if not "Messages" in response:
        log.debug("No messages picked up.  Looping")
        return

    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']
    message_body = message['Body']

    log.debug("Message handle: %s, body: %s" %(receipt_handle, message_body))

    try:
        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

        log.info('Deleted message: %s' % receipt_handle)

        match_groups = REGEX_GENERATED_MP3_STR.search(message_body)
        s3_bucket_name = match_groups.group(1)
        s3_bucket_key  = match_groups.group(2)

        log.debug("s3_bucket_name : |%s|" % s3_bucket_name)
        log.debug("s3_bucket_key  : |%s|" % s3_bucket_key )

        with open(s3_bucket_key, 'wb+') as data:
            s3.download_fileobj(s3_bucket_name, s3_bucket_key, data)

        log.info ("Saved          : " + s3_bucket_key )
        return s3_bucket_key
    except:  
        log.exception("Unexpected exception occurred! ")

    return None
#}}}


def play_mp3(mp3_filename):  #{{{
    VOLUME = 5000
    cmdline = 'mpg321 -g %s %s &'  % (VOLUME, mp3_filename)
    log.debug("Will execute: "+cmdline)
    os.system(cmdline)

    log.debug("Sound play done.")
#}}}


def main(): #{{{
    log.info("Starting "+sys.argv[0])
    log.debug("Will poll logs at: "+queue_url)
    log.info("Starting to listen  (^C to stop)...")


    try:

        while True:
            # Receive message from SQS queue
            response = sqs.receive_message(
                QueueUrl=queue_url
            )

            log.debug('Received: %s' % response)

            mp3_filename = process_response(response)
            if mp3_filename is not None:  
                play_mp3(mp3_filename)
            time.sleep( POLL_SLEEP )

    except KeyboardInterrupt:  
        log.warning("Caught ^C, and exiting")
    except:  
        log.exception("Unexpected exception occurred! ")

#}}}
    


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__": main()
#//EOF
