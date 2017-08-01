from testdata import loadTest


def main():
    testset = loadTest()

    for test in testset:
        test.convertSrc2Yuv()
        test.generateTestSet()
        print 'encoding failed:', test.encoding_failed
        test.calculateVmaf()
        print 'vmaf failed:', test.vmaf_failed
        print 'vmaf result:', test.result 

if __name__ == "__main__":
    main()
