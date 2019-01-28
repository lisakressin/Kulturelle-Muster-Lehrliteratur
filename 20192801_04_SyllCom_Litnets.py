# -*- coding: utf-8 -*-
"""
Created on Thu Jan 17 07:48:34 2019

@author: KressinL

In diesem Skript werden basierend auf dem bipartiten Netzwerk B Syllabi- und Literatur
netzwerke erstellt. Erstere werden auf ihre enthaltenen Communities untersucht, die
anschliessend den Rahmen für die Auswertung ihrer Literatur(netzwerke) bilden.
Dies ist im Kern die Auswertung des Artikels "Aus 4 mach 3", welcher für den Projektretreat
im Februar 2019 erstell worden ist.
"""
import os
import pandas as pd
import networkx as nx
import networkx.algorithms.bipartite as bi
from networkx.algorithms import community
import community
from operator import itemgetter
import pickle

os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")

# Laden des bipartiten Graphen
with open('B', 'rb') as B_file:
    B = pickle.load(B_file)

# =============================================================================
#                            Syllabinetzwerke
# =============================================================================

#########################Aufbereitung des Syllabigraphen #####################
# Filtern der Syllabiknoten 
plaene = [x for x,y in B.nodes(data=True) if y['bipartite']==0]

# projected Graph der Lehrpläne erstellen, gemäss der Geflogenheiten der Bibliometrie
# gewichte ich die Kanten mit Saltons Kosinus
Gplaene = bi.weighted_projected_graph(B, plaene,ratio=True)

# Hinzufügen von Attributen, die die Identifikation der Pläne ermöglichen.
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables")
attr_df = pd.read_csv("20192801_Ref_pro_Lehrplan.csv", index_col = False)

######################## Netzwerk- und Knotenmasse ###########################
# Dichte
density = nx.density(Gplaene)
print("Network density:", round(density, 3))
# 32 % aller möglichen Beziehungen zwischen den Syllabi existieren tatsächlich.

# Anzahl an verbundenen Komponenten = 3, entsprechend liegt ein 'disconnected graph' vor
nx.algorithms.components.number_connected_components(Gplaene)

# Subgraphen erstellen
#comp = list(nx.connected_component_subgraphs(Gplaene))[0]
#len(list(comp.nodes)) # 168 - entsprechend habe ich eine grosse Component und 
# zwei einzelne unverbundene Knoten
# Dichte
#density = nx.density(comp)
#print("Network density:", round(density, 3))
# 33 %

# Zentralitätsmasse
# degree
degree_dict = dict(Gplaene.degree(Gplaene))
nx.set_node_attributes(Gplaene, degree_dict, 'degree')
# Sortierte Knoten mit den 20 Höchsten degree-Werten
sorted_degree = sorted(degree_dict.items(), key=itemgetter(1), reverse=True)

print("Top 20 nodes by degree:")
for d in sorted_degree[:20]:
    print(d)
    print (Gplaene.nodes[d[0]]['Uni'])
    print (Gplaene.nodes[d[0]]['Kategorie'])
    
# Closeness vlt auch als 'kognitiv' close definieren
closeness = nx.closeness_centrality(Gplaene)
nx.set_node_attributes(Gplaene, closeness, 'closeness centrality')
sorted_between = sorted(closeness.items(), key=itemgetter(1), reverse=True)

print("Top 20 nodes by closeness centrality:")
for d in sorted_between[:10]:
    print(d)
    print (Gplaene.nodes[d[0]]['Uni'])
    print (Gplaene.nodes[d[0]]['Kategorie'])

########################### Communitydetection ################################
""" Modularität: "Networks with high modularity have dense connections between the
# nodes within modules but sparse connections between nodes in different modules." (Wiki)
# Zur Funktion: 
"Compute the partition of the graph nodes which maximises the modularity (or try..) using the Louvain heuristices
This is the partition of highest modularity, i.e. the highest partition of the 
dendrogram generated by the Louvain algorithm." https://perso.crans.org/aynaud/communities/api.html
"""
communities = community.best_partition(Gplaene)
# Anzahl der "communities"
set(communities.values()) # 5 Communities
nx.set_node_attributes(Gplaene, communities, 'modularity')

