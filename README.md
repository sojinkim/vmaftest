### env : 
- ubuntu 16.04
- python 2.7.12

### prerequisite : 
- sudo apt-get install ffmpeg
- vmaf install : https://github.com/Netflix/vmaf

### python packages used : 
- dill, pickle, csv, matplotlib, simplejson, pexpect 



## usage 1 : encode test video set from single src, and run vmaf 
1. edit 
- gvar.py : vmaf path
- testdata.py : define test set 
2. run test 
- $ python runtest.py
3. vis
- $ python report.py [pkl file name]


## usage 2 : run test from file (w/o encoding). test set defined in the file
1. edit
- filelist : json file 
2. run test
- $ python runvmaf.py filelist
3. vis
- $ python report.py [pkl file name]



## ps. celery/ rabbitmq test
- worker.py : fake worker
- sender.py : send one task, wait till finish, print result

1. install celery & rabbitmq
- http://docs.celeryproject.org/en/latest/getting-started/first-steps-with-celery.html#installing-celery

2. env setting
- $ sudo rabbitmqctl add_user myuser mypassword
- $ sudo rabbitmqctl add_vhost myvhost
- $ sudo rabbitmqctl set_user_tags myuser mytag
- $ sudo rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"

3. run worker
- $ celery -A worker worker --loglevel=info

4. On another termianl or remote server, execute sender.py. Both server should have celery/rabbitmq installed.  
- $ python sender.py

