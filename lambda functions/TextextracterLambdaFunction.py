import boto3
import base64
from urllib.parse import urlparse

def parse_s3_url(s3_url):
    parsed_url = urlparse(s3_url)
    bucket_name = "textractimagebucket1"
    object_key = parsed_url.path.lstrip('/')
    return bucket_name, object_key

def download_image_from_s3(bucket_name, object_key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    image_bytes = response['Body'].read()
    return image_bytes

def lambda_handler(event, context):
    s3_url = event['imageS3Url']
    email = event['email']
    bucket_name, object_key = parse_s3_url(s3_url)
    image_bytes = download_image_from_s3(bucket_name, object_key)

    textract_client = boto3.client('textract')
    sns_client = boto3.client('sns')

    response = textract_client.detect_document_text(
        Document={
            'Bytes': image_bytes
        }
    )

    extracted_text = ''
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            extracted_text += item['Text'] + '\n'

    sns_client.publish(
        TopicArn='arn:aws:sns:us-east-2:730335646873:topic123',
        Message=extracted_text,
        Subject='Extracted Text from Image',
        MessageAttributes={
            'email': {
                'DataType': 'String',
                'StringValue': email
            }
        }
    )

    return {
        'statusCode': 200,
        'body': 'Text extraction and email notification process completed successfully.'
    }

# input

# policy1
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": "sns:Publish",
#             "Resource": "arn:aws:sns:us-east-2:730335646873:topic123"
#         }
#     ]
# }
# policy2
# {
#     "Version": "2012-10-17",
#     "Statement": [
#         {
#             "Effect": "Allow",
#             "Action": "s3:GetObject",
#             "Resource": "arn:aws:s3:::*/*"
#         }
#     ]
# }