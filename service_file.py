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
# https://www.awaresystems.be/imaging/tiff/tifftags.html
# https://exiftool.org/TagNames/EXIF.html
# https://web.archive.org/web/20190624045241if_/http://www.cipa.jp:80/std/documents/e/DC-008-Translation-2019-E.pdf
#            (^ noted that the Dec'270' TagID value can be used for 'Image description', which will be where labels go)

import os
import io
import json
import requests
from google.cloud import vision
from PIL import Image as PIL_Image
from PIL import ImageOps
from PIL.ExifTags import TAGS
from exif import Image as exif_Image


def url_wrangler(raw_url, needed_url_type):
    """Update and decide the proper url name convention to be used, bascially do we/do not want './' in url string
    needed_url_type[arg] = 1 --- 'photos/nyc.JPG'
    needed_url_type[arg] = 2 --- './photos/nyc.JPG'
    """
    checked_url = raw_url
    current_url_type = 1

    # figure out the current labeling within the given raw_url
    if checked_url[0:2] == './':
        current_url_type = 2

    # decide if the raw_url is fit for the url_type_needed
    if current_url_type == needed_url_type:
        return checked_url

    # update the raw_url (if needed) to the url_type_needed
    elif current_url_type < needed_url_type:
        # need to add './' to the string
        addition = "./"
        temp = addition + checked_url
        checked_url = temp
        return checked_url
    else:
        # need to rid the first 2 bytes of the string
        temp = checked_url
        checked_url = temp[2:]
        return checked_url

def image_add_METADATA(my_dict, raw_url):
    # load image
    add_METADATA_url = url_wrangler(raw_url, 2)
    with open(f"{add_METADATA_url}", "rb") as image_file:
        image_file = exif_Image(image_file)

    # update the labels within the metadata tags
    results_JSON_labels = json.dumps(my_dict["labels"])
    image_file.image_description = str(results_JSON_labels)

    # save image with updates
    with open(f"{add_METADATA_url}", "wb") as image_file_updated:
        image_file_updated.write(image_file.get_file())

def image_check_METADATA(raw_url):
    # load image
    check_METADATA_url = url_wrangler(raw_url, 1)
    file_name = os.path.abspath(check_METADATA_url)

    # for basic image metadata extraction, using PIL's Image, not of Google API Vision
    exifdata = PIL_Image.open(file_name).getexif()
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

    # convert the created dictionary to JSON format
    results_JSON = json.dumps(another_dict)
    return results_JSON

def image_del_METADATA(raw_url):
    # load image
    del_METADATA_url = url_wrangler(raw_url, 1)
    original = PIL_Image.open(del_METADATA_url)
    new_image_path = del_METADATA_url

    # rotate image to correct orientation before removing EXIF data
    original = ImageOps.exif_transpose(original)

    # save image without tags, apparently a simple re-save will clear this... neat!
    stripped = PIL_Image.new(original.mode, original.size)
    stripped.putdata(list(original.getdata()))
    stripped.save(new_image_path)

def image_process(raw_url):

    # Imports the Google Cloud client library
    client = vision.ImageAnnotatorClient()

    # load image
    load_image_url = url_wrangler(raw_url, 1)
    file_name = os.path.abspath(load_image_url)
    try:
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
            image = vision.Image(content=content)
            print("\n begin processing image:")
            print(file_name)
    except:
        print('Error with loading photo')
        exit(1)

    # create the applied Vision outputs for each type
    label_response = client.label_detection(image=image)
    text_response = client.text_detection(image=image)
    logo_response = client.logo_detection(image=image)
    landmark_response = client.landmark_detection(image=image)
    face_response = client.face_detection(image=image)

    # create dictionary to hold output data
    my_dict = {"labels": [], "current_image_metadata":[]}

    # append any labels
    for label in label_response.label_annotations:
        my_dict["labels"].append(label.description)

    # append any logo findings
    for logo in logo_response.logo_annotations:
        my_dict["labels"].append(logo.description)

    # append any text findings, counter needed as this would give a string with \n listing all
    counter_to_skip_first = 0
    for text in text_response.text_annotations:
        if counter_to_skip_first == 0:
            counter_to_skip_first += 1
            continue
        else:
            my_dict["labels"].append(text.description)

    # append any landmarks
    for landmark in landmark_response.landmark_annotations:
        my_dict["labels"].append(landmark.description)

    # append any emotions found within faces of people
    # emotions/sentiments:: surprise, joy, anger, neutral
    for face in face_response.face_annotations:
        count_for_neutral = 0

        likelihood1 = vision.Likelihood(face.surprise_likelihood)
        if likelihood1.name == "LIKELY":
            my_dict["labels"].append("Face surprised")
        elif likelihood1.name == "VERY_UNLIKELY":
            my_dict["labels"].append("Face not surprised")
            count_for_neutral += 1
        else:
            continue

        likelihood2 = vision.Likelihood(face.joy_likelihood)
        if likelihood2.name == "LIKELY":
            my_dict["labels"].append("Face has joy")
        elif likelihood2.name == "VERY_UNLIKELY":
            my_dict["labels"].append("Face does not has joy")
            count_for_neutral += 1
        else:
            continue

        likelihood3 = vision.Likelihood(face.anger_likelihood)
        if likelihood3.name == "LIKELY":
            my_dict["labels"].append("Face is angered")
        elif likelihood3.name == "VERY_UNLIKELY":
            my_dict["labels"].append("Face is not angered")
            count_for_neutral += 1
        else:
            continue

        if count_for_neutral == 3:
            my_dict["labels"].append("Face is neutral")
        else:
            continue

    # for basic image metadata extraction, using PIL's Image, not of Google API Vision
    exifdata = PIL_Image.open(file_name).getexif()
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
    #results_JSON = json.dumps(my_dict)
    #print("\nHere is the processed data: \n")
    #print(results_JSON)

    # update the image with the new labels found
    image_add_METADATA(my_dict, raw_url)

    # notify user
    print("\nMetadata has been updated with new processed labels.")
