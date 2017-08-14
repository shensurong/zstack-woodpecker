'''

Test about monitor trigger on all host cpu free ratio in one minute,adding changing media state

@author: Songtao,Haochen

'''

import test_stub
import random
import time
import os
import zstacklib.utils.ssh as ssh
import zstackwoodpecker.test_util as test_util
import zstackwoodpecker.operations.resource_operations as res_ops
import zstackwoodpecker.operations.monitor_operations as mon_ops

def test():
    global trigger
    global media
    global trigger_action

    test_item = "host.cpu.util"
    resource_type="HostVO"
    host_monitor_item = test_stub.get_monitor_item(resource_type)
    if test_item not in host_monitor_item:
        test_util.test_fail('%s is not available for monitor' % test_item)

    hosts = res_ops.get_resource(res_ops.HOST)
    host = hosts[0]
    duration = 60
    expression = "host.cpu.util{cpu=-1,type=\"idle\"}<40.3"
    monitor_trigger = mon_ops.create_monitor_trigger(host.uuid, duration, expression)

    send_email = test_stub.create_email_media()
    media = send_email.uuid
    trigger_action_name = "trigger"+ ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(8)))
    trigger = monitor_trigger.uuid
    receive_email = os.environ.get('receive_email')
    monitor_trigger_action = mon_ops.create_email_monitor_trigger_action(trigger_action_name, send_email.uuid, trigger.split(), receive_email)
    trigger_action = monitor_trigger_action.uuid
    state = "disable"
    monitor_trigger = mon_ops.change_email_media_state(media,state)
    
    host.password = os.environ.get('hostPassword')
    ssh_cmd = test_stub.ssh_cmd_line(host.managementIp, host.username, host.password, port=int(host.sshPort))
    test_stub.run_all_cpus_load(ssh_cmd)

    status_problem, status_ok = test_stub.query_trigger_in_loop(trigger,50)
    test_util.action_logger('Trigger old status: %s triggered. Trigger new status: %s recovered' % (status_problem, status_ok ))
    if status_problem != 1 or status_ok != 1:
        test_util.test_fail('%s Monitor Test failed, expected Problem or OK status not triggered' % test_item)
    mail_list = test_stub.receive_email()
    keywords = "fired"
    mail_flag = test_stub.check_email(mail_list, keywords, trigger, host.uuid)
    if mail_flag != 0:
        test_util.test_fail('Failed to disable Media: %s for: %s Trigger Mail' % (media, test_item))

    state = "enable"
    monitor_trigger = mon_ops.change_email_media_state(media,state)
    test_stub.run_all_cpus_load(ssh_cmd)
    status_problem, status_ok = test_stub.query_trigger_in_loop(trigger)
    test_util.action_logger('Trigger old status: %s triggered. Trigger new status: %s recovered' % (status_problem, status_ok ))
    if status_problem != 1 or status_ok != 1:
        test_util.test_fail('%s Monitor Test failed, expected Problem or OK status not triggered' % test_item)
    mail_list = test_stub.receive_email()
    keywords = "fired"
    mail_flag = test_stub.check_email(mail_list, keywords, trigger, host.uuid)
    if mail_flag == 0:
        test_util.test_fail('Failed to Enable Media: %s for: %s Trigger Mail' % (media.uuid, test_item))

    mon_ops.delete_monitor_trigger_action(trigger_action)
    mon_ops.delete_monitor_trigger(trigger)
    mon_ops.delete_email_media(media)

def error_cleanup():
    global trigger
    global media
    global trigger_action
    mon_ops.delete_monitor_trigger_action(trigger_action)
    mon_ops.delete_monitor_trigger(trigger)
    mon_ops.delete_email_media(media)