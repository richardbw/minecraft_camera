#
#  auth: rbw
#  date: 20190503
#  desc: 
# .  https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import os
import json
import boto3
from contextlib import closing
import logging                   #
logger = logging.getLogger()     # https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
logger.setLevel(logging.DEBUG)   #

def lambda_handler(event, context):
    logger.debug("Start rbw-pi-trigger-ml-generate-mp3")
    logger.debug("Received: event: %s, context: %s" %(event, context))

    gen_mp3(
        event['Records'][0]['body'],
        event["Records"][0]["messageId"])

    logger.debug(" /End rbw-pi-trigger-ml-generate-mp3")



#   https://aws.amazon.com/blogs/machine-learning/build-your-own-text-to-speech-applications-with-amazon-polly/:
def gen_mp3(text,messageId):
    logger.debug("Turning [%s] into mp3, as [%s]" %(text, os.environ['POLLY_VOICEID']) )

    polly = boto3.client('polly')
    response = polly.synthesize_speech(
        OutputFormat='mp3',
        Text = text,
        VoiceId = os.environ['POLLY_VOICEID']
    )
    #Save the audio stream returned by Amazon Polly on Lambda's temp 
    # directory. If there are multiple text blocks, the audio stream
    # will be combined into a single file.
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = os.path.join("/tmp/", messageId)
            with open(output, "ab") as file:
                file.write(stream.read())

    s3_mp3_key = os.environ['S3_MP3_OUTPUT_KEYPREF']+messageId + ".mp3"
    logger.debug("Uploading to S3[%s][%s]" %(os.environ['S3_MP3_OUTPUT_BUCKET'], s3_mp3_key) )
    s3 = boto3.client('s3')
    s3.upload_file('/tmp/' + messageId, 
        os.environ['S3_MP3_OUTPUT_BUCKET'],
        s3_mp3_key) 

    logger.debug(" / Done Uploading ")

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#//EOF