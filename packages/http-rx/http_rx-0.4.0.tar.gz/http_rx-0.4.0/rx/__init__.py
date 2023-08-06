from . import check, doctor, report

import time
import logging


def run():
    """
    Run the HTTP RX application.
    """
    import json
    import os

    # Parse JSON config file
    config_file_path = os.environ.get('RX_CONF', 'config.json')
    with open(config_file_path) as config_file:
        config = json.load(config_file)

    logging.basicConfig(level=logging.getLevelName(config.get('logLevel', 'INFO')), format='%(asctime)s [%(levelname)s] - %(message)s')
    doc = doctor.Doctor(config)
    doc.run() # mainloop
