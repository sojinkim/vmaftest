import dill, pickle, csv, sys
import matplotlib.pyplot as plt
from collections import defaultdict
from itertools import cycle
from vmaftest import *

# load test result
if len(sys.argv) == 1:
    print "input file missing"
    exit(1)
else:
    pkl_file = open(sys.argv[1], 'rb')
    result = pickle.load(pkl_file)
    pkl_file.close()

# generate x y labels
setlist = [set([' '])]
keylist = [] 
for key, value in result.iteritems():
    setlist.append(set(value.keys()))  # bitrate 
    keylist.append(int(key))           # resolution 

bitrate_list =  sorted(set.union(*setlist))
resolution_list = sorted(keylist)

# for plotting
bitrate_list_num = []
for i in bitrate_list[1:]:
    bitrate_list_num.append(int((i))) 
getcolor = cycle('bgrcmyk').next

# print vmaf score table in csv format
print ', '.join(str(p) for p in bitrate_list) 

for i in resolution_list:
    print i, ', '.join( str(result[str(i)].get(j, list(["",""]))[1])  for j in bitrate_list ) 

    # draw plot
    vmaf_scores = [ result[str(i)].get(j, list(["",""]))[1]  for j in bitrate_list ] 
    vmaf_scores_calculated = []
    bitrate_list_num_used = []
    for index, score in enumerate(vmaf_scores[1:]):
        if score != '':
            vmaf_scores_calculated.append(score)
            bitrate_list_num_used.append(bitrate_list_num[index])
            
    plt.plot(bitrate_list_num_used, vmaf_scores_calculated, 's--', color=getcolor(),  label=str(i)+'p', linewidth=1)


plt.legend(loc=4)
plt.axis([bitrate_list_num[0]-500,bitrate_list_num[-1]+500, 20, 100])
plt.xlabel('bitrate(K)')
plt.ylabel('vmaf score')
plt.show()


