### env : 
- ubuntu 16.04
- python 2.7.12

### prerequisite : 
- sudo apt-get install ffmpeg
- vmaf install : https://github.com/Netflix/vmaf

### python packages used : 
- dill, pickle, csv, matplotlib, simplejson, pexpect, pika 



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


## run in rpc mode
1. rabbitmq must be installed
2. 'localhost' host name should be changed to run across different machines. 
- worker.py, rpc_sender.py
3. set the var to be true.
- gvar.py : g_rpc = True
4. run worker
- $ python worker.py
5. run test
- $ python runtest.py 
