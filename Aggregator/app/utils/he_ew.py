import logging
import os
import subprocess
import time
from pathlib import Path

import numpy

from config.flask_config import APP_ROOT, LIBRARY_EXECUTABLE


class HomomorphicEncryptionEW:
    max_range = 10.0
    supported_max_int = 32000

    def __init__(self, cipher_save_path):
        self._cipher_save_path = cipher_save_path
        self._encrypted_weights = []

    @staticmethod
    def get_param_info():
        res = {
            "scheme": "HomomorphicEncryptionEW"
        }
        return res

    def save_encrypted_weight(self, weights):
        self._encrypted_weights.append(weights)

    def aggregate_encrypted_weights(self):
        start_time = time.clock()
        inp_str = "0\n"
        num_party = len(self._encrypted_weights)
        for i in self._encrypted_weights:
            inp_str += i + "\n"
        executable_path = Path(APP_ROOT).parent.parent.joinpath(LIBRARY_EXECUTABLE)
        process = subprocess.run([str(executable_path.absolute()), "addition", str(num_party)],
                                 input=inp_str.encode('utf-8'),
                                 stdout=subprocess.PIPE)
        process_outputs = process.stdout.decode('utf-8')
        # Remove the key params from the output
        key_end_idx = process_outputs.find("\n")

        time_elapsed = time.clock() - start_time
        logging.info(f"Time taken for encrypted aggregation is {time_elapsed} s")

        # Reset encrypted weights
        self._encrypted_weights = []

        return process_outputs[key_end_idx:], num_party

