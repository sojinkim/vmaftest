from worker import run_fake_vmaf
import time

r = run_fake_vmaf.delay('cmd')

while not r.ready():
    time.sleep(1)

print r, r.get()
