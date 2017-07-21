import pika
import time
import os
import sys, pexpect

def run_encode(cmd1, cmd2):
    print cmd1
    print cmd2
    ret1 = os.system(cmd1)
    ret2 = os.system(cmd2)
    return ret1 or ret2

def run_vmaf(cmd):
    print cmd
    try:
        p = pexpect.spawn(cmd)
    except:
        return 0.0, -1

    p.timeout = None
    p.maxsize = 1
    for line in p: pass
    p.close()
    
    if p.exitstatus == 0:
        try:
            score = float(line.split(':')[-1])  # vmaf score
        except:
            score = 0.0
    else:
        score = 0.0
    return score, p.exitstatus


def on_encode_request(ch, method, props, body):
    print(" [x] Encode request received %r" % body)
    cmds = body.split(';')
    response = run_encode(cmds[0], cmds[1])

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                        props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)
    print(" [x] Done")

def on_vmaf_request(ch, method, props, body):
    print(" [x] Vmaf request received %r" % body)
    cmd = body
    score,exitcode = run_vmaf(cmd)
    response = str(score)+';'+str(exitcode) 

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                        props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag = method.delivery_tag)
    print(" [x] Done")



def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='rpc_queue_encode')
    channel.queue_declare(queue='rpc_queue_vmaf')


    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_encode_request, queue='rpc_queue_encode')
    channel.basic_consume(on_vmaf_request, queue='rpc_queue_vmaf')

    print(' [*] Waiting for messages. To exit press CTRL+C')

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()

if __name__ == '__main__':
    main()

