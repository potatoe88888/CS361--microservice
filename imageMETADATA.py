import os
import sys
import io
import json
from google.cloud import vision
from PIL import Image as PIL_Image
from PIL import ImageOps
from PIL.ExifTags import TAGS
from exif import Image as exif_Image

# connect Google environment variable
# USER will need to update this `credential_path with (.json) file with Google creds
credential_path = ""
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

ADDITION = "./"


def image_process_only(raw_url):
    processed_label_findings_dict = get_image_processing_dict(raw_url)

    results_JSON = json.dumps(processed_label_findings_dict)

    print("Begin printing processing results\n" + results_JSON + "\nFinished printing processing results")

    return results_JSON


def image_process_with_save(raw_url):
    processed_label_findings_dict = get_image_processing_dict(raw_url)

    results_JSON = json.dumps(processed_label_findings_dict)

    image_add_METADATA(processed_label_findings_dict, raw_url)

    print("\nNewly processed Metadata labels have been saved within the image.")

    return results_JSON


def image_del_METADATA(raw_url):
    print("\nBegin deleting Metadata.")

    # load image, wrangle URL if needed
    del_METADATA_url = url_wrangler(raw_url, 1)
    original = PIL_Image.open(del_METADATA_url)
    save_image_path = del_METADATA_url

    # rotate image to correct orientation before removing EXIF data
    original = ImageOps.exif_transpose(original)

    # save image without tags (metadata is cleared)
    stripped = PIL_Image.new(original.mode, original.size)
    stripped.putdata(list(original.getdata()))
    original.close()
    stripped.save(save_image_path)
    stripped.close()

    print("\nMetadata has been deleted from image.")

    return None


def url_wrangler(raw_url, needed_url_type):
    """Update and decide the proper url name convention to be used,
    basically do we/do not want './' in url string
    default :: 1 is assumed to be 'current_url_type'
     --> needed_url_type[arg] = 1 --- 'photos/nyc.JPG'
     --> needed_url_type[arg] = 2 --- './photos/nyc.JPG'
    """
    checked_url, current_url_type = raw_url, 1

    # figure out the current labeling within the given raw_url
    if checked_url[0:2] == ADDITION:
        current_url_type = 2

    # decide if the raw_url is fit for the url_type_needed
    if current_url_type == needed_url_type:
        pass
    # update the raw_url (if needed) to the url_type_needed
    elif current_url_type < needed_url_type:
        temp = ADDITION + checked_url
        checked_url = temp
    else:
        # need to rid the first 2 bytes of the string
        temp = checked_url
        checked_url = temp[2:]

    return checked_url


def image_add_METADATA(label_dict, raw_url):
    print("\nBegin adding and saving image Metadata.")

    add_METADATA_url = url_wrangler(raw_url, 2)
    with open(f"{add_METADATA_url}", "r+b") as image_file:
        image_file = exif_Image(image_file)

    # update the labels within the metadata tags
    results_JSON_labels = json.dumps(label_dict["labels"])
    image_file.image_description = results_JSON_labels

    # save image file with metadata updates
    with open(f"{add_METADATA_url}", "wb") as image_file_updated:
        image_file_updated.write(image_file.get_file())

    image_file_updated.close()

    print("\nFinished adding and saving image Metadata.")

    return None


def image_check_METADATA(raw_url):
    """
    Mostly this function is implemented to be able to check/test/debug
    the metadata of a image after del or add
    """
    print("\nBegin checking current image metadata.")

    check_METADATA_url = url_wrangler(raw_url, 1)
    file_name = os.path.abspath(check_METADATA_url)

    # for current/saved metadata extraction, using PIL's Image, not of Google API Vision
    check_image = PIL_Image.open(file_name)
    exifdata = check_image.getexif()

    exifdata_dict = {}
    updated_exifdata_dict = exifdata_extractor(exifdata, exifdata_dict)

    results_JSON = json.dumps(updated_exifdata_dict)

    print("\nCurrent image metadata: \n" + results_JSON + "\nChecking current image metadata is complete.\n")

    check_image.close()

    return results_JSON


def get_image_processing_dict(raw_url):
    load_image_url = url_wrangler(raw_url, 1)
    file_name = os.path.abspath(load_image_url)
    try:
        with io.open(file_name, 'rb') as image_file:
            content = image_file.read()
            image = vision.Image(content=content)
            print("\nBegin processing image:\n" + file_name)
    except:
        print('Error with loading photo')
        exit(1)

    processed_label_findings = {"labels": []}

    # create a Google API vision classed object
    client = vision.ImageAnnotatorClient()

    processed_label_findings = processing_for_labels(processed_label_findings, client, image)
    processed_label_findings = processing_for_logos(processed_label_findings, client, image)
    processed_label_findings = processing_for_landmark(processed_label_findings, client, image)
    processed_label_findings = processing_for_text(processed_label_findings, client, image)

    image_file.close()

    return processed_label_findings


def processing_for_labels(processed_label_findings, client, image):
    label_response = client.label_detection(image=image)

    for label in label_response.label_annotations:
        processed_label_findings["labels"].append(label.description)

    return processed_label_findings


def processing_for_logos(processed_label_findings, client, image):
    logo_response = client.logo_detection(image=image)

    for logo in logo_response.logo_annotations:
        processed_label_findings["labels"].append(logo.description)

    return processed_label_findings


def processing_for_landmark(processed_label_findings, client, image):
    landmark_response = client.landmark_detection(image=image)

    for landmark in landmark_response.landmark_annotations:
        processed_label_findings["labels"].append(landmark.description)

    return processed_label_findings


def processing_for_text(processed_label_findings, client, image):
    text_response = client.text_detection(image=image)

    # counter needed as this would give a string with \n listing all
    counter_to_skip_first = 0
    for text in text_response.text_annotations:
        if counter_to_skip_first != 0:
            processed_label_findings["labels"].append(text.description)
        else:
            counter_to_skip_first += 1

    return processed_label_findings


def exifdata_extractor(exifdata, exifdata_dict):
    for tag_id in exifdata:
        # get the tag name, instead of human unreadable tag id
        tag, data = TAGS.get(tag_id, tag_id), exifdata.get(tag_id)

        # ignore all byte-saved information, it is probably TIFF-type associated
        if isinstance(data, bytes):
            pass
        else:
            exifdata_dict[tag] = data
    return exifdata_dict


if __name__ == '__main__':
    raw_url = sys.argv[1]