# Graph für die Visualisierung speichern
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Plaenegraph', 'wb') as Gplaene_file:
    pickle.dump(Gplaene, Gplaene_file)

# Für schnelle Gephiinspektion
#os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Gephi")
#nx.write_graphml(Gplaene, "Syllabigraph.graphml")

# Umwandlung der Nodesattribute in ein Dataframe, auch für Inspektion
tab = pd.DataFrame.from_dict(dict(Gplaene.nodes(data=True)), orient='index')
# Löschen der "bipartite"-Spalte, Rücksetzen des Index, Umbenennung von Spalten Sortierung der Zeilen nach Communityzugehörigkeit.
tab = tab.drop(['bipartite'], axis =1).reset_index().rename(columns = 
              {'index': 'Syllabus ID'}).sort_values(by=['modularity'], ascending=True).rename(columns={'modularity':'Community'})

# os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables")
# tab.to_csv("Syllabicommunities_Attr.csv", header=True, encoding='utf-8-sig', index=False)

# Statistiken pro Communities
tab.groupby('Community')['Uni'].value_counts()
tab.groupby('Community')['Kurstitel'].value_counts()
tab.groupby('Community')['degree'].mean()
tab.groupby('Community')['closeness centrality'].mean()

# Noch sind die Werte der Variable "Kategorie" sehr ausdifferenziert, das brauche ich in der Form für die folgenden Auswertungen nicht.
# Ich hebe die Unterscheidung der Kategorien zu ihrem Kontrapart mit Computereinsatz ("&CS") auf, zudem wird die Mathekategorie "MATH" mit Statistik zusammengelegt.
tab_noCS = tab.copy()
tab_noCS['Kategorie'] = tab_noCS['Kategorie'].str.replace("(&CS)", "", regex=False).str.replace("S ", "S", regex=False).str.replace("MATH", "S", regex=False)

# Proportionaler Anteil in % der Kategorien pro Community.
kat = round(tab_noCS.groupby('Community')['Kategorie'].value_counts(normalize=True), 2)
kat.name = 'prop. Anteil'
kat = (kat*100).astype(int)
# Speichern der Tabelle
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables")
kat.to_csv('20192801_Kategorie_pro_Com.csv', header= True)

# Für die Visualisierung als Objekt speichern
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Kategorie_pro_Com', 'wb') as kat_file:
    pickle.dump(kat, kat_file)

# Rückbindung der Clusterpläne an ihre Literatur, um diese auszuwerten
# Erstellung von 3 bipartiten Subgraphen identisch mit den drei Communities.
# aus communitiesdicts 3 dics pro community mit ID
com0 = [k for k,v in communities.items() if v == 0]
with open('Com0_members', 'wb') as com0_file:
    pickle.dump(com0, com0_file)
com1 = [k for k,v in communities.items() if v == 1]
with open('Com1_members', 'wb') as com1_file:
    pickle.dump(com1, com1_file)
com2 = [k for k,v in communities.items() if v == 2]
with open('Com2_members', 'wb') as com2_file:
    pickle.dump(com2, com2_file)
    
# Das letzte 'Cluster' hat keine Nummer zugeordnet,
# weil die Knoten unverbunden sind.

# Bipartite Subgraphen basierend auf den Clusternotes erstellen, um anschliessend die Literatur
# der Cluster zu analysieren.
# "The view will only report edges incident to these nodes."

