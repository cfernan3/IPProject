from Topo_Specs import switch_port_mac_dict as mac_dict,dpid_switch_number as sw_num,switch_port_mat, switch_number_dpid as sw_dpid, switch_dict, paths as path_list
#from QoSApplication import switch_dict
from Dijkstra2 import test_Dijkstra as tD
from threading import Timer
from collections import defaultdict
import requests
flow_pusher_url = "http://localhost:8080/wm/staticentrypusher/json"

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
            for flow in flows[switch]:
                requests.post(flow_pusher_url, params={})
                #Push flow here
        return

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

    def FCpath(self,switch_dict, src, dst): #Dmax = length of longest path i.e. maximum number of hops
        min_cost_path = []
        min_cost  = 10000
        Dmax=6
        for path in path_list[src][dst]:
            cost = 0
            for i in range(len(path) - 1):
                egress_sw = sw_dpid[path[i]]
                ingress_sw = sw_dpid[path[i + 1]]
                cost += switch_dict[egress_sw]['port'][switch_port_mat[sw_num[egress_sw]][sw_num[ingress_sw]]][
                    'link_util']
                cost += 1
            if cost< min_cost and (len(path)-1)< Dmax:
                min_cost = cost
                min_cost_path = path
        if not len(min_cost_path):
            return min_cost_path
        else:
            return "No path found"


route_manager = RouteManagement()
route_manager.program_run(5)
