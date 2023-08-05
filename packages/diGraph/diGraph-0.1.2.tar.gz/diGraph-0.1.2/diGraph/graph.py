import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import random as r





from .node import *
from .springBoard import *




class Graph(object):
    '''
    Graph object
    '''
    def __init__(self, nodesDict:dict):
        '''
        Construct Graph object
        nodesDict - adjacency of first positive integers
        '''

        # check to make sure that the keys and values are not skipping any
        # positive integers and that they are the first positive integers
        testIDs = []
        for key in nodesDict:
            testIDs += [key] + [value for value in nodesDict[key]]
        if set(testIDs) != set(range(1,len(list(set(testIDs))) + 1)):
            raise ValueError('Error in node keys and values: ' +
                             'missing number or disallowed character.')

        # make sure that the nodes dictionary is bidirectional
        graphNodesDict = {}
        connectedToA = lambda nodeB : (nodeA in nodesDict[nodeB]) or (nodeB in nodesDict[nodeA])
        for nodeA in nodesDict:
            graphNodesDict[nodeA] = [nodeB for nodeB in nodesDict if (connectedToA(nodeB) and nodeA != nodeB)]

        # make adjacency matrix
        self.adjacencyMatrix = np.vstack([np.array([1 if nodeB in graphNodesDict[nodeA] else 0 for nodeB in graphNodesDict]) for nodeA in graphNodesDict]).T

        # use SpringBoard to find good coordinates
        self.springBoard = SpringBoard(graphNodesDict, 1, -1)
        self.springBoard.move(0.1, 8000)
        self._normalize_pos()

    def _normalize_pos(self):
        '''
        Normalize the positions springboard nodes for plotting
        '''
        # collect all X and Y coordinates
        X = [node.pos[0] for node in self.springBoard.nodes]
        Y = [node.pos[1] for node in self.springBoard.nodes]
        # sutract out minmum of each
        for node in self.springBoard.nodes:
            node.pos -= np.array([min(X), min(Y)])
        # recollect all X and Y coordinates
        X = [node.pos[0] for node in self.springBoard.nodes]
        Y = [node.pos[1] for node in self.springBoard.nodes]
        # Scale by a little more than the max of each collection, X and Y
        for node in self.springBoard.nodes:
            node.pos = np.array([node.pos[0]/(max(X) + 1), node.pos[1]/(max(Y) + 1)])

    def plot(self, saveAs:str='_'):
        '''
        Plot the Graph
        saveAs - (optional) a file path to save the plot
        '''
        fig, ax = plt.subplots(figsize=(7,7))
        plt.axis('off')
        ax.set_aspect('equal')
        r = 0.04
        for node in self.springBoard.nodes:
            X1, Y1 = node.pos[0], node.pos[1]
            # TODO: structure allows for other names, but circles won't adjust
            # add circle
            ax.add_artist(plt.Circle((X1,Y1), r, color='b', fill=False, clip_on=False))
            ax.text(X1, Y1, str(node.ID), fontsize=15, horizontalalignment='center', verticalalignment='center')
            # add lines per circle
            for connection in node.connections:
                # this makes each connection only graph once
                if node.ID < connection.ID:
                    X2, Y2 = connection.pos[0], connection.pos[1]
                    d = np.sqrt((X2-X1)**2 + (Y2-Y1)**2)
                    x = r * ((X2 - X1) / d)
                    y = r * ((Y2 - Y1) / d)
                    ax.annotate('', xytext=(X1 + x, Y1 + y), xy=(X2 - x, Y2 - y),  arrowprops={'arrowstyle': '-'})
        if saveAs != '_':
            plt.savefig(saveAs)

    def force(self, n:int):
        '''
        Move forward time step simulation
        n - number of time steps
        '''
        self.springBoard.move(0.1, n)
        self._normalize_pos()

    def random_reset(self):
        '''
        Randomly reset node positions and let time step simulation resettle
        '''
        self.springBoard.random_reset()
        self.springBoard.settle(0.1)
        self._normalize_pos()
