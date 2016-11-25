#!/usr/bin/python
from Topo_Specs import switch_port_mac_dict as mac_dict,dpid_switch_number as sw_num,switch_port_mat, switch_number_dpid as sw_dpid, switch_dict
#from QoSApplication import switch_dict
from Dijkstra2 import test_Dijkstra as tD
from threading import Timer
from collections import defaultdict
import requests
flow_pusher_url = "http://localhost:8080/wm/staticentrypusher/json"

#Stats Collector imports
import json
import requests
import time
import threading

# dictionary of switches with key = dpid
global switch_dict
switch_dict = {}


class RouteManagement():
    flow_counter = 0
    cost_matrix = []
    t = None    #thread

    def createCostMatrix(self):
        try: #Check if sw_num and switch_dict exist
            switch_dict and sw_num
        except:
            print("Check switch topology specs. Something missing.")
            return
        for egress_sw in sw_num:
            for ingress_sw in sw_num:
                egress_cost = switch_dict[egress_sw]['port'][switch_port_mat[sw_num[egress_sw]][sw_num[ingress_sw]]]['bandwidth']
                ingress_cost = switch_dict[ingress_sw]['port'][switch_port_mat[sw_num[ingress_sw]][sw_num[egress_sw]]]['bandwidth']
                try: egress_cost != ingress_cost
                except:
                    print("Ingress and Egress cost not equal on Egress Switch='"+egress_sw+"' and Ingress Switch='"+ingress_sw+"'")
                    break
                else: self.cost_matrix[sw_num[egress_sw]][sw_num[ingress_sw]] = egress_cost
                ##Check this function

    def calculatePath(self):
        path = tD()
        flows = self.createFlow(path)
        self.flowPusher(flows)
        return

    def createFlow(self, path):
        flows = defaultdict(list)
        dst = len(path)-1
        for i in range(dst):
            forward_flow_egress_port = switch_port_mat[path[i]][path[i+1]]
            backward_flow_egress_port = switch_port_mat[path[i+1]][path[i]]
            dst_ingress_port_mac = switch_dict[sw_dpid[path[dst]]]['port'][switch_port_mat[path[dst]][path[dst-1]]]['mac']
            src_egress_port_mac = switch_dict[sw_dpid[path[0]]]['port'][switch_port_mat[path[0]][path[1]]]['mac']
            forward_flow = '{"switch":"'+sw_dpid[path[i]]+'","name":"'+str(self.flow_counter)+'", "eth_dst":"'+dst_ingress_port_mac+'", "actions":"output="'+forward_flow_egress_port+'"}'
            self.flow_counter += 1
            backward_flow = '{"switch":"'+sw_dpid[path[i+1]]+'","name":"'+str(self.flow_counter)+'", "eth_dst":"'+src_egress_port_mac+'", "actions":"output="'+backward_flow_egress_port+'"}'
            self.flow_counter += 1
            flows[sw_dpid[path[i]]].append(forward_flow)
            flows[sw_dpid[path[i+1]]].append(backward_flow)
        return flows

    def flowPusher(self, flows):
        #Asumming flows to be a list of flow dictionaries, each dictionary having two keys, switch name and flow string
        for switch in flows.keys():
            for flow in flows[switch]
            requests.post(flow_pusher_url, params={#parameters dictionary here})
            #Push flow here

    def program_run(self,interval):
        global t
        t = Timer(interval, self.program_run(interval))
        t.daemon = True
        t.start()
        route_manager = RouteManagement()
        route_manager.createCostMatrix()
        route_manager.calculatePath()

    def program_stop(self):
        self.t.cancel()
        print("Stopping Route Manager ...")


def stats_collector():
    # hello
    # REST API call to get switch-details
    req_get_switch_details = requests.get('http://129.7.98.24:8080/wm/core/controller/switches/json')
    # parse json
    switch_details_json = json.loads(req_get_switch_details.text)
    # store switch details for each switch
    for switch in switch_details_json:
        switch_dict[switch['switchDPID']] = {'ports': {}}
        # get port details
        port_details_req = requests.get('http://129.7.98.24:8080/wm/core/switch/' + switch['switchDPID'] + '/port/json')
        port_details_json = json.loads(port_details_req.text)
        port_dict = {}
        # print (port_details_json['port_reply'][0]['port'][0])
        # store details for each port
        for port in port_details_json['port_reply'][0]['port']:
            port_dict[port['port_number']] = {'bandwidth_util': 0, 'time': int(time.time()),
                                              'tx': int(port['transmit_bytes']), 'rx': int(port['receive_bytes'])}
            switch_dict[switch['switchDPID']]['ports'].update(port_dict)

    # get mac and ip for every port for each switch
    r = requests.get('http://129.7.98.24:8080/wm/device/')
    data = json.loads(r.text)
    devices = data['devices']
    for entity in devices:
        # print(entity)
        dpid = entity['attachmentPoint'][0]['switch']
        port = entity['attachmentPoint'][0]['port']
        ip = entity['ipv4'][0]
        mac = entity['mac'][0]
        print(dpid, port, ip, mac)
        # store
        d = {'mac': mac, 'ip': ip}
        switch_dict[dpid]['ports'][port].update(d)

    print(switch_dict)


    # input params: vertex id of both switches
    '''def create_flow(a, b, port_matrix, dpid_arr, isQoS):
            #actual stuff comented out to test
            dpid_a = '00:00:ca:57:68:71:82:4f' #dpid_arr[a]
            dpid_b = '00:00:ee:2c:ef:87:1f:46' #dpid_arr[b]
            egress_port = '2' #port_matrix[a][b] #egress on switch a
            ingress_port = '1' #port_matrix[b][a] #ingress on switch b
            dest_mac = switch_dict[dpid_b]['ports'][ingress_port]['mac']
            forward_flow = '{"switch":"'+dpid_a + '","name":"' + "test" + '", "eth_dst":"' + dest_mac +'", "actions":"output=' + egress_port +'"}'
            return forward_flow
        '''

    # flow = create_flow(1,3,[], [], False)
    # print(flow)

    # computes bandwidth utilization and updates the value of 'bandwodth_utilization' in the switch_dict for every port of every switch
    def computeStats():

        dest_mac = switch_dict

        curr_time = int(time.time())
        for switch in switch_dict:
            # store_port stats
            print "-----------"
            print "switch_dpid:", switch
            port_stats = {}
            # get current_port_stats
            port_details_req = requests.get('http://129.7.98.24:8080/wm/core/switch/' + switch + '/port/json')
            port_details_json = json.loads(port_details_req.text)
            for port in port_details_json['port_reply'][0]['port']:
                port_stats[port['port_number']] = {'tx': int(port['transmit_bytes']), 'rx': int(port['receive_bytes'])}

            ports = switch_dict[switch]['ports']
            for port in ports:
                prev_tx = ports[port]['tx']
                prev_rx = ports[port]['rx']
                # calculate bw
                bw = float(port_stats[port]['tx'] + port_stats[port]['rx'] - prev_tx - prev_rx) / (
                curr_time - ports[port]['time'])
                # print(int(port_stats[port]['tx']))
                # print(int(port_stats[port]['rx']))
                # print(curr_time)

                bw = float(bw / 1000 / 125)
                bw = int((bw * 100) + 0.5) / 100.0
                ports[port]['bandwidth_util'] = bw
                ports[port]['tx'] = port_stats[port]['tx']
                ports[port]['rx'] = port_stats[port]['rx']
                ports[port]['time'] = curr_time
                # print "port id\t", port, "\tbandwidth_util\t", bw, "\tMbits/sec"
                print "port id\t\t", port, "\tbandwidth_util\t", ports[port]['bandwidth_util'], "\tMbits/sec"
            print "-----------"
        #print switch_dict

    class StatsManager(threading.Thread):

        def __init__(self, delay):
            threading.Thread.__init__(self)
            self.delay = delay

        def run(self):
            count = 0
            while True:
                time.sleep(self.delay)
                print(count)
                computeStats()
                count += 1

    class FlowManager():
        flow_dict = {}

        def push_flow(self, flow):
            # push a flow
            r = requests.post('http://129.7.98.24:8080/wm/staticentrypusher/json', data=flow)
            print r

        def update_flow(self, list):
            for flow in list:
                push_flow(flow)

        def clear_flow(self, switch):
            # clear all flows on the switch
            r = requests.get('http://129.7.98.24:8080/wm/staticentrypusher/clear/' + switch + '/json')

    stat_collector_thread = StatsManager(1)
    stat_collector_thread.daemon = True
    stat_collector_thread.start()

    while True:
        time.sleep(1)

    # flow_manager = FlowManager()
    # flow = '{"switch":"00:00:92:15:ed:4f:ff:49","name":"flow-mod-1", "active":"true", "eth_dst":"fa:16:3e:00:4a:ca", "actions":"output=2"}'
    switch = '00:00:92:15:ed:4f:ff:49'
    # flow_manager.clear_flow(switch)
    # flow_manager.push_flow(flow)

    # flow_manager.clear_flow(switch)



if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    stats_collector()
    route_manager = RouteManagement()
    route_manager.program_run(5)
