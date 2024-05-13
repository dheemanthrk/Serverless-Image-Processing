import boto3
import base64
from urllib.parse import urlparse

def parse_s3_url(s3_url):
    # Parse the S3 URL to extract bucket name and object key
    parsed_url = urlparse(s3_url)
    bucket_name = "textractimagebucket1"
    object_key = parsed_url.path.lstrip('/')
    print(bucket_name)
    print(object_key)
    return bucket_name, object_key

def download_image_from_s3(bucket_name, object_key):
    # Download the image from S3
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    image_bytes = response['Body'].read()
    return image_bytes

def lambda_handler(event, context):
    s3_url = event['imageS3Url']
    email = event['email']
    bucket_name, object_key = parse_s3_url(s3_url)
    image_bytes = download_image_from_s3(bucket_name, object_key)
    
    rekognition_client = boto3.client('rekognition')
    sns_client = boto3.client('sns')

    response = rekognition_client.detect_labels(
        Image={
            'Bytes': image_bytes
        }
    )

    labels = [label['Name'] for label in response['Labels']]

    sns_client.publish(
        TopicArn='arn:aws:sns:us-east-2:730335646873:topic123',
        Message="Detected labels: {}".format(", ".join(labels)),
        Subject='Detected Labels from Image',
        MessageAttributes={
            'email': {
                'DataType': 'String',
                'StringValue': email
            }
        }
    )

    return {
        'statusCode': 200,
        'body': 'Label detection and email notification process completed successfully.'
    }

input

policy1
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::*/*"
        }
    ]
}
policy2
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": "arn:aws:sns:us-east-2:730335646873:topic123"
        }
    ]
}