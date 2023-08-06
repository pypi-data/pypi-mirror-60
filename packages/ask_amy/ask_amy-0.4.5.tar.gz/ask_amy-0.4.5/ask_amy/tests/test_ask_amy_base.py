import unittest
import logging
import os
import sys
import json


class TestCaseASKAmy(unittest.TestCase):
    """ Base class for Testing ask_amy
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    path = sys.path
    test_data_dir = "{}/data/".format(os.path.dirname(__file__))
    if test_data_dir not in path:
        path.insert(0, test_data_dir)

    # Create and environment variable ASK_AMY_LOGGING to specify a logging directory
    path = os.getenv('ASK_AMY_LOGGING_DIR', os.path.expanduser('~')) + os.sep
    hdlr = logging.FileHandler(path + 'logfile.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)

    # Helper functions
    def load_json_file(self, file_name):
        test_script_location = os.path.dirname(__file__)
        file_path = "{}/data/{}".format(test_script_location,file_name)
        print("file_path {}".format(file_path))
        file_ptr_r = open(file_path, 'r')
        json_data = json.load(file_ptr_r)
        file_ptr_r.close()
        return json_data
