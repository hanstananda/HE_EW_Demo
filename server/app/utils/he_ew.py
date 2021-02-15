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
    EPS = 1e-3

    def __init__(self, private_key_save_path, cipher_save_path):
        self._cipher_save_path = cipher_save_path
        self._private_key_save_path = private_key_save_path

    @classmethod
    def get_param_info(cls):
        res = {
            "scheme": "HomomorphicEncryptionEW",
            "supported_max_int": cls.supported_max_int,
            "max_range": cls.max_range,
        }
        return res

    def decode_value(self, val: int, num_party: int):
        # if val >= 2 * self.supported_max_int:
        #     logging.warning(f"Found decrypted value of {val} more than supported limit!")
        processed_val = val * 2 * self.max_range
        processed_val /= self.supported_max_int

        # Divide by the number of involved parties
        result = processed_val / num_party

        # Normalize back from (0, 2*max_range) to (-max_range, max_range)
        result -= self.max_range

        if result - self.EPS > self.max_range or result + self.EPS < -self.max_range:
            logging.warning(f"Found decoded value of {result} from {val} more than supported limit! Resetting to 0...")
            result = 0.0

        return result

    def decrypt_layer_weights(self, metadata, layer_weights, num_party):
        decoded_weights = []
        start_time = time.clock()
        inp_str = metadata

        file_path = Path(self._cipher_save_path)
        secret_path = Path(self._private_key_save_path)

        with open(file_path, "wb+") as f:
            f.write(base64.b64decode(layer_weights))

        executable_path = Path(APP_ROOT).parent.joinpath(LIBRARY_EXECUTABLE)
        process = subprocess.run([str(executable_path.absolute()), "decrypt", file_path.absolute(), secret_path.absolute()],
                                 input=inp_str.encode('utf-8'),
                                 stdout=subprocess.PIPE)
        process_outputs = process.stdout.decode('utf-8').split("\n")

        for idx in range(2, len(process_outputs)):
            encoded_weights = process_outputs[idx].split()[1:]
            decoded = [self.decode_value(int(i), num_party=num_party) for i in encoded_weights]
            if decoded:  # Check nonempty
                decoded_weights.append(decoded)
                # logging.warning(decoded[:10])

        time_elapsed = time.clock() - start_time
        logging.info(f"Time taken for decryption and decoding is {time_elapsed} s")

        return decoded_weights
