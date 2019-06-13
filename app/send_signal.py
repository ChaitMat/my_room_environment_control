#Module to send the IR signal via LIRC

import os

def send_signal(key):

    remote_command = "irsend SEND_ONCE LG " + key

    os.system(remote_command)
