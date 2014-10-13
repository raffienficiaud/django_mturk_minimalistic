Django Mechanical Turk External Question minimalistic example
=============================================================

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
