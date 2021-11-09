from __future__ import print_function
import boto3
import json
import os
def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    sns = boto3.client('sns')
    subject=event['Records'][0]['Sns']['Subject']
    if subject is None:
        subject = 'None'
    message = event['Records'][0]['Sns']['Message']
    try:
        msg = json.loads(message)
        message = json.dumps(msg, indent=4)
        if 'detail-type' in msg:
          subject = msg['detail-type']
    except:
        print('Not json')
    response = sns.publish(
        TopicArn=os.environ.get('sns_arn'),
        Subject=subject,
        Message=message
    )
    print(response)
    return response