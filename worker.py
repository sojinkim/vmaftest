from celery import Celery
import sys, pexpect
from gvars import *
import time 

app = Celery('worker', backend='rpc://', broker='pyamqp://myuser:mypassword@192.168.10.242/myvhost')


@app.task
def run_fake_vmaf(cmd):
    print cmd
    time.sleep(3)
    return 99, 0


