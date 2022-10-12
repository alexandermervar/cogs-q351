class HopfieldNetwork:
    #Supply either a num_nodes to initialize all weights and nodes to 1, 
    #or supply start_nodes and target_stable nodes for what nodes to begin from, and what the target stable state will be
    def __init__(self, num_nodes=None, start_nodes=None, target_stable=None):
        if num_nodes is not None:
            self.nodes = [1 for _ in range(num_nodes)]
            self.weights = []
            for row in range(num_nodes):
                layer = []
                for col in range(num_nodes):
                    layer.append(0 if row == col else 1)
                self.weights.append(layer)
        else:
            self.nodes = start_nodes
            self.weights = []
            for row in range(len(start_nodes)):
                layer = []
                for col in range(len(start_nodes)):
                    if(row == col):
                        layer.append(0)
                    else:
                        layer.append(target_stable[row] * target_stable[col])
                self.weights.append(layer)

    ##################
    #      TODO      #
    ##################
    """
    Update not at given index according to the hopfield update rule
    Return True or False if node was changed
    """
    def update_node(self, node):
        raise NotImplementedError

    ##################
    #      TODO      #
    ##################
    """
    Update nodes in ascending order repeatedly until stable state is achieved
    """
    def cycle_until_stable(self):
        raise NotImplementedError
    
    
    def print(self, print_weights=False):
        print("Nodes:", end='')
        for node in self.nodes:
            print(" " + str(node), end='')
        print("")
        if print_weights:
            print("Weight Matrix: ")
            for row in self.weights:
                for weight in row:
                    print(str(weight) + " ", end='')
                print("")

if __name__== "__main__":
    temp = HopfieldNetwork(3)
    temp.print(True)
    temp.cycle_until_stable()
    temp.print()
    print("Expect 1 1 1")
    print("\n")

    start_nodes2 = [1, -1, 1]
    target_stable2 = [1, 1, 1]
    temp2 = HopfieldNetwork(start_nodes=start_nodes2, target_stable=target_stable2)
    temp2.cycle_until_stable()
    temp2.print()
    print("Expect 1 1 1")
    print("\n")

    start_nodes3 = [1, -1, 1, 1]
    target_stable3 = [1, -1, 1, -1]
    temp3 = HopfieldNetwork(start_nodes=start_nodes3, target_stable=target_stable3)
    temp3.cycle_until_stable()
    temp3.print()
    print("Expect 1 -1 1 -1")
    print("\n")

    start_nodes4 = [1, -1, 1, 1, 1]
    target_stable4 = [1, -1, 1, -1, 1]
    temp4 = HopfieldNetwork(start_nodes=start_nodes4, target_stable=target_stable4)
    temp4.cycle_until_stable()
    temp4.print()
    print("Expect 1 -1 1 -1 1")
    print("\n")

    start_nodes4 = [1, -1, 1, 1, 1, 1, 1]
    target_stable4 = [1, -1, 1, -1, 1, 1, -1]
    temp4 = HopfieldNetwork(start_nodes=start_nodes4, target_stable=target_stable4)
    temp4.cycle_until_stable()
    temp4.print()
    print("Expect 1 -1 1 -1 1 1 -1")
    
