import pika
import sys
import threading 
from threading import Thread
from testresult import TestResult

class Sender():

    def __init__(self, testresult):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)
        self.corr_id = None

        self.testresult = testresult

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

        self.connection.close()


    def remote_ffmpeg(self, msg, height, bitrate):

        self.response = None
        self.corr_id = str(height) + ';' + str(bitrate)
        self.channel.basic_publish(exchange='',
                      routing_key='rpc_queue_encode',
                      body=msg,
                      properties=pika.BasicProperties(
                         reply_to = self.callback_queue,
                         correlation_id = self.corr_id,
                      ))

        while self.response is None:
            self.connection.process_data_events()

        print 'ffmpeg response', self.corr_id, self.response
        if self.response != '0':
            self.testresult.add_encode_failure(height, bitrate)


    def remote_vmaf(self, msg, height, bitrate):

        self.response = None
        self.corr_id = str(height) + ';' + str(bitrate)
        self.channel.basic_publish(exchange='',
                      routing_key='rpc_queue_vmaf',
                      body=msg,
                      properties=pika.BasicProperties(
                         reply_to = self.callback_queue,
                         correlation_id = self.corr_id,
                      ))

        while self.response is None:
            self.connection.process_data_events()

        score, exitcode = self.response.split(';')
        print 'vmaf response', self.corr_id, self.response

        if exitcode != '0':
            self.testresult.add_vmaf_failure(height, bitrate)

        self.testresult.update_score(height, bitrate, score)