######################## 1. Subgraph #####################################
edges0 = list(B.edges(com0))
top_nodes0 = set([k for k,v in edges0])
bottom_nodes0 = set([v for k,v in edges0])
# zum Graph zusammensetzen
subG0 = nx.Graph()
subG0.add_edges_from(edges0)
# Bipartite nodes definieren
bi_dict0 = {}
for i in top_nodes0:
        bi_dict0[i] = 0
for i in bottom_nodes0:
        bi_dict0[i] = 1       
        
nx.set_node_attributes(subG0, bi_dict0, 'bipartite')

os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Sub_Com1', 'wb') as Sub_Com1_file:
    pickle.dump(subG0, Sub_Com1_file)

######################## 2, Subgraph #####################################
edges1 = list(B.edges(com1))
top_nodes1 = set([k for k,v in edges1])
bottom_nodes1 = set([v for k,v in edges1])
# zum Graph zusammensetzen
subG1 = nx.Graph()
subG1.add_edges_from(edges1)
# Bipartite nodes definieren
bi_dict1 = {}
for i in top_nodes1:
        bi_dict1[i] = 0
for i in bottom_nodes1:
        bi_dict1[i] = 1       
        
nx.set_node_attributes(subG1, bi_dict1, 'bipartite')

os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Sub_Com2', 'wb') as Sub_Com2_file:
    pickle.dump(subG1, Sub_Com2_file)
######################## 3. Subgraph #####################################
edges2 = list(B.edges(com2))
top_nodes2 = set([k for k,v in edges2])
bottom_nodes2 = set([v for k,v in edges2])
# zum Graph zusammensetzen
subG2 = nx.Graph()
subG2.add_edges_from(edges2)
# Bipartite nodes definieren
bi_dict2 = {}
for i in top_nodes2:
        bi_dict2[i] = 0
for i in bottom_nodes2:
        bi_dict2[i] = 1       
        
nx.set_node_attributes(subG2, bi_dict2, 'bipartite')

os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Sub_Com3', 'wb') as Sub_Com3_file:
    pickle.dump(subG2, Sub_Com3_file)

# =============================================================================
#                           Literaturnetzwerke
# =============================================================================

############ Literaturnetzwerk des 1 Subgraphen (Community) ###################
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Sub_Com1', 'rb') as Sub_Com1_file:
    subG0 = pickle.load(Sub_Com1_file)

# Literaturknoten des bipartiten Graphen auswählen
lit0 = [x for x,y in subG0.nodes(data=True) if y['bipartite']==1]
# Projektion des bipartiten Subgraphen zu einem Literaturnetzwerk, die Beziehungen
# zwischen den Knoten sind gewichtet durch die absolute Zahl der Ko-Zitationen der
# Knoten in Syllabi.
Glit0 = bi.weighted_projected_graph(subG0, lit0, ratio=False)

density0 = round(nx.density(Glit0), 2)
print("Network density:", density0)

# degree
degree_dict0 = dict(Glit0.degree(Glit0.nodes))
nx.set_node_attributes(Glit0, degree_dict0, 'degree')

# Speichern des Literaturnetzwerkes des 1. Subgraphen
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects") 
with open('LitGraph_com0', 'wb') as Glit0_file:
    pickle.dump(Glit0, Glit0_file)

# Sortierte Knoten mit den 20 Höchsten degree-Werten
sorted_degree0 = sorted(degree_dict0.items(), key=itemgetter(1), reverse=True)
print("Top 5 nodes by degree:")
for d in sorted_degree0[:10]:
    print(d)

# Auswertung der Zentralitätsmasse der Knoten
top0 = list(sorted_degree0[:10])
referenzen0 = []
grad0 = []
for i, j in top0:
    referenzen0.append(i)
    grad0.append(j)
 
# Top5 der Knoten mit höchster Gradzahl
top5_0 = pd.DataFrame(
    {'Referenzen': referenzen0,
     'Gradzahl': grad0,
    })

os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables") 
top5_0.to_csv("20192801_Top5_Com0.csv", header=True, encoding='utf-8-sig', index=False)

