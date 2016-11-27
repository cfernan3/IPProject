#!/usr/bin/python

import json
import requests
import time
import threading
import thread

#from RouteManagement import RouteManagement
# dictionary of switches with key = dpid
global switch_dict
switch_dict = {}

#from formerly route management.py
from Topo_Specs_General import switch_port_mac_dict as mac_dict,dpid_switch_number as sw_num,switch_port_mat, switch_number_dpid as sw_dpid, switch_dict, paths as path_list
#from QoSApplication import switch_dict
from Dijkstra2 import test_Dijkstra as tD
from threading import Timer
from collections import defaultdict
import requests
flow_pusher_url = "http://127.0.0.1:8080/wm/staticentrypusher/json"

def main():
    # hello
    # REST API call to get switch-details
    req_get_switch_details = requests.get('http://127.0.0.1:8080/wm/core/controller/switches/json')
    # parse json
    switch_details_json = json.loads(req_get_switch_details.text)
    # store switch details for each switch
    for switch in switch_details_json:
        switch_dict[switch['switchDPID']] = {'ports': {}}
        # get port details
        port_details_req = requests.get('http://127.0.0.1:8080/wm/core/switch/' + switch['switchDPID'] + '/port/json')
        port_details_json = json.loads(port_details_req.text)
        port_dict = {}
        # print (port_details_json['port_reply'][0]['port'][0])
        # store details for each port
        for port in port_details_json['port_reply'][0]['port']:
            port_dict[port['port_number']] = {'bandwidth_util': 0, 'time': int(time.time()),
                                              'tx': int(port['transmit_bytes']), 'rx': int(port['receive_bytes']),'link_util':0}
            switch_dict[switch['switchDPID']]['ports'].update(port_dict)

    # get mac and ip for every port for each switch
    r = requests.get('http://127.0.0.1:8080/wm/device/')
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

    #print(switch_dict)


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
            #print "-----------"
            #print "switch_dpid:", switch
            port_stats = {}
            # get current_port_stats
            port_details_req = requests.get('http://127.0.0.1:8080/wm/core/switch/' + switch + '/port/json')
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
                if int(bw) is not 0:
                    l_util = float((bw - 7)/bw)
                else:
                    l_util = 0
                ports[port]['bandwidth_util'] = bw
                ports[port]['tx'] = port_stats[port]['tx']
                ports[port]['rx'] = port_stats[port]['rx']
                ports[port]['time'] = curr_time
                ports[port]['link_util'] = l_util
                # print "port id\t", port, "\tbandwidth_util\t", bw, "\tMbits/sec"
                #print "port id\t\t", port, "\tbandwidth_util\t", ports[port]['bandwidth_util'], "\tMbits/sec"
            #print "-----------"
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
            r = requests.post('http://127.0.0.1:8080/wm/staticentrypusher/json', data=flow)
            print r

        def update_flow(self, list):
            for flow in list:
                push_flow(flow)

        def clear_flow(self, switch):
            # clear all flows on the switch
            r = requests.get('http://127.0.0.1:8080/wm/staticentrypusher/clear/' + switch + '/json')

    stat_collector_thread = StatsManager(1)
    stat_collector_thread.daemon = True
    stat_collector_thread.start()

    while True:
        time.sleep(1)

    # flow_manager = FlowManager()
    # flow = '{"switch":"00:00:ca:57:68:71:82:4f","name":"flow-mod-1", "active":"true", "eth_dst":"fa:16:3e:00:4a:ca", "actions":"output=2"}'
    switch = '00:00:92:15:ed:4f:ff:49'
    # flow_manager.clear_flow(switch)
    # flow_manager.push_flow(flow)

    # flow_manager.clear_flow(switch)

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
            dst_ingress_port_mac = mac_dict[sw_dpid[path[-1]]][switch_port_mat[path[-1]][path[-2]]]
            src_egress_port_mac = mac_dict[sw_dpid[path[0]]][switch_port_mat[path[0]][path[1]]]
            forward_flow = '{"switch":"'+sw_dpid[path[i]]+'","name":"'+str(self.flow_counter)+'", "eth_dst":"fa:16:3e:00:7a:32", "actions":"output='+forward_flow_egress_port+'"}'
            self.flow_counter += 1
            print "forward flow: src=",path[i],", dst=",path[i+1],", flow = ",forward_flow
            backward_flow = '{"switch":"'+sw_dpid[path[i+1]]+'","name":"'+str(self.flow_counter)+'", "eth_dst":"fa:16:3e:00:44:1f", "actions":"output='+backward_flow_egress_port+'"}'
            self.flow_counter += 1
            flows[sw_dpid[path[i]]].append(forward_flow)
            flows[sw_dpid[path[i+1]]].append(backward_flow)
        return flows

    def createEndpointFlow(self,src,dst):
        flows = defaultdict(list)
        flow = '{"switch":"00:00:22:67:d7:d5:d4:48","name":"0", "eth_dst":"fa:16:3e:00:44:1f", "actions":"output=4"}'
        flows[sw_dpid[src]].append(flow)
        flow = '{"switch":"00:00:22:67:d7:d5:d4:48","name":"1", "eth_dst":"fa:16:3e:00:7f:f0", "actions":"output=2"}'
        flows[sw_dpid[src]].append(flow)
        flow = '{"switch": "00:00:da:e7:78:d1:30:44", "name": "2", "eth_dst": "fa:16:3e:00:7a:32", "actions": "output=2"}'
        flows[sw_dpid[dst]].append(flow)
        self.flow_counter+=3
        return


    def flowPusher(self, flows):
        #Asumming flows to be a list of flow dictionaries, each dictionary having two keys, switch name and flow string
        for switch in flows.keys():
            for flow in flows[switch]:
                r = requests.post(flow_pusher_url, data = flow)
                #Push flow here
        return r

    def program_run(self,interval):
        global t
        t = Timer(interval, self.program_run, args=[interval])
        t.daemon = True
        t.start()
        route_manager = RouteManagement()
        route_manager.createCostMatrix()
        route_manager.calculatePath()

    def program_stop(self):
        self.t.cancel()
        print("Stopping Route Manager ...")

    def FCpath(self,switch_dict, src, dst): #Dmax = length of longest path i.e. maximum number of hops
        #print switch_dict
        min_cost_path = []
        min_cost  = 10000
        Dmax=6
        for path in path_list[sw_dpid[src]][sw_dpid[dst]]:
            cost = 0
            for i in range(len(path) - 1):
                egress_sw = sw_dpid[path[i]]
                ingress_sw = sw_dpid[path[i + 1]]
                #print path
                #print switch_dict
                #print "egress_sw=", egress_sw, "ingress_sw=", ingress_sw, "port = " ,switch_port_mat[sw_num[egress_sw]][sw_num[ingress_sw]]
                #try:
                cost += switch_dict[egress_sw]['ports'][switch_port_mat[sw_num[egress_sw]][sw_num[ingress_sw]]]['link_util']
                #except:
                cost += 1
            #print path
            #print "cost=",cost
            #print "min cost=",min_cost
            if cost< min_cost and (len(path)-1)< Dmax:
                min_cost = cost
                min_cost_path = path
        if len(min_cost_path):
            return min_cost_path
        else:
            return "No path found"



if __name__ == "__main__":
    # stuff only to run when not called via 'import' here
    route_manager = RouteManagement()
    thread.start_new_thread(main,())
    time.sleep(10)
    while(1):
        #print switch_dict
        #print "Yes"
        endpoint_flows = route_manager.createEndpointFlow(0,3)
        r = route_manager.flowPusher((endpoint_flows))
        print r
        fcpath = route_manager.FCpath(switch_dict,0,3)
        #print fcpath
        flows = route_manager.createFlow(fcpath)
        print flows
        r = route_manager.flowPusher(flows)
        print r
        time.sleep(5)
