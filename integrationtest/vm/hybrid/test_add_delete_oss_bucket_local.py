'''

New Integration Test for hybrid.

@author: Quarkonics
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time


test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
hybrid = test_stub.HybridObject()

def test():
    hybrid.add_datacenter_iz(add_datacenter_only=True)
    hybrid.add_bucket()
    time.sleep(10)
    hybrid.del_bucket(remote=False)
    test_util.test_pass('Add Delete OSS Bucket in Local Test Success')

def env_recover():
    if hybrid.oss_bucket_create:
        hybrid.del_bucket()

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
