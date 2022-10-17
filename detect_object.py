import boto3

rek_client = boto3.client('rekognition')

with open('test_images/pekingese.jpg', 'rb') as image:
    response = rek_client.detect_labels(Image={'Bytes': image.read()})

labels = response['Labels']
print(f'Found {len(labels)} labels in the image:')
for label in labels:
    name = label['Name']
    confidence = label['Confidence']
    print(f'> Label "{name}" with confidence {confidence:.2f}')