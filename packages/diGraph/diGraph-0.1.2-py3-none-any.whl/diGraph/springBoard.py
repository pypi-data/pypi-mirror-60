import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import random as r



from .node import *




class SpringBoard(object):
    '''
    SpringBoard object
    '''
    def __init__(self, nodesDict:dict, k:float, Q:float):
        '''
        nodes - an adjacency dictionary of first positive integers
        k - coefficient of spring
        Q - coefficient of electric field
        '''

        # create a bidirectional dictionary of nodes (numbers) that do not
        # contain self-maps
        graphNodesDict = {}
        for nodeA in nodesDict:
            connectedToA = lambda nodeB : (nodeA in nodesDict[nodeB]) or (nodeB in nodesDict[nodeA])
            graphNodesDict[nodeA] = [nodeB for nodeB in nodesDict if (connectedToA(nodeB) and nodeA != nodeB)]

        # initialize the list of nodes
        self.nodes = [Node(ID + 1) for ID in range(len(nodesDict))]

        # add connections to nodes using dictionary
        for nodeA in self.nodes:
            nodeA.addConnections([self.nodes[nodeB - 1] for nodeB in graphNodesDict[nodeA.ID]])

        # set spring and field constants
        self.k = k
        self.Q = Q

        # add positions to nodes
        for (node, i) in zip(self.nodes,range(len(self.nodes))):
            arg = 2 * np.pi * i / len(nodesDict)
            node.setCoord(np.array([np.cos(arg), np.sin(arg)]))

    def _increment(self, deltaT:float):
        '''
        increments the timestep simulation by one step
        deltaT - simulation time step
        '''
        for node in self.nodes:

            # add the spring forces
            for connection in node.connections:
                deltaD = deltaT**2 * self.k * (1 - node.distanceTo(connection)) / node.degree
                vec = node.pos - connection.pos
                vec *= deltaD / np.sqrt(vec[0]**2 + vec[1]**2)
                node.displacement += vec

            # add the repellant forces
            for other in self.nodes:
                if not node.equals(other):
                    deltaD = self.Q * (deltaT / node.distanceTo(other))**2 * other.degree
                    vec = other.pos - node.pos
                    vec *= deltaD / np.sqrt(vec[0]**2 + vec[1]**2)
                    node.displacement += vec

            # add universal force
            node.displacement += -1 * node.pos / np.sqrt(sum(node.pos**2)) * node.degree * .001

        # finalize displacements
        for node in self.nodes:
            node.setDisplacement()

    def move(self, deltaT:float, n:int):
        '''
        Iterate _increment()
        deltaT - simulation time step
        n - number of time steps
        '''
        for i in range(n):
            self._increment(deltaT)

    def plot(self, saveAs:str='_'):
        '''
        Plot the graph.
        saveAs - (optional) file path to save
        '''
        fig, ax = plt.subplots(figsize=(7,7))
        ax.set_aspect('equal')
        ax.autoscale()
        for node in self.nodes:
            x = [node.pos[0] for node in self.nodes]
            y = [node.pos[1] for node in self.nodes]
        ax.plot(x,y,'o');
        for node in self.nodes:
            for connection in node.connections:
                ax.annotate('', xytext=node.pos,xy=connection.pos,
                            arrowprops={'arrowstyle': '-'}, va='center')
        plt.show();
        if saveAs != '_':
            plt.savefig(saveAs)

    def move_plot_save(self, deltaT:float, n:int, saveAs:str):
        '''
        Move forward in simulation and save image after each timestep
        deltaT - simulation time step
        n - number of time steps
        saveAs - folder path to save images
        '''
        for i in range(n):
            self.plot(f'{saveAs}/{i}');
            self._increment(deltaT)
        self.plot(f'{saveAs}/{n}')

    def settle(self, deltaT:float):
        '''
        Increment timestep simulation until objects have settled
        deltaT - simulation time step
        '''
        sumDiff = 1 # > 0.05
        while sumDiff > 0.05:
            last = {node.ID: node.pos for node in self.nodes}
            self.move(deltaT,500)
            sumDiff = sum([abs(node.pos[0] - last[node.ID][0]) + abs(node.pos[1] - last[node.ID][1]) for node in self.nodes])

    def random_reset(self):
        '''
        Randomly reset node positions
        '''
        for node in self.nodes:
            node.pos = np.array([r.uniform(0,1), r.uniform(0,1)])
