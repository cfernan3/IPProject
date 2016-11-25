from Dijkstra2 import dijkstra_larac, Graph2
from Topo_Specs import switch_dict
from Topo_Specs import switch_port_mac_dict as mac_dict,dpid_switch_number as sw_num,switch_port_mat, switch_number_dpid as sw_dpid


def find_cost(path):
    src = path[0]
    dst = path[-1]
    cost = 0
    for i in range(len(path)-1):
        egress_sw = sw_dpid[path[i]]
        ingress_sw = sw_dpid[path[i+1]]
        cost += switch_dict[egress_sw]['port'][switch_port_mat[sw_num[egress_sw]][sw_num[ingress_sw]]]['link_util']
        cost += 1
    return cost

def find_delay(path):
    return len(path)-1

def find_lamda_cost(path,lamda)
    return

def larac(s,t,c,d,Dmax):
    p_c = dijkstra_larac(s, t, c)    #p_c = path
    if find_delay(p_c)<=Dmax:
        return p_c
    p_d = dijkstra_larac(s, t, d)
    if find_delay(p_d) > Dmax:
        return "There is no solution"
    while 1:
        lamda = (find_cost(p_c)-find_cost(p_d))/(find_delay(p_d)-find_delay(p_c))
        r = dijkstra_larac(s, t, c+lamda*d)
        if find_lamda_cost(r,lamda) == find_lamda_cost(p_c,lamda):
            return p_d
        elif find_delay(r) <= Dmax:
            p_d = r
        else:
            p_c = r


