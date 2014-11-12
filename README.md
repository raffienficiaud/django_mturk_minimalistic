Django Amazon Mechanical Turk External Question minimalistic example
====================================================================

This is a super small project on how to use Django to show and manage external question for the Amazon Mechanical Turk. 

Why external questions?
-----------------------
Amazon Mechanical Turk (AMT) comes with a lot of possibilities. However sometimes you just need to do something really hacky on the Javascript side (interactive image segmentation), and the provided built-in functionalities are not addressing your needs. Hopefully, AMT provides the External Question possibility: the question posted on the AMT market is just a redirection to a particular URL you own, with some metadata. 

In this setup, you can show whatever you want to the end user, interact with him much better. The only limit are your creativity, your skills and your browser.

Why Django?
-----------
Django is a super Framework in Python for doing web applications. It contains a database backend, a nice template for creating the HMTL files shown to the user, and a nice logic for transforming the requested URLs (the one from the AMT) into functions.

In this project, we simply use the database backend to store the information that will be shown to the user. We also store in the database how this information is linked to the AMT (the question instances or "hits", the results, etc).

Dependencies
------------
The only dependencies are

* django
* boto

What does this application?
---------------------------

* The "app" starts by parsing a directory and retrieves all the images. These images are added into the database as primary source of information for creating the questions to the Amazon workers. 
* Then, the "HITS" are created. The HITS are external questions showing a specific URL on our app server. This URL is constructed in such a way that the image from which the hit is created is shown to the user. The HITS are also stored into the database to better track what is going on on the Amazon side.
* Finally, the results are taken back from Amazon. The content of the result is also stored into the database and bound to the HIT and the image on which it operates. 

How to use the app?
-------------------
All these 3 commands are available from the command line, basically by doing
```
python manage.py command [options]
```

These commands are, respecitively to their description above:

* `add_picture_folder`: a folder containing the pictures should be specified. A picture is not added twice in the database.
* `create_hits`: the HITS are created on the Amazon side. For this to run properly, a proper credential should be set in the function `get_connection` in the file `boto1\management\commands\create_hits.py`. The base URL of the server (such as `https://my.app.domain/my/app`) should be provided to the command
* `retrieve_results`: the results are retrieved from Amazon. Each new result is added in the database. 

Any other configuration?
------------------------
The application is functional in the code base. A couple of changes should be done in order to be able to deploy the app in a production server. Note that even for the sandbox, the HTTPS protocol should be used, which is hard to handle from Django directly.

The real deployment should be done behind a real http server, and using HTTPS protocol. We refer to the numerous documentation for that, which depends on your system and the front server. Also the static and media folders should be set properly, and the `Debug` value in the `settings.py` should be set to `False`.
In the `settings.py` file also is set whether the app should be using the sandbox of the Amazon Mechanical Turk or the production server. The default in the code is the use of the sandbox.
