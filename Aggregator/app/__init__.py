import json
import logging
import os

import requests

from app.utils.he_ew import HomomorphicEncryptionEW

from flask import Flask, jsonify, send_file, request

from app.constant.http.error import SERVER_OK, SERVER_OK_MESSAGE

from config.flask_config import PARAMS_JSON_ENDPOINT, CIPHERTEXT_SAVE_FILE, \
    UPDATE_MODEL_ENDPOINT, DefaultConfig


def create_app(config_object=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'launcher.sqlite'),
    )

    if config_object is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(DefaultConfig)
    else:
        # load the test config if passed in
        app.config.from_object(config_object)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    logging.info("Setting up HE library for Aggregator!")

    server_ip = app.config.get("SERVER_IP")

    # Setup PySeal
    cipher_save_path = os.path.join(app.instance_path + CIPHERTEXT_SAVE_FILE)
    he_lib = HomomorphicEncryptionEW(cipher_save_path)

    logging.info("HE library for Aggregator set up successfully!")

    # a simple page that says hello
    @app.route('/')
    def hello():
        return "Hello from Aggregator!".format(id)

    # To check whether worker params successfully set up
    @app.route('/get_params')
    def get_params():
        res = he_lib.get_param_info()
        return jsonify({
            'success': True,
            'error_code': SERVER_OK,
            'error_message': SERVER_OK_MESSAGE,
            'result': res
        })

    @app.route('/save_weights', methods=['POST'])
    def save_weights():
        content = request.json
        weights = content['weights']
        he_lib.save_encrypted_weight(weights)
        return jsonify({
            'success': True,
            'error_code': SERVER_OK,
            'error_message': SERVER_OK_MESSAGE,
        })

    @app.route('/agg_val')
    def agg_val():
        weight, num_party = he_lib.aggregate_encrypted_weights()
        if not weight:
            return jsonify({
                'success': True,
                'error_code': SERVER_OK,
                'error_message': SERVER_OK_MESSAGE,
                'result': weight,
            })

        res = {
            "weights": weight,
            "num_party": num_party
        }
        response = requests.post(server_ip + UPDATE_MODEL_ENDPOINT, json=res)

        res["update_status_code"] = response.status_code
        return jsonify({
            'success': True,
            'error_code': SERVER_OK,
            'error_message': SERVER_OK_MESSAGE,
            # 'result': res,
        })

    return app
