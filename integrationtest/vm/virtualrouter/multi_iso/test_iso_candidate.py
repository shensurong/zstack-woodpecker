'''

New Integration Test for Multi-ISO.

@author: Legion
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import time

test_obj_dict = test_state.TestStateDict()
test_stub = test_lib.lib_get_test_stub()
multi_iso = test_stub.MulISO()

def test():
    multi_iso.add_iso_image()
    multi_iso.create_vm()
    test_obj_dict.add_vm(multi_iso.vm1)

    multi_iso.get_all_iso_uuids()
    multi_iso.attach_iso(multi_iso.iso_uuids[0])
    multi_iso.check_iso_candidate(multi_iso.iso_names[0])
    multi_iso.attach_iso(multi_iso.iso_uuids[1])
    multi_iso.check_iso_candidate(multi_iso.iso_names[1])

    multi_iso.detach_iso(multi_iso.iso_uuids[0])
    multi_iso.check_iso_candidate(multi_iso.iso_names[0], is_candidate=True)
    multi_iso.detach_iso(multi_iso.iso_uuids[1])
    multi_iso.check_iso_candidate(multi_iso.iso_names[1], is_candidate=True)

    test_lib.lib_robot_cleanup(test_obj_dict)
    test_util.test_pass('Get Candidate ISO Test Success')

#Will be called only if exception happens in test().
def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
