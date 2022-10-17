import boto3

client = boto3.client('rekognition')

photo='test_images/pekingese.jpg'
model='arn:aws:rekognition:us-west-2:490776989874:project/dog_breeds/version/dog_breeds.2022-10-16T17.38.46/1665967125295'
min_confidence=20

with open(photo, 'rb') as image:
    response = client.detect_custom_labels(Image={'Bytes': image.read()},
    MinConfidence=min_confidence,
    ProjectVersionArn=model)

labels = response['CustomLabels']
print(f'Found {len(labels)} labels in the image:')
for label in labels:
    name = label['Name']
    confidence = label['Confidence']
    print(f'> Label "{name}" with confidence {confidence:.2f}')