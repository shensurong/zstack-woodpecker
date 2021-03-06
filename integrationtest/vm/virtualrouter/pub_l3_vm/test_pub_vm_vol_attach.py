'''

@author: FangSun
'''


import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.test_state as test_state
import zstackwoodpecker.test_util as test_util


test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


def test():

    pub_l3_vm, flat_l3_vm, vr_l3_vm = test_stub.generate_pub_test_vm(tbj=test_obj_dict)

    volume_list = test_stub.create_multi_volumes()
    for volume in volume_list:
        test_obj_dict.add_volume(volume)

    for vm in [pub_l3_vm, flat_l3_vm, vr_l3_vm]:
        for volume in volume_list:
            volume.attach(vm)
        vm.check()
        for volume in volume_list:
            volume.detach()
        vm.check()

    test_util.test_pass('pub vm volume attach check pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)


