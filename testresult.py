import threading


class TestResult:

    lock = threading.Lock()
    result = None
    encode_failed = []
    vmaf_failed = []
   
    def __init__(self):
        pass
 
    def init_once(self, result):
        if TestResult.result is None:
            TestResult.result = result

    def update_score(self, height, bitrate, fvalue):
        with TestResult.lock:
            TestResult.result[height][bitrate][1] = fvalue

    def add_encode_failure(self, height, bitrate):
        with TestResult.lock:
            TestResult.encode_failed.append(height + '_' + bitrate)

    def add_vmaf_failure(self, height, bitrate):
        with TestResult.lock:
            TestResult.vmaf_failed.append(height + '_' + bitrate)

    def get_result(self):
        return TestResult.result 
