# -*- coding: utf-8 -*-
"""
Created on Mon Dec 17 14:37:08 2018
@author: KressinL

In diesem Skript werden Eigenschaften des bipartiten Graphen und seiner Struktur
visualisiert.
"""
import os
import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms import bipartite as bi
from matplotlib import pyplot as plt
import pickle
import random

# Laden des bipartiten Graphen
with open('B', 'rb') as B_file:
    B = pickle.load(B_file)

# Aufteilung der unterschiedlichen Knotentypen (Syllabi, Referenzen) auf 2 Variablen.
plaene = [x for x,y in B.nodes(data=True) if y['bipartite']==0]
lit = [x for x,y in B.nodes(data=True) if y['bipartite']==1]

# projected Graph der Lehrpläne erstellen 
planB = bi.weighted_projected_graph(B, plaene,ratio=False)
# der Referenzen
graphR = bi.weighted_projected_graph(B, lit,ratio=False)

# =============================================================================
# Illustrative künstliche Beispielmatrizen für die Darstellung der 
# Ko-Zitation und der bibliographischen Kopplung
# =============================================================================
# Erstellung der Adjencymatrix der Syllabi
MplanBgew = nx.adjacency_matrix(planB, weight='weight')
MplanBgew = pd.DataFrame(MplanBgew.todense())

# Benennung der Achsen der Matrix mit Kurstiteln.
MplanBgew.columns = [y for x,y in list(planB.nodes(data='Kurstitel'))]
MplanBgew.index = [y for x,y in list(planB.nodes(data='Kurstitel'))]
# willkürlicher Beispielausschnitt zur Darstellung
mbspplan = MplanBgew.iloc[23:27, 23:27]

mbspplan.to_csv("20192801_Besp_AM_Plaene.csv", header=True, encoding='utf-8-sig', index=True)
# In Artikeln werden Tabellen jedes Mal mithilfe der folgenden seite bearbeitet:
# http://www.tablesgenerator.com/latex_tables, um sie anschliessend in Latex-Dokumente
# einfügen zu können.

# Das gleiche noch mal Referenzen und ihrer Matrix.
Mref = nx.adjacency_matrix(graphR, weight='weight')
Mref = pd.DataFrame(Mref.todense())

Mref.columns = lit
Mref.index = lit
mbspref = Mref.iloc[54:58, 54:58]
mbspref.to_csv("20192801_Besp_AM_Ref.csv", header=True, encoding='utf-8-sig', index=True)

# =============================================================================
#                   bipartiten Graph zeichnen
# ============================================================================
pos = dict()
pos.update( (n, (1, i + 100 + i*2)) for i, n in enumerate(plaene) ) # put nodes from X at x=1
pos.update( (n, (2, i)) for i, n in enumerate(lit) ) # put nodes from Y at x=2
plt.figure(figsize=(10,10))
nodes1 = nx.draw_networkx_nodes(B, pos=pos, nodelist= plaene, node_color = 'y', node_shape = 'h', node_size = 100)
nodes2 = nx.draw_networkx_nodes(B, pos=pos, nodelist= lit, node_color = 'b', node_shape ='o', node_size = 100)
nodes1.set_edgecolor('k')
nodes2.set_edgecolor('k')
nodes1.set_linewidth(0.1)
nodes2.set_linewidth(0.1)
nx.draw_networkx_edges(B, pos=pos, width=0.05)
plt.axis('off')
plt.savefig('20192801_bipartiter_Graph.pdf')
plt.show()
