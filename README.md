# microservice
This program utilizes Google Vision API and python librarys to execute three tasks:
1. Delete metadata image tags from uploaded image files.
2. Process uploaded image with Google Vision API (labels, landmarks, logos, text gathering) with potential labels.
3. Process and save image with potential labels found using Google Vision API.

## microservice -- Python libraries needed
os, sys, io, json, PIL, exif

## microservice -- how to run (main application should be running)
1. Navigate to your directory which will hold this repository through terminal of choice.
2. Upload your photos into the photo directory.
3. Depending on your python PATH variable set up, you could be using 'python' or 'python3', figure this out before proceeding the user could also house another variable other than these for python running more info? check out [Source 1](http://net-informations.com/python/intro/path.html) and [Source 2](https://geek-university.com/python/add-python-to-the-windows-path/). Run (imageMETEDATA_broker.py).
```  
$python imageMETADATA_broker.py
```  
--or --
```  
$python3 imageMETADATA_broker.py
```  
4. Checkout the three url_paths set up for the user, wihthin a current local host, replace [PORT NUMER HERE] with actual desired port number (excluding '[ ]') and add some image path you want, there is a sample set to try out on this repository, for example, replace [INSERT FILE HERE] with photos/nyc_has_text.JPG (excluding '[ ]')
```
http://127.0.0.1:[PORT NUMER HERE]/image_process_only?url=[INSERT FILE HERE]
```
(ex. http://127.0.0.1:5000/image_process_only?url=photos/nyc_has_text.JPG)
```
http://127.0.0.1:[PORT NUMER HERE]/image_process_with_save?url=[INSERT FILE HERE]
```
(ex. http://127.0.0.1:5000/image_process_with_save?url=photos/nyc_has_text.JPG)
```
http://127.0.0.1:[PORT NUMER HERE]/image_del_METADATA?url=[INSERT FILE HERE]
```
(ex. http://127.0.0.1:5000/image_del_METADATA?url=photos/nyc_has_text.JPG)


5. Review the terminal outputs or see within the browser the JSON output (if applicable to URL). Ability to process image labels and add them as image_description metadata AND ability to delete metadata are now in your hands.
6. Alternatively, you can look at each image file's property before and after the manipulation to confirm the expected output is what you are looking for.

## microservice -- sources

- https://cloud.google.com/vision/docs/labels
- https://cloud.google.com/vision/docs/ocr
- https://cloud.google.com/vision/docs/detecting-faces
- https://cloud.google.com/vision/docs/detecting-landmarks
- https://googleapis.dev/python/vision/latest/vision_v1/image_annotator.html
- https://www.thepythoncode.com/article/extracting-image-metadata-in-python
- https://medium.com/crowdbotics/how-to-build-a-real-time-logo-detection-app-with-react-native-google-vision-api-and-crowdbotics-9ed65fbcd15
- https://docs.python.org/3.8/library/stdtypes.html#mapping-types-dict
- https://github.com/python-pillow/Pillow/issues/4359
- https://www.awaresystems.be/imaging/tiff/tifftags.html
- https://exiftool.org/TagNames/EXIF.html
- https://web.archive.org/web/20190624045241if_/http://www.cipa.jp:80/std/documents/e/DC-008-Translation-2019-E.pdf
