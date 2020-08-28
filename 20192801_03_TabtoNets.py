# -*- coding: utf-8 -*-
"""
Created on Sat Nov 10 17:17:18 2018
@author: KressinL

Hier sind alle Veranstaltungen der drei von mir aggregierten Jahrgänge drin, BA und verpflichtend.
In diesem Skript wird aus der Tabelle "Date_Ref_pro_Lehrplan" das bipartite Netzwerk geformt.
"""
import os
import pandas as pd
import networkx as nx
import pickle

# Einlesen der Tabelle, in der die pro Lehrplan gesplitte Literatur samt Metainformationen
# zu den Lehrplänen und zur Literatur enthalten ist.
mergedf = pd.read_csv("20192801_Ref_pro_Lehrplan.csv", index_col = False)

# Vorbereitung Uniname als nodeattribute
uni_att = mergedf[['recnr','uni']].drop_duplicates(subset='recnr')
uni_attsort = uni_att.sort_values(by=['recnr'])
# zur Tuple, das Datenformat, was der Code später erfordert
unidict= dict(zip(uni_attsort['recnr'], uni_attsort['uni']))

# Vorbereitung Reftyp als nodeattribute
Reftyp_att = mergedf[['Label','Reftyp']].drop_duplicates(subset='Label')
Reftyp_attsort = Reftyp_att.sort_values(by=['Label'])
# zur Tuple, das Datenformat, was der Code später erfordert
Reftypdict= dict(zip(Reftyp_attsort['Label'], Reftyp_attsort['Reftyp']))
# Vorbereitung meiner händisch vergebenen 'Unterkategorie' der Monographie
Mono_att = mergedf[['Label','Unterkat_Mono']].drop_duplicates(subset='Label')
Mono_attsort = Mono_att.sort_values(by=['Label'])
Monodict= dict(zip(Mono_attsort['Label'], Mono_attsort['Unterkat_Mono']))

# Vorbeiten der Kurs- und Modultitel und Kategorie als Attribute für die Lehrplannodes
kurst = mergedf[['recnr','kurstitel']].drop_duplicates(subset='recnr')
kurs_sort = kurst.sort_values(by=['recnr'])
kursdict= dict(zip(kurs_sort['recnr'], kurs_sort['kurstitel']))

k = mergedf[['recnr','kategorie']].drop_duplicates(subset='recnr')
k_sort = k.sort_values(by=['recnr'])
kdict= dict(zip(k_sort['recnr'], k_sort['kategorie']))

modult = mergedf[['recnr','modultitel']].drop_duplicates(subset='recnr')
modul_sort = modult.sort_values(by=['recnr'])
moduldict= dict(zip(modul_sort['recnr'], modul_sort['modultitel']))

# bipartiten Graph erstellen
B = nx.Graph()
# Add nodes with the node attribute "bipartite"
top_nodes = set(mergedf['recnr'])
bottom_nodes = set(mergedf['Label'])

# Syllabiknoten samt Attributen zum Graph hinzufügen
B.add_nodes_from(top_nodes, bipartite=0)
nx.set_node_attributes(B, unidict, 'Uni')
nx.set_node_attributes(B, kursdict, 'Kurstitel')
nx.set_node_attributes(B, kdict, 'Kategorie')
nx.set_node_attributes(B, moduldict, 'Modultitel')
# Referenzknoten samt Attributen zum Graph hinzufügen
B.add_nodes_from(bottom_nodes, bipartite=1)
nx.set_node_attributes(B, Reftypdict, 'Reftyp')
nx.set_node_attributes(B, Monodict, 'Monographietyp')

# Add edges only between nodes of opposite node sets
edgetuple= list(zip(mergedf.recnr, mergedf.Label))
B.add_edges_from(edgetuple)

# für den späteren Gebrauch abspeichern:
with open('B', 'wb') as B_file:
    pickle.dump(B, B_file)
