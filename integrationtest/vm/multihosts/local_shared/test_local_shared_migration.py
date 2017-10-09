'''
@author: FangSun
'''

import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.test_lib as test_lib
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.test_state as test_state
import random
import os
import zstackwoodpecker.operations.volume_operations as vol_ops

_config_ = {
        'timeout' : 3000,
        'noparallel' : True
        }

test_stub = test_lib.lib_get_test_stub()
test_obj_dict = test_state.TestStateDict()


case_flavor = dict(root_local_data_local=dict(root_local=True, data_local=True),
                   root_local_data_shared=dict(root_local=True, data_local=False),
                   root_shared_data_local=dict(root_local=False, data_local=True),
                   root_shared_data_shared=dict(root_local=False, data_local=False),
                   )


@test_stub.skip_if_not_local_shared
def test():
    flavor = case_flavor[os.environ.get('CASE_FLAVOR')]
    ps_env = test_stub.PSEnvChecker()
    local_ps, shared_ps = ps_env.get_two_ps()
    disk_offering_uuids = [random.choice(res_ops.get_resource(res_ops.DISK_OFFERING)).uuid]

    test_util.test_dsc("Create vm with data vol")
    vm = test_stub.create_vm_with_random_offering(vm_name='test_vm',
                                                  disk_offering_uuids=disk_offering_uuids,
                                                  ps_uuid=local_ps.uuid if flavor["root_local"] else shared_ps.uuid,
                                                  l3_name='l3VlanNetworkName1',
                                                  system_tags=['primaryStorageUuidForDataVolume::{}'.format(local_ps.uuid if flavor["data_local"]
                                                                                                            else shared_ps.uuid)])

    if flavor["data_local"]:
        volume = test_stub.create_multi_volume(count=2, ps=local_ps, host_uuid=vm.get_vm().hostUuid)
    else:
        volume = test_stub.create_multi_volume(count=2, ps=shared_ps)

    volume.attach(vm)

    test_util.test_dsc("Try to perform live migration")
    if flavor['root_local'] or flavor['data_local']:
        with test_lib.expected_failure("live migration will fail if have local volumes", Exception):
            test_stub.migrate_vm_to_random_host(vm)
    else:
        test_stub.migrate_vm_to_random_host(vm)
    vm.check()

    test_util.test_dsc("Try to perform cold migration")
    volume.detach()
    vm.stop()
    vm.check()
    target_host = test_lib.lib_find_random_host(vm.get_vm())
    if flavor['root_local']:
        vol_ops.migrate_volume(test_lib.lib_get_root_volume(vm.get_vm()).uuid, target_host.uuid)
    else:
        with test_lib.expected_failure("root cold migration on shared PS", Exception):
            vol_ops.migrate_volume(test_lib.lib_get_root_volume(vm.get_vm()).uuid, target_host.uuid)

    if flavor['data_local']:
        vol_ops.migrate_volume(volume.get_volume().uuid, target_host.uuid)
    else:
        with test_lib.expected_failure("root cold migration on shared PS", Exception):
            vol_ops.migrate_volume(volume.get_volume().uuid, target_host.uuid)

    volume.attach(vm)
    vm.start()
    vm.check()

    test_util.test_dsc("Try to perform detached VM hot migration")
    if flavor['root_local'] == False and flavor['data_local']:
        volume.detach()
        test_stub.migrate_vm_to_random_host(vm)
        vol_ops.migrate_volume(volume.get_volume().uuid, vm.get_vm().hostUuid)
        volume.attach(vm)
        vm.check()


    test_util.test_pass('Multi PrimaryStorage Test Pass')


def env_recover():
    test_lib.lib_error_cleanup(test_obj_dict)