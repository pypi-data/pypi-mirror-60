import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as ptc
import random as r









class Node(object):
    '''
    Node object
    '''
    def __init__(self, ID:int=-1, connections:list=None, pos:np.array=None):
        '''
        Initialize Node object.

        ID - node identifier
        connections - list of connected nodes
        pos - (x,y) position of node
        '''
        self.ID = ID
        self.connections = [] if connections == None else connections
        self.degree = 0 if connections == None else len(connections)
        self.pos = np.array([0.0,0.0]) if pos == None else pos
        self.displacement = np.array([0.0,0.0])

    def setCoord(self, pos:np.array):
        '''
        Set node position
        :param pos: (x,y) position of node
        '''
        self.pos = pos

    def setDisplacement(self):
        '''
        Add displacement to node position
        '''
        self.pos += self.displacement
        self.displacement = np.array([0.0,0.0])

    def addConnection(self, connection):
        '''
        Add connection to node and update the node degree
        connection - connected node
        '''
        self.connections += [connection]
        self.degree += 1

    def addConnections(self, connections:list):
        '''
        Add connection to node and update the node degree
        connection - list of connected nodes
        '''
        self.connections += connections
        self.degree += len(connections)

    def distanceTo(self, node):
        '''
        Return distance to node
        node - Node object
        '''
        return np.sqrt((self.pos[0]-node.pos[0])**2 + (self.pos[1]-node.pos[1])**2)

    # how would you check the connections being equal?
    def equals(self, node):
        '''
        Return if equal to node
        node - Node object
        '''
        boolID = self.ID == node.ID
        boolPos = all(self.pos == node.pos)
        boolDegree = self.degree == node.degree
        return boolID and boolPos and boolDegree

    def __repr__(self):
        '''
        retrurn string representation of (self) node
        '''
        return f'<Node {self.ID} @ ({round(self.pos[0],3)},{round(self.pos[1],3)})>'
