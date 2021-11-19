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
import sys
import io
import json
from google.cloud import vision
from PIL import Image as PIL_Image
from PIL import ImageOps
from PIL.ExifTags import TAGS
from exif import Image as exif_Image

ADDITION = "./"

def url_wrangler(raw_url, needed_url_type):
    """Update and decide the proper url name convention to be used, basically do we/do not want './' in url string
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
        temp = ADDITION + checked_url
        checked_url = temp
        return checked_url
    else:
        # need to rid the first 2 bytes of the string
        temp = checked_url
        checked_url = temp[2:]
        return checked_url

def image_add_METADATA(my_dict, raw_url):
    # notify user -- check metadata start
    print("\nBegin adding image Metadata.")

    # load image file
    add_METADATA_url = url_wrangler(raw_url, 2)
    with open(f"{add_METADATA_url}", "r+b") as image_file:
        image_file = exif_Image(image_file)

    # update the labels within the metadata tags
    results_JSON_labels = json.dumps(my_dict["labels"])
    image_file.image_description = results_JSON_labels

    # save image file with updates
    with open(f"{add_METADATA_url}", "wb") as image_file_updated:
        image_file_updated.write(image_file.get_file())

    # notify user -- check metadata ended
    print("\nFinished adding image Metadata.")

    # close image file
    image_file_updated.close()

    return None

def image_check_METADATA(raw_url):
    """
    Mostly this function is implemented to be able to check the metadata of a image after del or add
    """
    # notify user -- check metadata start
    print("\nBegin checking current Metadata.")

    # load image file
    check_METADATA_url = url_wrangler(raw_url, 1)
    file_name = os.path.abspath(check_METADATA_url)

    # for basic image metadata extraction, using PIL's Image, not of Google API Vision
    check_image = PIL_Image.open(file_name)
    exifdata = check_image.getexif()
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
    print("\nHere is the current Metadata: \n")
    print(results_JSON)

    # close file (possible issue fixer?)
    check_image.close()

    # notify user -- check metadata end
    print("\nCurrent Metadata has been printed for the image.")

    # return new labels
    return results_JSON

def image_del_METADATA(raw_url):
    # notify user -- delete metadata start
    print("\nBegin deleting Metadata.")

    # load image, wrangle URL if needed
    del_METADATA_url = url_wrangler(raw_url, 1)
    original = PIL_Image.open(del_METADATA_url)
    save_image_path = del_METADATA_url

    # rotate image to correct orientation before removing EXIF data
    original = ImageOps.exif_transpose(original)

    # save image without tags, apparently a simple re-save will clear this... neat!
    stripped = PIL_Image.new(original.mode, original.size)
    stripped.putdata(list(original.getdata()))
    original.close()
    stripped.save(save_image_path)
    stripped.close()

    # notify user -- delete metadata end
    print("\nMetadata has been deleted from image.")

    return None

def image_process_only(raw_url):
    # Imports the Google Cloud client library
    client = vision.ImageAnnotatorClient()

    # load image file
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

    # create the applied Google Vision API outputs for each type
    label_response = client.label_detection(image=image)
    text_response = client.text_detection(image=image)
    logo_response = client.logo_detection(image=image)
    landmark_response = client.landmark_detection(image=image)

    # create dictionary to hold output data
    my_dict = {"labels": []}

    # append any labels
    for label in label_response.label_annotations:
        my_dict["labels"].append(label.description)

    # append any logos
    for logo in logo_response.logo_annotations:
        my_dict["labels"].append(logo.description)

    # append any text
    # counter needed as this would give a string with \n listing all
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

    # capture findings into JSON format
    results_JSON = json.dumps(my_dict)

    # close image file
    image_file.close()

    ### May not need to use for final production, but good to see on stdio ###
    # notify user -- printing new labelings found
    print("\nBegin printing labels found from image.")
    # print out the new labels
    print(results_JSON)
    # notify user -- finished printing new labelings found
    print("\nPrinting labels found from image is finished.")

    # return new labels
    return results_JSON

def image_process_with_save(raw_url):
    # Imports the Google Cloud client library
    client = vision.ImageAnnotatorClient()

    # load image file
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

    # create dictionary to hold output data
    my_dict = {"labels": []}

    # append any labels
    for label in label_response.label_annotations:
        my_dict["labels"].append(label.description)

    # append any logo findings
    for logo in logo_response.logo_annotations:
        my_dict["labels"].append(logo.description)

    # append any text findings
    # counter needed as this would give a string with \n listing all
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

    # convert the created dictionary to JSON format
    results_JSON = json.dumps(my_dict)
    print("\nHere is the current Metadata: \n")
    print(results_JSON)

    # close image file
    image_file.close()

    # add new labelings to the image
    image_add_METADATA(my_dict, raw_url)

    # notify user -- check metadata end
    print("\nCurrent Metadata has been printed for the image.")

    # return new labels
    return results_JSON

if __name__ == '__main__':
    raw_url = sys.argv[1]
