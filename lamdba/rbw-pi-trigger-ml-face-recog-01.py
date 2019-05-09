#
#  auth: rbw
#  date: 20190503
#  desc: 
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import os
import json
import boto3
import logging                   #
logger = logging.getLogger()     # https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
logger.setLevel(logging.DEBUG)   #

def lambda_handler(event, context):
    logger.debug("Start rbw-pi-trigger-ml-face-recog-01")
    logger.debug("Received: event: %s, context: %s" %(event, context))
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    filename = event['Records'][0]['s3']['object']['key']
    
    #call_rekognition(bucket, filename)
    face_compare(bucket, filename)
    
    #push_to_generate_mp3("London calling to the faraway towns.  Now war is declared and battle come down")
    
    logger.debug(" /End rbw-pi-trigger-ml-face-recog-01")



def call_rekognition(bucket='bucket', filename='input.jpg'):
    logger.debug("Start call_rekognition(bucket=%s', filename=%s)" %(bucket, filename))
    
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':filename}})

    print('Detected labels for ' + filename)    
    for label in response['Labels']:
        print (label['Name'] + ' : ' + str(label['Confidence']))
    
    logger.debug(" /End call_rekognition()")
    

 def face_compare(bucket='bucket', filename='input.jpg'):   
    logger.debug("Start face_compare(bucket=%s', filename=%s)" %(bucket, filename))
    
    client=boto3.client('rekognition')
    for name in os.environ['REKOG_NAME_LIST'].split(','):
        ref_img = os.environ['REKOG_S3_KEYPREF'] + name
        logger.debug("Checking similarity with '%s'" % (ref_img))

        response = client.compare_faces(SimilarityThreshold=70,
                    SourceImage={'S3Object':{'Bucket':os.environ['REKOG_S3_BUCKET'] ,'Name':ref_img}},
                    TargetImage={'S3Object':{'Bucket':bucket                        ,'Name':filename}})
        logger.debug("Similarity response |%s|" % (response))

        for faceMatch in response['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            confidence = str(faceMatch['Face']['Confidence'])
            logger.debug('The face at ' +
                str(position['Left']) + ' ' +
                str(position['Top']) +
                ' matches with ' + confidence + '% confidence')

    logger.debug(" /End face_compare()")


# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html
def push_to_generate_mp3(text="nothing to say"):
    logger.debug("Start push_to_generate_mp3(text=%s')" %(text))
    
    queue_url = os.environ['SQS_URL_GENERATEMP3']
    logger.debug("Pushing to: %s')" %(queue_url))
    
    sqs = boto3.client('sqs')
    
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=(text)
    )

    logger.debug(" Message sent.  ID: "+response['MessageId'])
    logger.debug(" /End push_to_generate_mp3()")


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#//EOF
