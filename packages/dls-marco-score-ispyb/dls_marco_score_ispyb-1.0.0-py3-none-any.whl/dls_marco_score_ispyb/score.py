import ispyb
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # get rid of the warnings
import tensorflow as tf

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR) # get rid of warnings related to v1 API

# see https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
# for warning suppression

def run(crystal_images, ispb_config_path='config.cfg', model_path='savedmodel'):
    # generator
    # the default path works for the packaged version
    def load_images(file_list):
        for i in file_list:
            files = open(i, 'rb')
            yield {"image_bytes": [files.read()]}, i

    predictor = tf.contrib.predictor.from_saved_model(model_path)
    ispyb_classes = ["crystal", "precipitant", "clear", "other"]
    ispyb_score_schema = "MARCO"
    with ispyb.open(ispb_config_path) as conn:
        mxprocessing = conn.mx_processing
        for data, name in load_images(crystal_images):
            results = predictor(data)
            vals = results['scores'][0] # returns values for "crystal", "precipitant", "clear", "other"
            for i, cl in enumerate(ispyb_classes):
                mxprocessing.upsert_sample_image_auto_score(name,ispyb_score_schema,cl,str(vals[i]))