# closeness
closeness_dict0 = nx.closeness_centrality(Glit0)
nx.set_node_attributes(Glit0, closeness_dict0, 'Closeness')
# Sortierte Knoten mit den 20 Höchsten degree-Werten
sorted_between0 = sorted(closeness_dict0.items(), key=itemgetter(1), reverse=True)
print("Top 5 nodes by Closeness Centrality:")
for d in sorted_degree0[:5]:
    print(d)

# Graph für Gephiinspektion speichern
#os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Gephi")
#nx.write_graphml(Glit0, "20192801_Lit_SubG0.graphml")

# Tabelle der Referenzen der ersten Community (Subgraphen) mit Zentralitätsmassen, sortiert nach Grad.
lit0_counts = pd.DataFrame.from_dict(dict(Glit0.nodes(data=True)), orient='index')
lit0_counts = lit0_counts.drop(['bipartite'], axis =1).reset_index().sort_values(by=['degree'], ascending=False).rename(columns={'degree':'Grad', 'index': 'Quelle'})
lit0_counts['Closeness'] = round(lit0_counts['Closeness'], 2)

# Speichern
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables")
lit0_counts.to_csv("20192801_Lit0_measures.csv", header=True, encoding='utf-8-sig', index=False)

###### Statistiken zur Literatur der ersten Community
# Hinzufügen von Literatur-Attributen
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables")
attr_df = pd.read_csv("20192801_Ref_pro_Lehrplan.csv", index_col = False)
# Entfernen aller Variablen, die die Lehrpläne statt die Referenzen charakterisieren.
attr_df = attr_df.drop(['recnr', 'uni', 'modultitel', 'kurstitel', 'software', 'kategorie'], axis=1)
attr_df_uni = attr_df.drop_duplicates('Label')

# Umwandlung des Subgraphen samt Attributen (Zentralitätsmasse) in Tabelle und zusammenfügen
# mit Attributen aus attr_df_uni
ref_attr0 = pd.DataFrame.from_dict(dict(Glit0.nodes(data=True)), orient='index').drop('bipartite', axis=1).reset_index().rename(columns= {'index': 'Label'})
ref_attr0 = ref_attr0.merge(attr_df_uni)

# Speichern als Objekt
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Refattribute_com0', 'wb') as ref_attr0_file:
    pickle.dump(ref_attr0, ref_attr0_file)

# Durchschnittsmasse der Literatur dieses ersten Subgraphen der ersten Community
grad_schnitt0 = (ref_attr0['degree'].sum() / len(ref_attr0)).astype(int)
close_schnitt0 = round(ref_attr0['Closeness'].sum() / len(ref_attr0), 2)
# Verteilung der Referenztypen im Subgraphen
reftyp0 = ref_attr0['Reftyp'].value_counts()
reftyp0_prop = (round(ref_attr0['Reftyp'].value_counts(normalize = True), 2)*100).astype(int)

############## Literaturnetzwerk des 2. Subgraphen (Community) ###############
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Sub_Com2', 'rb') as Sub_Com2_file:
    subG1 = pickle.load(Sub_Com2_file)

lit1 = [x for x,y in subG1.nodes(data=True) if y['bipartite']==1]
Glit1 = bi.weighted_projected_graph(subG1, lit1, ratio=False)

density1 = round(nx.density(Glit1), 2)
print("Network density:", density1)

# degree
degree_dict1 = dict(Glit1.degree(Glit1.nodes))
nx.set_node_attributes(Glit1, degree_dict1, 'degree')

# Speichern des Literaturnetzwerkes des 2. Subgraphen
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects") 
with open('LitGraph_com1', 'wb') as Glit1_file:
    pickle.dump(Glit1, Glit1_file)

# Sortierte Knoten mit den 20 Höchsten degree-Werten
sorted_degree1 = sorted(degree_dict1.items(), key=itemgetter(1), reverse=True)
print("Top 5 nodes by degree:")
for d in sorted_degree1[:5]:
    print(d)
    
