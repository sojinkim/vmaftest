from vmaftest import *

src_path = ''     # reference video
target_path = ''  # distorted videos
result_path = ''  # pkl file

# SourceVideo(filename, width, height, framerate, pixfmt)
src = SourceVideo('2sec.mov', '1920', '1080', '29.97', 'yuv420p')

# dict {height : [list of bitrate in kb]}
target = {
    '1080' : ['3000', '2000', '1000', '500', '300'],
    '900' : ['3000', '2000', '1000', '500', '300', '100'],
    '576' : ['2000', '1000', '1000', '500', '300', '100']
}
target2 = {
    '1080' : ['1000', '500', '300', '100'],
    '900' : ['500', '300', '100'],
}

def loadTest():
    testset = []

    test = VmafTest("test", src, target, src_path, target_path, result_path)
    test.encoding_in_args = ""
    test.encoding_out_args = ""
    testset.append(test)

    test = VmafTest("test2", src, target2, src_path, target_path, result_path)
    test.encoding_in_args = ""
    test.encoding_out_args = ""
    testset.append(test)

    return testset



