import os

import ispyb

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # mute the warnings
import tensorflow as tf

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)  # mute warnings related to v1 API
# see https://stackoverflow.com/questions/35911252/disable-tensorflow-debugging-information
# for warning suppression

package_dir, _ = os.path.split(__file__)
DEFAULT_MODEL_DIR = os.path.join(package_dir, "savedmodel")
DEFAULT_ISPYB_CONFIG = os.path.join(package_dir, "config.cfg")


def run(crystal_images, ispyb_config_path=DEFAULT_ISPYB_CONFIG, model_path=DEFAULT_MODEL_DIR):
    def load_images(file_list):
        for i in file_list:
            files = open(i, 'rb')
            yield {"image_bytes": [files.read()]}, i

    predictor = tf.contrib.predictor.from_saved_model(model_path)
    ispyb_classes = ["crystal", "precipitant", "clear", "other"]
    ispyb_score_schema = "MARCO"
    with ispyb.open(ispyb_config_path) as conn:
        mxprocessing = conn.mx_processing
        for data, name in load_images(crystal_images):
            results = predictor(data)
            vals = results['scores'][0]  # returns values for "crystal", "precipitant", "clear", "other"
            for i, cl in enumerate(ispyb_classes):
                mxprocessing.upsert_sample_image_auto_score(name, ispyb_score_schema, cl, str(vals[i]))
