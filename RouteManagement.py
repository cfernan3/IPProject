from Topo_Specs import switch_port_mac_dict as mac_dict,dpid_switch_number as sw_num,switch_port_mat, switch_number_dpid as sw_dpid
from QoSApplication import switch_dict

class RouteManagement():
    flow_counter = 0
    cost_matrix = []

    def createCostMatrix(self):
        for egress_sw in sw_num:
            for ingress_sw in sw_num:
                egress_cost = switch_dict[egress_sw]['port'][switch_port_mat[sw_num[egress_sw]][sw_num[ingress_sw]]]['bandwidth']
                ingress_cost = switch_dict[ingress_sw]['port'][switch_port_mat[sw_num[ingress_sw]][sw_num[egress_sw]]]['bandwidth']
                try: egress_cost != ingress_cost
                except: "Ingress and Egress cost not equal on Egress Switch='"+egress_sw+"' and Ingress Switch='"+ingress_sw+"'"
                else: self.cost_matrix[sw_num[egress_sw]][sw_num[ingress_sw]] = egress_cost

    def calculatePath(self):


    def createFlow(self, path):
        flows = []
        dst = len(path)-1
        for i in range(dst):
            local_egress_port = switch_port_mat[path[i]][path[i+1]]
            dst_ingress_port = switch_port_mat[path[dst]][path[dst-1]]
            forward_flow = '{"switch":'+sw_dpid[path[i]]+',"name":'+str(self.flow_counter)+', "eth_dst":'+switch_dict[sw_dpid[path[dst]]]['port'][dst_ingress_port]['mac']+', "actions":"output='+local_egress_port+'"}'
            self.flow_counter += 1
            flows.append(forward_flow)
            flows.append(backward_flow)
        return flows