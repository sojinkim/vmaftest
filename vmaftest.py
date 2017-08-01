import dill, pickle, os
import sys, pexpect
from collections import defaultdict
from gvars import *
from Queue import Queue
if g_rpc:
    from rpc_sender import Sender
    from threading import Thread
else:
    from worker import run_encode, run_vmaf


class SourceVideo:
    def __init__(self, filename, width, height, framerate, pixfmt):
        self.name = filename
        self.width = width
        self.height = height
        self.yuv = self.name + '.yuv' 
        self.framerate = framerate
        self.pixfmt = pixfmt  # yuv420p, yuv422p, yuv444p, yuv420p10le, yuv422p10le, yuv444p10le


class VmafTest:

    def __init__(self, name, srcVideo, targetVideos, src_path, target_path, result_path):
        self.name = name
        self.src = srcVideo # class SourceVideo
        self.targetVideos = targetVideos   # dict of list {height : [list of bitrate in k]} 

        self.encoding_overwrite = False
        self.encoding_in_args = ""
        self.encoding_out_args = ""
        self.vmaf_runall = False

        self.src_path = src_path
        self.target_path = target_path
        self.result_path = result_path

        self.result = None
        self._init_result()

        self.rpc_resultqueue = Queue(maxsize=0)
        self.failedqueue = Queue(maxsize=0)

        self.encoding_failed = []
        self.vmaf_failed = []

    def _init_result(self):
        if os.path.exists(self._getResultFile()):
            pkl_file = open(self._getResultFile(), 'rb')
            self.result = pickle.load(pkl_file)
            pkl_file.close()
        else:
            self.result = defaultdict(lambda: defaultdict(list))
        
        # test result is cumulative, bacause vmaf run takes very long time. 
        # new test case added under the same test name will be inserted in the test set.
        # removed test case is not eliminated from the previous pkl file, if exists. 
        # test cases are defined in testdata.py
        for key, value in self.targetVideos.iteritems():  
            for i in range(len(value)):
                height, bitrate = (key, value[i].zfill(5))
                if not (height in self.result) or not (bitrate in self.result[key]):
                    self.result[height][bitrate] = [self._getTargetYuvFile(height, bitrate), 0.0]
                print height, bitrate

        pkl_file = open(self._getResultFile(), 'wb')
        pickle.dump(self.result, pkl_file)
        pkl_file.close()

        
    def _composeTargetVideoName(self, height, bitrate):
        return self.src.yuv + '_' + self.name + '_' + height + '_' + bitrate

    def _getResultFile(self):
        return self.result_path + self.name + '_vmaf_result.pkl'

    def _getSourceFile(self):
        return self.src_path + self.src.name

    def _getSourceYuvFile(self):
        return self.src_path + self.src.yuv

    def _getTargetMp4File(self, height, bitrate):
        return self.target_path + self._composeTargetVideoName(height, bitrate) + '.mp4'

    def _getTargetYuvFile(self, height, bitrate):
        return self.target_path + self._composeTargetVideoName(height, bitrate) + '.yuv'
  
    def _ffmpeg_cmds(self, height, bitrate):

        src_file = self._getSourceYuvFile()
        trans_file_mp4 = self._getTargetMp4File(height, bitrate)   
        trans_file_yuv = self._getTargetYuvFile(height, bitrate)  

        cmd1 = 'ffmpeg -y -s:v ' + self.src.width + 'x' + self.src.height \
              + ' -r ' + self.src.framerate \
              + self.encoding_in_args \
              + ' -i ' + src_file \
              + ' -c:v libx264 -b:v ' + bitrate +'k' \
              + ' -vf "scale=-1:' + height + '"' + ' -qcomp 0.0 ' \
              + self.encoding_out_args \
              + trans_file_mp4
    
        cmd2 = 'ffmpeg -y -i ' + trans_file_mp4 \
              + ' -c:v rawvideo -vf scale=' + self.src.width + ':' + self.src.height \
              + ' -pix_fmt ' + self.src.pixfmt + ' ' \
              + trans_file_yuv

        return cmd1, cmd2


    def convertSrc2Yuv(self):
        src_file = self._getSourceFile()
        src_yuv_file = self._getSourceYuvFile()

        if (not os.path.exists(src_yuv_file)) or self.encoding_overwrite: 
            cmd = 'ffmpeg -y -i ' + src_file \
                  + ' -vf "yadif=0:-1:0" -c:v rawvideo -pix_fmt ' + self.src.pixfmt + ' ' \
                  + src_yuv_file
            print cmd 
            os.system(cmd)


    def generateTestSet(self):
        result = self.result
        threads = []

        for key, value in result.iteritems():
            for i in value.keys():
                height, bitrate = (key, i.zfill(5))

                if (not os.path.exists(self._getTargetMp4File(height, bitrate))) \
                   or self.encoding_overwrite:
                    cmd1, cmd2 = self._ffmpeg_cmds(height, bitrate)
                    
                    if g_rpc: 
                        cmds = cmd1 + ';' + cmd2
                        t = Thread(target=Sender().remote_ffmpeg, args=(cmds, height, bitrate, self.rpc_resultqueue, self.failedqueue))
                        threads += [t]
                        t.start()
                        t.join()
                    else:
                        ret = run_encode(cmd1, cmd2)
                        if ret != 0:
                            self.failedqueue.put(height + '_' + bitrate)

        while not self.failedqueue.empty():
            self.encoding_failed.append(self.failedqueue.get())


    def _vmaf_cmd(self, height, bitrate):
        cmd = g_vmaf_cmd + ' ' + self.src.pixfmt + ' ' \
              + self.src.width + ' ' + self.src.height + ' ' \
              + self._getSourceYuvFile() + ' ' + self._getTargetYuvFile(height, bitrate)  
        return cmd


    def calculateVmaf(self):
        src = self.src
        runall = self.vmaf_runall
        result = self.result
        threads = []

        # run vmaf through testset
        for key, value in result.iteritems():
            for i in value.keys():
                if runall or result[key][i][1] == 0.0:
                    cmd = self._vmaf_cmd(key, i)
                    
                    if g_rpc: 
                        t = Thread(target=Sender().remote_vmaf, args=(cmd, key, i, self.rpc_resultqueue, self.failedqueue))
                        threads += [t]
                        t.start()
                        t.join()
                       
                    else: 
                        score, exitcode = run_vmaf(cmd)
                        if exitcode != 0:
                            self.failedqueue.put(key + '_' + i)
                    
                        print key, i, score, exitcode
                        result[key][i][1] = score
        if g_rpc:
            self._update_result()

        # store the updated dictionay back to the file
        pkl_file = open(self._getResultFile(), 'wb')
        pickle.dump(result, pkl_file)
        pkl_file.close()
        
        while not self.failedqueue.empty():
            self.vmaf_failed.append(self.failedqueue.get())


    def _update_result(self):
        while not self.rpc_resultqueue.empty():
            height, bitrate, score = self.rpc_resultqueue.get()
            self.result[height][bitrate][1] = score