# Visualisierung
top1 = list(sorted_degree1[:5])
referenzen1 = []
grad1 = []
for i, j in top1:
    referenzen1.append(i)
    grad1.append(j)
    
top5_1 = pd.DataFrame(
    {'Referenzen': referenzen1,
     'Gradzahl': grad1,
    })

os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables")
top5_1.to_csv("20192801_Top5_1.csv", header=True, encoding='utf-8-sig', index=False)

# closeness
closeness_dict1 = nx.closeness_centrality(Glit1)
nx.set_node_attributes(Glit1, closeness_dict1, 'Closeness')
# Sortierte Knoten mit den 20 Höchsten degree-Werten
sorted_between1 = sorted(closeness_dict1.items(), key=itemgetter(1), reverse=True)
print("Top 20 nodes by Closeness Centrality:")
for d in sorted_degree1[:20]:
    print(d)

# Gephi
#os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Gephi")
#nx.write_graphml(Glit1, "20192801_Lit_SubG1.graphml")

# Zentralitätsmasse der Knoten des Subgraphen der Community 2
lit1_counts = pd.DataFrame.from_dict(dict(Glit1.nodes(data=True)), orient='index')
lit1_counts = lit1_counts.drop(['bipartite'], axis =1).reset_index().sort_values(by=['degree'], ascending=False).rename(columns={'degree':'Grad', 'index': 'Quelle'})
lit1_counts['Closeness'] = round(lit1_counts['Closeness'], 2)
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables")
lit1_counts.to_csv("20192801_Lit1_measures.csv", header=True, encoding='utf-8-sig', index=False)

###### Statistiken zur Literatur des Clusters
# Hinzufügen von Attributen
ref_attr1 = pd.DataFrame.from_dict(dict(Glit1.nodes(data=True)), orient='index').drop('bipartite', axis=1).reset_index().rename(columns= {'index': 'Label'})
ref_attr1 = ref_attr1.merge(attr_df_uni)

# Speichern
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Refattribute_com1', 'wb') as ref_attr1_file:
    pickle.dump(ref_attr1, ref_attr1_file)

grad_schnitt1 = (ref_attr1['degree'].sum() / len(ref_attr1)).astype(int)
close_schnitt1 = round(ref_attr1['Closeness'].sum() / len(ref_attr1), 2)
reftyp1 = ref_attr1['Reftyp'].value_counts()
reftyp1_prop = (round(ref_attr1['Reftyp'].value_counts(normalize = True), 2)*100).astype(int)

############## Literaturnetzwerk des 3. Subgraphen (Community) ###############
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Sub_Com3', 'rb') as Sub_Com3_file:
    subG2 = pickle.load(Sub_Com3_file)

lit2 = [x for x,y in subG2.nodes(data=True) if y['bipartite']==1]
Glit2 = bi.weighted_projected_graph(subG2, lit2, ratio=False)

density2 = round(nx.density(Glit2), 2)
print("Network density:", density2)

# degree
degree_dict2 = dict(Glit2.degree(Glit2.nodes))
nx.set_node_attributes(Glit2, degree_dict2, 'degree')

# Speichern des Literaturnetzwerkes des 3. Subgraphen
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects") 
with open('LitGraph_com2', 'wb') as Glit2_file:
    pickle.dump(Glit2, Glit2_file)

# Sortierte Knoten mit den 20 Höchsten degree-Werten
sorted_degree2 = sorted(degree_dict2.items(), key=itemgetter(1), reverse=True)
print("Top 5 nodes by degree:")
for d in sorted_degree2[:5]:
    print(d)
    
# Visualisierung
top2 = list(sorted_degree2[:5])
referenzen2 = []
grad2 = []
for i, j in top2:
    referenzen2.append(i)
    grad2.append(j)
    
