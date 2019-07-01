#!/bin/bash
#
#  auth: rbw
#  date: 20190701
#  desc: 
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
BASE_DIR=`cd "${0%/*}/." && pwd`
BUCKET='rbw-pi-camera-uploads-01'
FOLDER_PREFIX='uploads' 

FILE=$1
[ ! -f "$FILE"  ] && echo "ERROR: invalid file on command line" && exit 9
S3_DEST="s3://${BUCKET}/${FOLDER_PREFIX}/$(basename $FILE)"
echo "-----------------------------"
echo "Copying '$FILE' to '$S3_DEST'"
echo "-----------------------------"

aws s3 cp $FILE $S3_DEST

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
echo "Done."
#//EOF
