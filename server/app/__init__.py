import logging
import os
import subprocess
from pathlib import Path

import numpy

from flask import Flask, jsonify, send_file, request

from app.constant.http.error import SERVER_OK, SERVER_OK_MESSAGE
from app.utils.he_ew import HomomorphicEncryptionEW

from config.flask_config import PARAMS_SAVE_FILE, MODEL_SAVE_FILE, CIPHERTEXT_SAVE_FILE, LIBRARY_EXECUTABLE, basedir, \
    APP_ROOT
from model import create_model, num_classes
from tensorflow import keras


def create_app(test_config=None, private_key=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'launcher.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Setup HE library
    if private_key is None:
        executable_path = Path(APP_ROOT).parent.parent.joinpath(LIBRARY_EXECUTABLE)
        logging.debug(executable_path.absolute())
        ip = "0\n1\n1 1\n".encode('utf-8')
        process = subprocess.run([str(executable_path.absolute()), "encrypt"],
                                 input=ip,
                                 stdout=subprocess.PIPE)
        process_outputs = process.stdout.decode('utf-8').split()
        # logging.warning(process_outputs)
        private_key = process_outputs[1]
        logging.info("Private key created successfully!")
        # logging.debug(f"Private key is {private_key}")
        he_lib = HomomorphicEncryptionEW(
            private_key=private_key,
        )

    model = create_model()
    # Load model
    if os.path.exists(MODEL_SAVE_FILE):
        try:
            model = keras.models.load_model(MODEL_SAVE_FILE)
        except:
            logging.warning("Error loading previous model! creating a new one...")
    else:
        logging.info("Previous model not found! creating a new one...")

    model.save(MODEL_SAVE_FILE)
    logging.info("Demo model saved!")

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Hello, World!'

    @app.route('/get_params')
    def get_params():
        res = he_lib.get_param_info()
        return jsonify({
            'success': True,
            'error_code': SERVER_OK,
            'error_message': SERVER_OK_MESSAGE,
            'result': res
        })

    @app.route('/get_key')
    def get_saved_params():
        res = {
            "key": private_key
        }
        return jsonify({
            'success': True,
            'error_code': SERVER_OK,
            'error_message': SERVER_OK_MESSAGE,
            'result': res
        })

    @app.route('/get_model')
    def get_model():
        return send_file(os.path.join(os.path.dirname(app.root_path), MODEL_SAVE_FILE))

    @app.route('/get_model_weights')
    def get_model_weights():
        # for i in model.get_weights():
        #     print(i.shape)
        #     print(i[0])
        # print("weight from layers:")
        # for i in model.layers:
        #     print(i.get_weights())
        res = {
            "weights": [i.tolist() for i in model.get_weights()]
        }
        return jsonify({
            'success': True,
            'error_code': SERVER_OK,
            'error_message': SERVER_OK_MESSAGE,
            'result': res
        })

    @app.route('/update_model_weights_enc', methods=['POST'])
    def update_model_weights():
        content = request.json
        weights = content['weights']
        num_party = content['num_party']
        logging.info("Num workers involved = {}".format(num_party))
        update_weights = he_lib.decrypt_layer_weights(weights, num_party)

        for idx, weight in enumerate(model.get_weights()):
            shape = weight.shape
            new_weight = update_weights[idx]
            logging.debug(f"Original decrypted layer weight {idx} = {min(new_weight)} " +
                            f"{max(new_weight)} {len(new_weight)}")
            new_weight = numpy.resize(new_weight, shape)
            update_weights[idx] = new_weight

        model.set_weights(update_weights)
        evaluate_model()
        return jsonify({
            'success': True,
            'error_code': SERVER_OK,
            'error_message': SERVER_OK_MESSAGE,
        })

    @app.route('/evaluate_model')
    def evaluate_model():
        (_, _), (x_test, y_test) = keras.datasets.mnist.load_data()
        # Scale images to the [0, 1] range
        x_test = x_test.astype("float32") / 255
        # Make sure images have shape (28, 28, 1)
        x_test = numpy.expand_dims(x_test, -1)
        logging.info("{} test samples".format(x_test.shape[0]))
        y_test = keras.utils.to_categorical(y_test, num_classes)
        score = model.evaluate(x_test, y_test, verbose=0)
        logging.info("Test loss: {}".format(score[0]))
        logging.info("Test accuracy: {}".format(score[1]))
        res = {
            "loss": score[0],
            "accuracy": score[1],
        }
        return jsonify({
            'success': True,
            'error_code': SERVER_OK,
            'error_message': SERVER_OK_MESSAGE,
            'result': res
        })

    return app
