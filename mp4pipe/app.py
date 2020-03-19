import os
from os import getenv
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS, cross_origin
import logging
import boto3

TMP_DIR = '/'

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['TMP_DIR'] = TMP_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('S3 Upload')

region_name = getenv('AWS_REGION')

session = boto3.Session(
   aws_access_key_id = getenv('AWS_ACCESS_KEY_ID'),
   aws_secret_access_key = getenv('AWS_ACCESS_KEY_SECRET'),
)

s3 = session.resource('s3')
bucketname = getenv('AWS_S3_UPLOAD')

@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
      file = request.files['file']
      filename = secure_filename(file.filename)
      target=os.path.join(TMP_DIR,'tmp')
      if not os.path.isdir(target):
          os.mkdir(target)
      destination="/".join([target, filename])
      file.save(destination)
      
      file_path = os.path.join(target, filename)
      data = open(file_path, 'rb')
      s3.Bucket(bucketname).put_object(ACL='public-read', Key=filename, Body=data)

      os.remove(file_path)
      return 'file uploaded successfully'


@app.route('/hello')
def hello():
    return 'hello world'


if __name__ == "__main__":
    app.run(debug=True,host="0.0.0.0",use_reloader=False)

CORS(app, expose_headers='Authorization')