import simplejson as json
import dill, pickle
import os, sys, pexpect
from collections import defaultdict
from worker import run_vmaf
from gvars import *

def getResultFile(ref):
        return 'vs' + ref +'.pkl'

def initResult(ref):
    if os.path.exists(getResultFile(ref)):
        pkl_file = open(getResultFile(ref), 'rb')
        result = pickle.load(pkl_file)
        pkl_file.close()
    else:
        result = defaultdict(lambda: defaultdict(list))
    return result

def main():
    # read input file
    if len(sys.argv) == 1:
        print 'input file missing'   
        exit(1)
    else:
        with open(sys.argv[1], 'rb') as data_file:
            data = json.load(data_file)
            data_file.close()

    for item in data['testset']:
        result = initResult(item['ref'])
        vmaf_failed =[]
        for dis in item['dis']: 
            height = dis.split('_')[-2]  ## dependent to file naming rule
            bitrate = (dis.split('_')[-1].split('.')[0]).zfill(5) ##

            if height in result and bitrate in result[height]: pass
            else: 
                cmd = g_vmaf_cmd + ' ' \
                     + item['pixfmt'] + ' ' +  item['res'] + ' ' \
                     + item['refpath'] + item['ref'] + ' ' + item['dispath'] + dis
                score, exitcode = run_vmaf(cmd)
                if exitcode != 0:
                    vmaf_failed.append(height + '_' + bitrate)

                result[height][bitrate] = [dis, score]

        print result
        print 'failed :', vmaf_failed

        pkl_file = open(getResultFile(item['ref']), 'wb')
        pickle.dump(result, pkl_file)
        pkl_file.close()


if __name__ == "__main__":
    main()

