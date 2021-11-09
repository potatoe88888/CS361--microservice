import imageMETADATA
from flask import Flask, request

app = Flask(__name__)


@app.route("/image_process", methods=["GET", "POST"])
def image_process():
    """HTTP GET request to get labels off images and save them as metadata exif tags 'image_description'
    Example of end point: http://127.0.0.1:5000/image_process?url=photos/nyc_has_text.JPG
    gives JSON confirmation of completed request back to requester
     """
    raw_url = request.args.get("url")
    imageMETADATA.image_process(raw_url)

    # for testing the image processing saved correctly in environment
    imageMETADATA.image_check_METADATA(raw_url)

    return '''Successful image processing and adding this data within the image's metadata'''


@app.route("/image_del_METADATA", methods=["GET", "POST"])
def image_del_METADATA():
    """HTTP GET request to delete all current metadata on the image
    Example of end point: http://127.0.0.1:5000/image_del_METADATA?url=photos/nyc_has_text.JPG
    gives JSON confirmation of completed request back to requester
    """
    raw_url = request.args.get("url")
    imageMETADATA.image_del_METADATA(raw_url)

    # for testing the image processing saved correctly in environment
    imageMETADATA.image_check_METADATA(raw_url)

    return '''Successful deletion image's metadata'''


if __name__ == '__main__':
    app.run(debug=True)