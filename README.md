# microservice
DESCRIPTION ::
This program utilizes Google Vision API and python librarys to add labling to an image and added functionality of deleting the metadata from the said image.

LET'S RUN THIS ::
1. navigate to your directory which will hold this repository through terminal of choice.
2. depending on your python PATH variable set up, you could be using 'python' or 'python3', figure this out before proceeding the user could also house another variable other than these for python running more info? check out ::
      *http://net-informations.com/python/intro/path.htm*
      *https://geek-university.com/python/add-python-to-the-windows-path/*
3. run Flask app, starts up the hosting
      *$python imageMETADATA_broker.py*
      *-- or try --*
      *$python3 imageMETADATA_broker.py*
4. checkout the two url_paths set up for the user, wihthin a current local host, replace [PORT NUMER HERE] with actual desired port number (excluding '[ ]') and add some image path you want, there is a sample set to try out on this repository, for example, replace [INSERT FILE HERE] with photos/nyc_has_text.JPG (excluding '[ ]')
      *http://127.0.0.1:[PORT NUMER HERE]/image_process_only?url=[INSERT FILE HERE]*
      *(ex. http://127.0.0.1:5000/image_process_only?url=photos/nyc_has_text.JPG)*
      *http://127.0.0.1:[PORT NUMER HERE]/image_process_with_save?url=[INSERT FILE HERE]*
      *(ex. http://127.0.0.1:5000/image_process_with_save?url=photos/nyc_has_text.JPG)*
      *http://127.0.0.1:[PORT NUMER HERE]/image_del_METADATA?url=[INSERT FILE HERE]*
      *(ex. http://127.0.0.1:5000/image_del_METADATA?url=photos/nyc_has_text.JPG)*
5. Ability to process image labels and add them as image_description metadata AND ability to delete metadata are now in your hands.   
