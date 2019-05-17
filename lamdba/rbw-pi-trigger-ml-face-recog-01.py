#
#  auth: rbw
#  date: 20190503
#  desc: 
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import os
import json
import boto3
import logging                      #
log = logging.getLogger(__name__)   # https://docs.aws.amazon.com/lambda/latest/dg/python-logging.html
log.setLevel(logging.DEBUG)         # https://stackoverflow.com/a/8269542

def lambda_handler(event, context):
    log.debug("RBW> Start rbw-pi-trigger-ml-face-recog-01--------------------------------------------------")
    log.debug("RBW> Received: event: %s, context: %s" %(event, context))
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    filename = event['Records'][0]['s3']['object']['key']
    
    #call_rekognition(bucket, filename)
    
    push_to_generate_mp3(
        face_compare(bucket, filename)
    )
    
    log.debug("RBW>  /End rbw-pi-trigger-ml-face-recog-01")



def call_rekognition(bucket='bucket', filename='input.jpg'):
    log.debug("RBW>  ===== Start call_rekognition(bucket=%s', filename=%s)" %(bucket, filename))
    
    client=boto3.client('rekognition')
    response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':filename}})

    print('RBW> Detected labels for ' + filename)    
    for label in response['Labels']:
        log.debug('-->'+label['Name'] + ' : ' + str(label['Confidence']))
    
    log.debug("RBW>  /End call_rekognition()")
    

def face_compare(bucket='bucket', filename='input.jpg'):   
    log.debug("RBW> ==== Start face_compare(bucket=%s', filename=%s)" %(bucket, filename))
    
    ret_str = ""
    
    client=boto3.client('rekognition')
    for name in os.environ['REKOG_NAME_LIST'].split(','):
        ref_img = os.environ['REKOG_S3_KEYPREF'] + name + '.jpg'
        log.debug("RBW> Checking similarity with '%s'" % (ref_img))

        response = client.compare_faces(SimilarityThreshold=70,
                    SourceImage={'S3Object':{'Bucket':os.environ['REKOG_S3_BUCKET'] ,'Name':ref_img}},
                    TargetImage={'S3Object':{'Bucket':bucket                        ,'Name':filename}})
        log.debug("RBW> Similarity response |%s|" % (response))

        for faceMatch in response['FaceMatches']:
            position = faceMatch['Face']['BoundingBox']
            confidence = str(faceMatch['Face']['Confidence'])
            log.debug('RBW> The face at ' +
                str(position['Left']) + ' ' +
                str(position['Top']) +
                ' matches with ' + confidence + '% confidence')
            ret_str += name + " is in the picture."

    if len(ret_str) == 0:  ret_str = "No faces recognised"
    log.debug("RBW>  /End face_compare(): "+ret_str)
    return ret_str


# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html
def push_to_generate_mp3(text="nothing to say"):
    log.debug("RBW> ===== Start push_to_generate_mp3(text=%s')" %(text))
    
    queue_url = os.environ['SQS_URL_GENERATEMP3']
    log.debug("RBW> Pushing to: %s')" %(queue_url))
    
    sqs = boto3.client('sqs')
    
    response = sqs.send_message(
        QueueUrl=queue_url,
        DelaySeconds=10,
        MessageBody=(text)
    )

    log.debug("RBW>  Message sent.  ID: "+response['MessageId'])
    log.debug("RBW>  /End push_to_generate_mp3()")


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#//EOF
