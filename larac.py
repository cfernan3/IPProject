from Dijkstra2 import dijkstra_larac, Graph2,

def find_cost(path):
    return

def find_delay(path):
    return

def larac(s,t,c,d,deltadelay):
    pc = dijkstra_larac(s, t, c)    #pc = path
    if find_delay(pc)<=deltadelay:
        return pc
    pd = dijkstra_larac(s, t, d)
    if find_delay(pd) > deltadelay:
        return "There is no solution"
    while 1:
        lamda = (find_cost(pc)-find_cost(pd))/(find_delay(pd)-find_delay(pc))
        c_lamda = c + lamda*d
        r = dijkstra_larac(s, t, c_lamda)
        if