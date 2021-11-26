import imageMETADATA
from flask import Flask, request

app = Flask(__name__)


@app.route("/image_process_only", methods=["GET", "POST"])
def image_process_only():
    """HTTP GET request to get labels off images (only)
    Example of end point: http://127.0.0.1:5000/image_process_only?url=photos/nyc_has_text.JPG
    displays the Google Vision API processing to the user through stdio
    returns JSON data including the Google Vision API processing
     """
    raw_url = request.args.get("url")

    return imageMETADATA.image_process_only(raw_url)

@app.route("/image_process_with_save", methods=["GET", "POST"])
def image_process_with_save():
    """HTTP GET request to get labels off images and save them as metadata exif tags 'image_description'
    Example of end point: http://127.0.0.1:5000/image_process_with_save?url=photos/nyc_has_text.JPG
    displays the Google Vision API processing to the user through stdio
    returns JSON data including the Google Vision API processing
     """
    raw_url = request.args.get("url")

    return imageMETADATA.image_process_with_save(raw_url)


@app.route("/image_del_METADATA", methods=["GET", "POST"])
def image_del_METADATA(debug=0):
    """HTTP GET request to delete all current metadata on the image
    Example of end point: http://127.0.0.1:5000/image_del_METADATA?url=photos/nyc_has_text.JPG
    displays process
    unless using the (.image_check_METADATA) testing, it will not return anything, except this string below.
    defaulted to not show the testing output, checking the metadata of the image, user can enter debug = 1
    as parameter if the need becomes.
    """
    raw_url = request.args.get("url")
    imageMETADATA.image_del_METADATA(raw_url)

    # for testing the image processing saved correctly in environment
    if debug == 1:
        imageMETADATA.image_check_METADATA(raw_url)

    return '''Metadata has been removed from image.'''


if __name__ == '__main__':
    app.run(debug=True)