top5_2 = pd.DataFrame(
    {'Referenzen': referenzen2,
     'Gradzahl': grad2,
    })

os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables")
top5_2.to_csv("20192801_Top5_2.csv", header=True, encoding='utf-8-sig', index=False)

# closeness
closeness_dict2 = nx.closeness_centrality(Glit2)
nx.set_node_attributes(Glit2, closeness_dict2, 'Closeness')
# Sortierte Knoten mit den 20 Höchsten degree-Werten
sorted_between2 = sorted(closeness_dict2.items(), key=itemgetter(1), reverse=True)
print("Top 20 nodes by Closeness Centrality:")
for d in sorted_degree2[:20]:
    print(d)

# Für Gephi speichern
#os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Gephi")
#nx.write_graphml(Glit2, "20192801_Lit_SubG2.graphml")

# Für Visualisierung
lit2_counts = pd.DataFrame.from_dict(dict(Glit2.nodes(data=True)), orient='index')
lit2_counts = lit2_counts.drop(['bipartite'], axis =1).reset_index().sort_values(by=['degree'], ascending=False).rename(columns={'degree':'Grad', 'index': 'Quelle'})
lit2_counts['Closeness'] = round(lit2_counts['Closeness'], 2)
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Tables")
lit2_counts.to_csv("20192801_Lit2_measures.csv", header=True, encoding='utf-8-sig', index=False)

###### Statistiken zur Literatur des Clusters
# Hinzufügen von Attributen
ref_attr2 = pd.DataFrame.from_dict(dict(Glit2.nodes(data=True)), orient='index').drop('bipartite', axis=1).reset_index().rename(columns= {'index': 'Label'})
ref_attr2 = ref_attr2.merge(attr_df_uni)

# Für die Visualisierung
os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Outputs\Objects")
with open('Refattribute_com2', 'wb') as ref_attr2_file:
    pickle.dump(ref_attr2, ref_attr2_file)

grad_schnitt2 = (ref_attr2['degree'].sum() / len(ref_attr2)).astype(int)
close_schnitt2 = round(ref_attr2['Closeness'].sum() / len(ref_attr2), 2)
reftyp2 = ref_attr2['Reftyp'].value_counts()
reftyp2_prop = (round(ref_attr2['Reftyp'].value_counts(normalize = True), 2)*100).astype(int)

###########################################################################

# Überschneidungen der Literaturnetzwerke
#print(set(lit0).intersection(lit1))
#print(set(lit0).intersection(lit2))
#print(set(lit1).intersection(lit2))

# =============================================================================
#       Vergleich mit Gesamtnetzwerk (nicht in Retreatartikel aufgenommen)
# =============================================================================
#Glit = [x for x,y in B.nodes(data=True) if y['bipartite']==1]
#Glit = bi.weighted_projected_graph(B, Glit,ratio=False)
#
#communities_lit = community.best_partition(Glit)
## Anzahl der "communities"
#set(communities_lit.values()) # 11 Communities
#nx.set_node_attributes(Glit, communities_lit, 'modularity')
#nx.write_graphml(Glit, "170118 Graph Literatur.graphml")
#density_lit = round(nx.density(Glit), 2)
#
## Nach Blick in Gephi: Ähnliche Unterteilung bezüglich der grossen Blöcke,
## nur eben mit einzelnen separaten Lehrplänen als einzelne Cluster.
#
## Nach degree Filtern, um solche Insel herauszubekommen.
#degree_dict = dict(Glit.degree(Glit.nodes))
#nx.set_node_attributes(Glit, degree_dict, 'degree')
#nx.get_node_attributes(Glit, 'degree')
#
## Zur Bestimmung des Schwellenwertes durchschnittliche Reflänge heranziehen?
#selected_nodes = [n for n,v in Glit.nodes(data=True) if v['degree'] > 20]
#len(selected_nodes)
#Gfilter = Glit.subgraph(selected_nodes)
