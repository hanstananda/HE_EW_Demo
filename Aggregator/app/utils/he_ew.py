import base64
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

import numpy

from config.flask_config import APP_ROOT, LIBRARY_EXECUTABLE, CIPHERTEXT_SAVE_FILE


class HomomorphicEncryptionEW:
    max_range = 10.0
    supported_max_int = 60000

    def __init__(self, cipher_save_path):
        self._cipher_save_path = cipher_save_path
        self._encrypted_weights = []
        self.metadata = ""

    @staticmethod
    def get_param_info():
        res = {
            "scheme": "HomomorphicEncryptionEW"
        }
        return res

    def save_encrypted_weight(self, weights):
        file_path = Path(self._cipher_save_path).joinpath(str(datetime.now()) + ".bin")
        with open(file_path, "wb+") as f:
            f.write(base64.b64decode(weights))
        self._encrypted_weights.append(file_path.absolute())

    def aggregate_encrypted_weights(self):
        start_time = time.clock()
        inp_str = self.metadata
        num_party = len(self._encrypted_weights)
        if num_party == 0:
            return {
                "metadata": self.metadata,
                "weights": None,
                "num_party": num_party
            }
        executable_path = Path(APP_ROOT).parent.joinpath(LIBRARY_EXECUTABLE)
        result_file = Path(self._cipher_save_path).joinpath(CIPHERTEXT_SAVE_FILE)
        process = subprocess.run(
            [
                str(executable_path.absolute()),
                "add",
                result_file.absolute(),
                str(num_party),
                *self._encrypted_weights
            ],
            input=inp_str.encode('utf-8'),
            stdout=subprocess.PIPE)
        process_outputs = process.stdout.decode('utf-8')

        time_elapsed = time.clock() - start_time
        logging.info(f"Time taken for encrypted aggregation is {time_elapsed} s")

        # Reset encrypted weights
        for i in self._encrypted_weights:
            file = Path(i)
            file.unlink()
        self._encrypted_weights = []

        with open(result_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')

        return {
            "metadata": process_outputs,
            "weights": encoded_string,
            "num_party": num_party
        }
