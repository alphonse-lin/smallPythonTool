precision = 3

class Graph():
    def __init__(self, edgeLists=None):
        self.vertices = {}   # {(): [], (): [], ...}, record all the edges connected to each vertice; edges are represented by index
        self.edges = []   # [[(), ()], [(), ()], ...], only to record the head and tail point of each multiline
        self.edgeAttrs = []
        if edgeLists is not None:
            for i in range(len(edgeLists)):
                this_list = edgeLists[i]
                if self.__isMultiline(this_list):
                    for inner_list in this_list:
                        self.addEdge(inner_list)
                else:
                    self.addEdge(this_list)

    def __isMultiline(self, line):
        first_point = line[0]
        return type(first_point[0]) == list

    def addEdge(self, edgeList):
        headPoint = edgeList[0]
        tailPoint = edgeList[-1]
        headPoint = tuple([round(x, precision) for x in headPoint])
        tailPoint = tuple([round(x, precision) for x in tailPoint])
        self.edges.append([headPoint, tailPoint])
        self.edgeAttrs.append({"geometry": [tuple([round(x[0], precision), round(x[1], precision)]) for x in edgeList],
                               "visited": False})

        currentEdgeNum = len(self.edges) - 1
        self.vertices.setdefault(headPoint, [])
        self.vertices[headPoint].append(currentEdgeNum)
        self.vertices.setdefault(tailPoint, [])
        self.vertices[tailPoint].append(currentEdgeNum)

    def __findAnotherVerticeOfEdge(self, e, v):
        this_edge = self.edges[e]
        if (this_edge[0] == v):
            return this_edge[1]
        else:
            return this_edge[0]

    def findDegree(self, v):
        if self.vertices.get(v) is None:
            return 0
        else:
            return len(self.vertices[v])

    def isCrosspoint(self, v):
        if self.vertices.get(v) is None:
            return False
        elif len(self.vertices[v]) > 2:
            return True
        else:
            return False

    def setAllEdgeUnvisited(self):
        for i in range(len(self.edgeAttrs)):
            self.edgeAttrs[i]["visited"] = False

    def setEdgeVisited(self, e):
        self.edgeAttrs[e]["visited"] = True

    def edgeIsVisited(self, e):
        return self.edgeAttrs[e]["visited"]

    def getEdgeGeometry(self, e):
        return self.edgeAttrs[e]["geometry"]

    def __searchSingleWholeLine(self, head, edge):
        current_vertice = self.__findAnotherVerticeOfEdge(edge, head)
        line_list = [edge]
        self.setEdgeVisited(edge)
        while self.findDegree(current_vertice) == 2:
            this_all_edges = self.vertices[current_vertice]
            non_visited_edge = [x for x in this_all_edges if not self.edgeIsVisited(x)][0]
            line_list.append(non_visited_edge)
            current_vertice = self.__findAnotherVerticeOfEdge(non_visited_edge, current_vertice)
            self.setEdgeVisited(non_visited_edge)

        # Connect all edges into a single consecutive linestring
        line_geom_list = self.getEdgeGeometry(line_list[0])
        if len(line_list) > 1:   # Avoid overflow of the list
            next_edge = self.edges[line_list[1]]
            if line_geom_list[0] in next_edge:   # The head point of the first edge should not appear in the next edge. Otherwise, it needs processing
                if len(line_list) > 2:
                    line_geom_list = list(reversed(line_geom_list))
                else:
                    head_degree = self.findDegree(line_geom_list[0])   # Deal with the situation when the single line consists of only two lines, which consitutes a ring
                    tail_degree = self.findDegree(line_geom_list[-1])
                    if head_degree < tail_degree:
                        line_geom_list = list(reversed(line_geom_list))

        for i in range(1, len(line_list)):
            this_edge_id = line_list[i]
            this_edge = self.edges[this_edge_id]
            this_geom_list = self.getEdgeGeometry(this_edge_id)

            last_tail = line_geom_list[-1]
            if last_tail == this_edge[0]:
                line_geom_list.extend(this_geom_list[1:])
            else:
                reversed_list = list(reversed(this_geom_list[:-1]))
                line_geom_list.extend(reversed_list)
        return line_geom_list

    def arrangeIntoWholeLines(self):
        crosspoints = [x for x in self.vertices.keys() if self.findDegree(x) > 2]
        self.setAllEdgeUnvisited()
        all_whole_lines = []
        for i in range(len(crosspoints)):
            this_crosspoint = crosspoints[i]
            this_edges = self.vertices[this_crosspoint]
            for this_edge in this_edges:
                if not self.edgeIsVisited(this_edge):
                    new_whole_line = self.__searchSingleWholeLine(this_crosspoint, this_edge)
                    all_whole_lines.append(new_whole_line)
        return all_whole_lines
