from gurobipy import *
import random
import pandas as pd
import math
import numpy as np
import csv
import random
import matplotlib.pyplot as plt
import networkx as nx

# #-------------------------------------------------------#
# #                 defining set                          #
# #-------------------------------------------------------#
K = 3
C= range(K)

df = pd.read_csv("ukfaculty.csv")
V =list()
d_ij = {}

counter = 1
for index, row in df.iterrows():
    V.append(row[0])
    counter2 = 1
    for element in row[1:]:
        d_ij[counter,counter2] = element
        counter2 +=1
    counter +=1

E = list()
df = pd.read_csv("edgelist.csv")
for index, row in df.iterrows():
    E.append((row[1], row[2]))

print("E:", E)

# #-------------------------------------------------------#
# #                 defining variable                     #
# #-------------------------------------------------------#

Y_ij, X_ic = {}, {}
graph_coloring = Model()
for c in C:
    for i in V:
        X_ic[i,c] = graph_coloring.addVar(vtype=GRB.BINARY, lb=0, ub=1, name="X_ic[%s, %s]" % (i,c))

for i in V[:-1]:
    for j in range(i+1, V[-1]+1):
        Y_ij[i,j] = graph_coloring.addVar(vtype=GRB.CONTINUOUS, lb=0, name="Y_ij[%s,%s]" % (i,j))

# #-------------------------------------------------------#
# #                 defining constraints                     #
# #-------------------------------------------------------#

for i in V:
    graph_coloring.addConstr(quicksum(X_ic[i,c] for c in C) == 1, name= 'const1')

for c in C:
    graph_coloring.addConstr(quicksum(X_ic[i,c] for i in V) >= 1, name= 'const2')

for i in V[:-1]:
    for j in range(i+1, V[-1]+1):
        for c in C:
            graph_coloring.addConstr(Y_ij[i,j] >= X_ic[i,c] +X_ic[j,c]-1, name='const3')

graph_coloring.setObjective(quicksum(d_ij[i,j]*Y_ij[i,j] for i in V[:-1] for j in range(i+1, V[-1]+1)), GRB.MINIMIZE)

graph_coloring.update()
graph_coloring.optimize()

val_map = {}
for c in C:
    for i in V:
        if X_ic[i,c].x >0:
            # print("X_ic[%s, %s]:" % (i,c), X_ic[i,c].x, "colour type:", c)
            val_map[i] = c

G = nx.Graph()
G.add_nodes_from([i for i in V])
G.add_edges_from([(i, j, {'weight': d_ij[i, j]}) for (i,j) in E])

values = [val_map.get(node) for node in G.nodes()]
nx.draw(G, cmap=plt.get_cmap('viridis'), node_color=values, with_labels=True, node_size=40,width= 0.1, font_color='black', font_size = '6')
plt.show()