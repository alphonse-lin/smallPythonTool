class union_find_tree:
    def __init__(self):
        self.myTree = {}
        self.children = {}
        self.rootSize = {}
        self.ancestor = {}

    def find_root(self, mypoint):
        if self.myTree[mypoint] == mypoint:
            return mypoint
        else:
            return self.find_root(self.myTree[mypoint])

    def add_new_vertice(self, p):
        self.myTree.setdefault(p, p)
        self.children.setdefault(p, [])
        self.rootSize.setdefault(p, 1)

    def new_father(self, p1, p2): # p2 is p1's father
        self.myTree[p1] = p2
        self.rootSize[p2] = self.rootSize[p2] + self.rootSize[p1]
        self.children[p2].append(p1)

    def union(self, myLine):
        p1 = myLine[0]
        p2 = myLine[1]
        self.add_new_vertice(p1)
        self.add_new_vertice(p2)
        p1_root = self.find_root(p1)
        p2_root = self.find_root(p2)
        if (p1_root != p2_root):
            if self.rootSize[p1_root] < self.rootSize[p2_root]:
                self.new_father(p1_root, p2_root)
            else:
                self.new_father(p2_root, p1_root)

    def find_all_roots(self):
        all_roots = [x for x in self.myTree.keys() if self.myTree[x] == x]
        return all_roots

    def find_all_descendants(self, myancestor, myroot):
        self.ancestor[myroot] = myancestor
        if len(self.children[myroot]) == 0:
            return [myroot]
        else:
            this_descendants = []
            for i in range(len(self.children[myroot])):
                this_child = self.children[myroot][i]
                this_descendants = this_descendants + self.find_all_descendants(myancestor, this_child)
            return this_descendants
