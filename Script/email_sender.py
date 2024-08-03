import boto3
from botocore.exceptions import ClientError

def send_email(sender, recipient, subject, body_html, charset="UTF-8"):
    client = boto3.client('ses', region_name='YOUR_AWS_REGION')

    try:
        response = client.send_email(
            Destination={'ToAddresses': [recipient]},
            Message={
                'Body': {'Html': {'Charset': charset, 'Data': body_html}},
                'Subject': {'Charset': charset, 'Data': subject},
            },
            Source=sender,
        )
    except ClientError as e:
        print(f"Error sending email: {e.response['Error']['Message']}")
    else:
        print(f"Email sent! Message ID: {response['MessageId']}")