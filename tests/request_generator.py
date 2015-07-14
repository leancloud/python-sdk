import time
import hashlib

def generate_request(app_key, master_key=False):
    md5sum = hashlib.md5()
    current_time = str(int(time.time() * 1000))
    md5sum.update(current_time + app_key)
    md5sum = md5sum.hexdigest()
    if master_key:
        return md5sum + "," + current_time + ",master"
    else:
        return md5sum + "," + current_time
