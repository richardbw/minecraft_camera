#!/usr/bin/env python3
#
#  auth: rbw
#  date: 20190503
#  desc: 
#   src from https://stackabuse.com/example-upload-a-file-to-aws-s3-with-boto/
#
# $ aws rekognition detect-labels --image '{"S3Object":{"Bucket":"rbw-pi-camera-uploads-01","Name":"uploads/rbw_passpic.jpg"}}'
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
import os,configparser,sys
import boto
from boto.s3.key import Key

BUCKET                  = 'rbw-pi-camera-uploads-01'
FOLDER_PREFIX           = 'uploads/'  #trailing '/'
AWS_CREDS_FILE          = '~/.aws/credentials'
AWS_CREDS_SECTION       = 'default'

def upload_to_s3(aws_access_key_id, aws_secret_access_key, file, bucket, key, callback=None, md5=None, reduced_redundancy=False, content_type=None):
    """
    Uploads the given file to the AWS S3
    bucket and key specified.

    callback is a function of the form:

    def callback(complete, total)

    The callback should accept two integer parameters,
    the first representing the number of bytes that
    have been successfully transmitted to S3 and the
    second representing the size of the to be transmitted
    object.

    Returns boolean indicating success/failure of upload.
    """
    try:
        size = os.fstat(file.fileno()).st_size
    except:
        # Not all file objects implement fileno(),
        # so we fall back on this
        file.seek(0, os.SEEK_END)
        size = file.tell()

    conn = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
    bucket = conn.get_bucket(bucket, validate=True)
    k = Key(bucket)
    k.key = key
    if content_type:
        k.set_metadata('Content-Type', content_type)
    sent = k.set_contents_from_file(file, cb=callback, md5=md5, reduced_redundancy=reduced_redundancy, rewind=True)

    # Rewind for later use
    file.seek(0)

    if sent == size:
        return True
    return False



def main():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser(AWS_CREDS_FILE))

    if len(sys.argv) != 2:
        raise ValueError("No filename given on cmd line...")

    file = open(sys.argv[1], 'rb+')   #self upload
    key = FOLDER_PREFIX+os.path.basename(file.name)

    print("Uploading to S3> %s:%s" %(BUCKET, key))

    if upload_to_s3(
            config[AWS_CREDS_SECTION]['aws_access_key_id'], 
            config[AWS_CREDS_SECTION]['aws_secret_access_key'], 
            file, 
            BUCKET, 
            key):
        print('It worked!')
    else:
        print('The upload failed...')


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == "__main__": main()
##EOF
