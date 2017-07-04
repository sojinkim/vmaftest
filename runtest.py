from testdata import loadTest


def main():
    testset = loadTest()

    for test in testset:
        test.convertSrc2Yuv()
        test.generateTestSet()
        print 'encoding failed', test.encode_failed 
        test.calculateVmaf()
        print 'vmaf failed', test.vmaf_failed


if __name__ == "__main__":
    main()
