import io
import os

from google.cloud import vision
from google.cloud.vision import types
import google.auth


#credentials, projectId = google.auth.default()
#creds = '/Users/Steven/PycharmProjects/HQ/My-Project-52127-72370db5e401.json'

#client = vision.ImageAnnotatorClient(credentials=creds)
client = vision.ImageAnnotatorClient()

file_name = os.path.join(os.path.dirname(__file__),'IMG_1661.PNG')

# Loads the image into memory
with io.open(file_name, 'rb') as image_file:
    content = image_file.read()

image = types.Image(content=content)

print('image is: ', image)

# Performs label detection on the image file

response = client.label_detection(image=image)
labels = response.label_annotations

print('Labels:')
for label in labels:
    print(label.description)