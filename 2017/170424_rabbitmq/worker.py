﻿#!/usr/bin/env/env python
import pika
import time

connection =pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print '[*] waiting for messages. to exit press CTRL+C'

def callback(ch, method, properties, body):
    print "[x] received %r" % (body,)
    time.sleep(body.count('.'))
    print "[x] done."
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue='hello', no_ack=False)

channel.start_consuming()

# # worker.py