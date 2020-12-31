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

    def __init__(self, private_key):
        self._private_key = private_key

    @classmethod
    def get_param_info(cls):
        res = {
            "scheme": "HomomorphicEncryptionEW",
            "supported_max_int": cls.supported_max_int,
            "max_range": cls.max_range,
        }
        return res

    def decode_value(self, val, num_party):
        processed_val = val * 2 * self.max_range
        processed_val /= self.supported_max_int

        # Normalize back from (0, 2*max_range) to (-max_range, max_range)
        processed_val -= self.max_range * num_party

        return processed_val / num_party

    def decrypt_layer_weights(self, layer_weights, num_party):
        decoded_weights = []
        start_time = time.clock()
        inp_str = f"1 {self._private_key}\n"
        inp_str += layer_weights
        executable_path = Path(APP_ROOT).parent.parent.joinpath(LIBRARY_EXECUTABLE)
        process = subprocess.run([str(executable_path.absolute()), "decrypt"],
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
