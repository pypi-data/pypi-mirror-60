#!/usr/bin/python
import threading

import pika
import time
from datetime import datetime
import json
from FAPSDemonstratorAPI import Command, CommandMode, ParameterMode, Program, utils
from FAPSDemonstratorAPI.ApplicationConstants import *
from random import shuffle
import logging

MAGAZIN_INDEX = 4


levels = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL)
logging.basicConfig(format='%(asctime)-15s [%(levelname)] [%(name)-12s] %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logger = logging.getLogger('FAPS Image Stiching Service')
DEMONSTRATOR_ENDPOINT = "cloud.faps.uni-erlangen.de"


def connect(_url, _port, _user, _passwd, _exchange, _queue):
    """
        Connect the FAPSDemonstratorAPI to the demonstrator.
    :return true if the connect has been established or false otherwise.
    """
    connection = None
    channel = None
    exchange = None
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            port=_port,
            host=_url,
            credentials=pika.PlainCredentials(_user, _passwd))
        )
        channel = connection.channel()
        exchange = channel.exchange_declare(
            exchange=_exchange,
            passive=False,
            durable=False,
            exchange_type='fanout'
        )

        queue = channel.queue_declare(
            queue=_queue,
            durable=False,
            exclusive=False,
            auto_delete=True
        ).method.queue
        channel.queue_bind(exchange=_exchange, queue=queue, routing_key='')

        return connection, channel, exchange, queue

    except Exception as e:
        logger.error(e)
        if not (channel is None):
            channel.close()
            channel = None
        if not (connection is None):
            connection.close()
            connection = None
        return None, None


def periodic_main():
    # Add Connection to the calibration channel
    logger.info('Demonstrator Programm Api using pika version: %s' % pika.__version__)

    # Connect to rabbitMQ
    connection, channel, exchange, queue = connect(
        DEMONSTRATOR_ENDPOINT,
        5672,
        'esys',
        'esys',
        "FAPS_DEMONSTRATOR_ImageProcessing_CalibrationSignals",
        "FAPS_DEMONSTRATOR_ImageProcessing_CalibrationSignals"
    )

    # Signal the calibration start
    data = {
        "time": datetime.now().timestamp(),
        "start": True,
        "object": "MAGAZIN_ALL"
    }
    channel.basic_publish(exchange="FAPS_DEMONSTRATOR_ImageProcessing_CalibrationSignals",
                               routing_key='',
                               body=json.dumps(data))

    # Send the program for calibration
    demonstrator_program = Program()
    if demonstrator_program.connect(): ## Demonstrator is connected
        demonstrator_program.reset()
        for i in range(len(MAGAZIN_POSITION_CAMERA)):
            demonstrator_program.append_all_instructions(utils.calibrate_magazin(magazin_index=i))

        ## Execute
        demonstrator_program.execute()
    else:
        print('Connection cannot be established to the Demonstrator')


if __name__ == '__main__':
    periodic_main()
