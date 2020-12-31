import logging
import os
import subprocess
import time
from pathlib import Path

import numpy

from config.flask_config import APP_ROOT, LIBRARY_EXECUTABLE


class HomomorphicEncryptionEW:
    min_range = -10.0
    max_range = 10.0
    supported_max_int = 32767

    def __init__(self, private_key, cipher_save_path):
        self._private_key = private_key
        self._cipher_save_path = cipher_save_path

    @staticmethod
    def get_param_info():
        res = {
            "key": "HomomorphicEncryptionEW"
        }
        return res

    def normalize_value(self, val):
        processed_val = max(val, self.min_range)
        processed_val = min(processed_val, self.max_range)
        processed_val *= 32767
        processed_val /= (self.max_range - self.min_range)
        return int(processed_val)

    def encrypt_layer_weights(self, layer_weights):
        weights = []
        start_time = time.clock()

        for idx, layer_weight in enumerate(layer_weights):
            logging.debug("layer weight {} = {}".format(idx, layer_weight))
            logging.debug(layer_weight.shape)
            # Reshape to 1D vector
            vector_size = layer_weight.size
            reshaped_layer_weight = numpy.resize(layer_weight, (vector_size,))
            logging.debug(reshaped_layer_weight.shape)
            # Cast to python native list then pass to SEAL library to be encrypted
            weights.append(reshaped_layer_weight)

        time_elapsed = time.clock() - start_time
        logging.info(f"Time taken for encryption is {time_elapsed} s")
        # Format input to be given to the library
        inp_str = f"1 {self._private_key}\n"
        inp_str += f"{len(weights)}\n"
        for layer in weights:
            inp_str += f"{len(layer)} "
            for val in layer:
                processed_val = self.normalize_value(val)
                inp_str += f"{processed_val} "
            inp_str += "\n"

        executable_path = Path(APP_ROOT).parent.parent.joinpath(LIBRARY_EXECUTABLE)
        process = subprocess.run([str(executable_path.absolute()), "encrypt"],
                                 input=inp_str.encode('utf-8'),
                                 stdout=subprocess.PIPE)
        process_outputs = process.stdout.decode('utf-8')
        # Remove the key from the output
        key_end_idx = process_outputs.find("\n")
        return process_outputs[key_end_idx:]
