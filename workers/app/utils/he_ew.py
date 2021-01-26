import base64
import logging
import os
import subprocess
import time
from pathlib import Path

import numpy

from config.flask_config import APP_ROOT, LIBRARY_EXECUTABLE


class HomomorphicEncryptionEW:
    max_range = 10.0
    supported_max_int = 60000

    def __init__(self, private_key, cipher_save_path):
        self._private_key = private_key
        self._cipher_save_path = cipher_save_path

    @classmethod
    def get_param_info(cls):
        res = {
            "scheme": "HomomorphicEncryptionEW",
            "supported_max_int": cls.supported_max_int,
            "max_range": cls.max_range,
        }
        return res

    def normalize_value(self, val):
        processed_val = max(val, -self.max_range)
        processed_val = min(processed_val, self.max_range)
        # Normalize from (-max_range, max_range) to (0, 2*max_range)
        processed_val += self.max_range

        processed_val *= self.supported_max_int
        processed_val /= 2 * self.max_range
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
            logging.debug(f"Encrypting layer weight {idx} = {numpy.amin(reshaped_layer_weight)} " +
                          f"{numpy.amax(reshaped_layer_weight)} {reshaped_layer_weight.shape}")
            # Cast to python native list then pass to SEAL library to be encrypted
            weights.append(reshaped_layer_weight)

        # Format input to be given to the library
        inp_str = f"1 {self._private_key}\n"
        inp_str += f"{len(weights)}\n"
        for layer in weights:
            inp_str += f"{len(layer)} "
            for val in layer:
                processed_val = self.normalize_value(val)
                inp_str += f"{processed_val} "
            inp_str += "\n"

        executable_path = Path(APP_ROOT).parent.joinpath(LIBRARY_EXECUTABLE)
        process = subprocess.run([str(executable_path.absolute()), "encrypt", Path(self._cipher_save_path).absolute()],
                                 input=inp_str.encode('utf-8'),
                                 stdout=subprocess.PIPE)

        process_outputs = process.stdout.decode('utf-8')
        # Remove the key from the output
        key_end_idx = process_outputs.find("\n")

        with open(self._cipher_save_path, "rb") as f:
            encoded_string = base64.b64encode(f.read())

        time_elapsed = time.clock() - start_time
        logging.info(f"Time taken for encryption and encoding is {time_elapsed} s")

        return {
            "metadata": process_outputs[key_end_idx:],
            "weights": encoded_string
        }
