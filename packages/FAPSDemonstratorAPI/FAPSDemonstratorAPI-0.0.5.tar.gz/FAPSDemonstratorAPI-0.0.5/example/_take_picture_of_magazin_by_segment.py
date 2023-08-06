#!/usr/bin/python
import threading

import pika
import time
from datetime import datetime
import json
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program, utils
from FAPSDemonstratorAPI.ApplicationConstants import *
from random import shuffle

def periodic_main():
    demonstrator_program = Program()
    if demonstrator_program.connect(): ## Demonstrator is connected
        demonstrator_program.reset()
        demonstrator_program.append_all_instructions(utils.take_picture_of_all_magazin_by_segment())

        ## Execute
        demonstrator_program.execute()
        # threading.Timer(30, periodic_main).start()

    else:
        print('Connection cannot be established to the Demonstrator')


if __name__ == '__main__':
    periodic_main()
