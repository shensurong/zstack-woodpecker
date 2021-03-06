'''

@author: Youyk
'''
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import test_stub
import zstackwoodpecker.test_state as test_state
import time

test_obj_dict = test_state.TestStateDict()
vol_num = 22
volume_list = []

def test():
    global test_obj_dict
    global vol_num
    global volume
    vm = test_stub.create_vm()
    test_obj_dict.add_vm(vm)
    vm.check()
    for i in range(vol_num):
        volume_list.append(test_stub.create_volume())
        test_obj_dict.add_volume(volume_list[i])

    additional_vol = test_stub.create_volume()
    test_obj_dict.add_volume(additional_vol)

    for i in range(vol_num):
        volume_list[i].check()
    time.sleep(60)

    test_util.test_dsc('Test attach/detach 22 volumes operations.')
    for i in range(vol_num):
        volume_list[i].attach(vm)

    for i in range(vol_num):
        volume_list[i].check()

    for i in range(vol_num):
        volume_list[i].detach()
        volume_list[i].check()

    test_util.test_dsc('Redo attach/detach 22 volumes operations.')

    for i in range(vol_num):
        volume_list[i].attach(vm)
        volume_list[i].check()

    test_util.test_dsc('Try to attach the 22th data volume.')
    try:
        additional_vol.attach(vm)
    except:
        test_util.test_logger('Catch expected exception: try to attach the 25th data [volume:] %s to [vm:] %s fail.' % (additional_vol.volume.uuid, vm.vm.uuid))
        
        for i in range(vol_num):
            volume_list[i].detach()
            volume_list[i].check()

        for i in range(vol_num):
            volume_list[i].delete()
            volume_list[i].check()

        vm.destroy()
        test_util.test_pass('Create Multi Data Volumes for VM Test Success')
        return True

    test_util.test_fail('Fail: could attached the 25th data [volume:] %s to [vm:] %s .' % (additional_vol.volume.uuid, vm.vm.uuid))
    return False

def error_cleanup():
    global test_obj_dict
    test_lib.lib_error_cleanup(test_obj_dict)
