### SOURCES
# https://cloud.google.com/vision/docs/labels
# https://cloud.google.com/vision/docs/ocr
# https://cloud.google.com/vision/docs/detecting-faces
# https://cloud.google.com/vision/docs/detecting-landmarks
# https://googleapis.dev/python/vision/latest/vision_v1/image_annotator.html
# https://www.thepythoncode.com/article/extracting-image-metadata-in-python
# https://medium.com/crowdbotics/how-to-build-a-real-time-logo-detection-app-with-react-native-google-vision-api-and-crowdbotics-9ed65fbcd15
# https://docs.python.org/3.8/library/stdtypes.html#mapping-types-dict
# https://github.com/python-pillow/Pillow/issues/4359

from io import BytesIO
import json
import requests
from google.cloud import vision
from PIL import Image
from PIL.ExifTags import TAGS

image_uri = 'https://www.thebrooklynnomad.com/wp-content/uploads/2021/01/Museums-lighten-up-1024x683.jpg?x57786'

# Imports the Google Cloud client library
client = vision.ImageAnnotatorClient()

image = vision.Image()
image.source.image_uri = image_uri

# create the applied Vision outputs for each type
label_response = client.label_detection(image=image)
text_response = client.text_detection(image=image)
logo_response = client.logo_detection(image=image)
landmark_response = client.landmark_detection(image=image)
face_response = client.face_detection(image=image)

# create dictionary to hold output data
my_dict = {"labels": [], "logos": [], "text": [], "landmark": [], "sentiment": []}

# append any labels
for label in label_response.label_annotations:
    my_dict["labels"].append(label.description)

# append any logo findings
for logo in logo_response.logo_annotations:
    my_dict["logos"].append(logo.description)

# append any text findings, counter needed as this would give a string with \n listing all
counter_to_skip_first = 0
for text in text_response.text_annotations:
    if counter_to_skip_first == 0:
        counter_to_skip_first += 1
        continue
    else:
        my_dict["text"].append(text.description)

# append any landmarks found
for landmark in landmark_response.landmark_annotations:
    my_dict["landmark"].append(landmark.description)

# append any emotions found within faces of people
# emotions/sentiments:: surprise, joy, anger, neutral
for face in face_response.face_annotations:
    count_for_neutral = 0

    likelihood1 = vision.Likelihood(face.surprise_likelihood)
    if likelihood1.name == "LIKELY":
        my_dict["sentiment"].append("Face surprised")
    elif likelihood1.name == "VERY_UNLIKELY":
        my_dict["sentiment"].append("Face not surprised")
        count_for_neutral += 1
    else:
        continue

    likelihood2 = vision.Likelihood(face.joy_likelihood)
    if likelihood2.name == "LIKELY":
        my_dict["sentiment"].append("Face has joy")
    elif likelihood2.name == "VERY_UNLIKELY":
        my_dict["sentiment"].append("Face does has joy")
        count_for_neutral += 1
    else:
        continue

    likelihood3 = vision.Likelihood(face.anger_likelihood)
    if likelihood3.name == "LIKELY":
        my_dict["sentiment"].append("Face is angered")
    elif likelihood3.name == "VERY_UNLIKELY":
        my_dict["sentiment"].append("Face is not angered")
        count_for_neutral += 1
    else:
        continue

    if count_for_neutral == 3:
        my_dict["sentiment"].append("Face is neutral")
    else:
        continue

# for basic image metadata extraction, using PIL's Image, not of Google API Vision
response = requests.get(image_uri)
exifdata = Image.open(BytesIO(response.content)).getexif()

#exifdata = Image.open(image).getexif()
another_dict = {}

# iterating over all EXIF data fields
for tag_id in exifdata:
    # get the tag name, instead of human unreadable tag id
    tag = TAGS.get(tag_id, tag_id)
    data = exifdata.get(tag_id)

    # ignore all byte-saved information, it is probably TIFF-type associated
    if isinstance(data, bytes):
        pass
    else:
        # build out a dictionary for this data
        another_dict[tag] = data

# add this dictionary to the main dictionary of program
my_dict["current_image_metadata"] = another_dict

# convert the created dictionary to JSON format
results_JSON = json.dumps(my_dict)
print(results_JSON)
