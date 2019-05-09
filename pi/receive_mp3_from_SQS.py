#!/usr/bin/env python3
#
#  auth: rbw
#  date: 20190508
#  desc: 
#	https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-sending-receiving-msgs.html
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import boto3,re

REGEX_GENERATED_MP3_STR = re.compile(r"MP3> ([a-z0-9-]+):([a-z0-9-\/\.]+.mp3)")

# Create SQS client
sqs = boto3.client('sqs')

queue_url = 'https://sqs.us-east-1.amazonaws.com/688142363120/rbw-pi-ml-face-recog-generated-mp3'

# Receive message from SQS queue
response = sqs.receive_message(
    QueueUrl=queue_url,
    AttributeNames=[ 'SentTimestamp' ],
    MaxNumberOfMessages=1,
    MessageAttributeNames=[ 'All' ],
    VisibilityTimeout=0,
    WaitTimeSeconds=0
)
print('Received: %s' % response)

if not "Messages" in response:
    print("No messages picked up.  Exiting")
    exit(28)

message = response['Messages'][0]
receipt_handle = message['ReceiptHandle']

# Delete received message from queue
sqs.delete_message(
    QueueUrl=queue_url,
    ReceiptHandle=receipt_handle
)

print('Deleted message: %s' % receipt_handle)

match_groups = REGEX_GENERATED_MP3_STR.search(message['Body']['Message'])
s3_bucket_name = match_groups.group(1)
s3_bucket_key  = match_groups.group(2)

print("s3_bucket_name" + s3_bucket_name)
print("s3_bucket_key " + s3_bucket_key )

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#//EOF
