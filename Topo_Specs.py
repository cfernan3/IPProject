global switch_port_mac_dict
switch_port_mac_dict = {'00:00:ca:57:68:71:82:4f':{'1':'fa:16:3e:00:72:f1','2':'fa:16:3e:00:45:c0','3':'fa:16:3e:00:1c:99','4':'fa:16:3e:00:1e:94'},
                        '00:00:ee:2c:ef:87:1f:46':{'1':'fa:16:3e:00:2f:12','2':'fa:16:3e:00:8f:20','3':'fa:16:3e:00:56:02'}
                        }

sw2 = '00:00:ee:2c:ef:87:1f:46'
sw1 = '00:00:ca:57:68:71:82:4f'

global switch_port_mat
global switch_number_dpid
dpid_switch_number = {sw1:0,sw2:1}
switch_number_dpid = {0:sw1,1:sw2}
switch_port_mat = [[0,'3'],
                   ['3',0]]

#dictionary of switches with key = dpid
global switch_dict
switch_dict = {}

global paths
paths = {sw1:{sw2:[[0,1]]}}




