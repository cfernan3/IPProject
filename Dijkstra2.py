from pythonds.graphs import PriorityQueue, Graph, Vertex
from numpy import inf,nan

class Graph2(Graph):
    def addEdge(self,f,t,cost=0):
        if f not in self.vertices:
            nv = self.addVertex(f)
        if t not in self.vertices:
            nv = self.addVertex(t)
        self.vertices[f].addNeighbor(self.vertices[t],cost)
        self.vertices[t].addNeighbor(self.vertices[f],cost)


def get_path(aGraph, source, dest):
    cur_node = dest
    path = list([dest.id])
    while cur_node!=source:
        temp = cur_node.pred
        path.append(temp.id)
        cur_node = temp
    #path.append(source.id)
    return path

def getMin(queue):
    min = [nan,inf]
    for i in queue:
        if i.getDistance()<min[1]:
            min[0] = i
            min[1] = i.getDistance()
    queue.remove(min[0])
    return min[0]

def dijkstra2(aGraph,start):
    q = set([vertex for vertex in aGraph])
    start.setDistance(0)
    while len(q)>0:
        u = getMin(q)
        for neigh in u.getConnections():
            alt = u.getDistance() + u.getWeight(neigh)
            if alt < neigh.getDistance():
                neigh.setDistance(alt)
                neigh.setPred(u)

def show_graph(aGraph):
    g = aGraph
    print("Source Vertex=" + str(g.vertices[0].getDistance()))
    print("1st Vertex=" + str(g.vertices[1].getDistance()))
    print("2nd Vertex=" + str(g.vertices[2].getDistance()))
    print("3rd Vertex=" + str(g.vertices[3].getDistance()))
    print("4th Vertex=" + str(g.vertices[4].getDistance()))
    print("5th Vertex=" + str(g.vertices[5].getDistance()))
    print("6th Vertex=" + str(g.vertices[6].getDistance()))
    print("7th Vertex=" + str(g.vertices[7].getDistance()))
    print("8th Vertex=" + str(g.vertices[8].getDistance()))
    return

def gen_graph(cost_matrix):
    g = Graph2()
    length = len(cost_matrix)
    for i in range(length):
        for j in range(length):
            if cost_matrix[i][j]!=0:
                g.addEdge(i,j,cost_matrix[i][j])
    return g

def test_Dijkstra():
    cost_matrix = [[0, 4, 0, 0, 0, 0, 0, 8, 0],[4, 0, 8, 0, 0, 0, 0, 11, 0],[0, 8, 0, 7, 0, 4, 0, 0, 2],[0, 0, 7, 0, 9, 14, 0, 0, 0],[0, 0, 0, 9, 0, 10, 0, 0, 0],[0, 0, 4, 14, 10, 0, 2, 0, 0],[0, 0, 0, 0, 0, 2, 0, 1, 6],[8, 11, 0, 0, 0, 0, 1, 0, 7],[0, 0, 2, 0, 0, 0, 6, 7, 0]]
    #print(cost_matrix)
    g = gen_graph(cost_matrix)
    #print("Before Dijkstra-------------")
    #show_graph(g)
    dijkstra2(g,g.vertices[0])
    #print("After Dijkstra--------------")
    #show_graph(g)
    print(get_path(g,g.vertices[0],g.vertices[4]))
    return


