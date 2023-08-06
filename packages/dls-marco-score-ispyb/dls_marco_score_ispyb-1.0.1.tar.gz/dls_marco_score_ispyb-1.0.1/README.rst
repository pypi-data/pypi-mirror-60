dls_marco_score_ispby
=====================

dls_marco_score_ispby ia a script which runs the marco scoring tool
for images passed to it in a list and writes the scores into ispyb database
using ispby API.

There are two requirements for it tow work:

* the connection to the database has to be established
* the images for which the scoring is calculate need to be added to the database table called ispyb.BLSampleImage.


See comments in ticket VMXI-488 for more details.

Once the local database connection is established and the images added
to the database the script can be used as follows:

    import dls_marco_score_ispyb.score as ms

    crystal_images =
    ['imgae1', 'image2']

    ms.run(crystal_images)

Features
--------
Run function takes up to 3 parameters. The first one is the list of image names
(absolute path) and is an obligatory parameter. The second is the path
to the ispyb config file (ispyb_config_path), this is a optional parameter with the default
path to the local host (DEFAULT_ISPYB_CONFIG=dls_marco_score_ispby/config.conf)
The third parameter is the path to the marco model, this is also
an optional parameter, the default value is the path to the model
packaged up with the module (DEFAULT_MODEL_DIR=dls_marco_score_ispby/savedmodel).

Installation
------------
In order to install dls_marco_score_ispyb it do:

    pip install dls_marco_score_ispyb

Note one of the modules used by dls_marco_score_ispyb - tensorflow - is a bit picky in terms of the version of
pip used to install it. Make sure you have the latest version of pip installed.


Contribute
----------
The source code of dls_marco_score_ispyb is on gitlab
- Source Code: https://gitlab.diamond.ac.uk/controls/python3/dls_marco_score_ispyb

Support
-------

If you are having issues, please contact Urszula Neuman at
urszula.neuman@diamond.ac.uk


