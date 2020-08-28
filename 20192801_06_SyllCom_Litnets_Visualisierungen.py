# -*- coding: utf-8 -*-
"""
Created on Fri Jan 18 09:57:08 2019

@author: KressinL

Visualisierungen für die Syllabi- und Literaturnetzwerke
"""
import pickle
import os
import pandas as pd
import networkx as nx
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec

# Laden des ganzen Syllabi mit der Communityzugehörigkeit als Attribut.
with open('Plaenegraph', 'rb') as Gplaene_file:
    Gplaene = pickle.load(Gplaene_file)

# =============================================================================
#      Visualisierung des Syllabinetzwerkes mit Communityzugehörigkeit
# =============================================================================
# giant = max(nx.connected_component_subgraphs(Gplaene), key=len)
edge_width = [100*(d['weight']) for (u, v, d) in Gplaene.edges(data=True)]
eins = [x for x,y in Gplaene.nodes(data=True) if y['modularity']==0]
zwei = [x for x,y in Gplaene.nodes(data=True) if y['modularity']==1]
drei = [x for x,y in Gplaene.nodes(data=True) if y['modularity']==2]
vier = [x for x,y in Gplaene.nodes(data=True) if y['modularity']==3]
fuenf = [x for x,y in Gplaene.nodes(data=True) if y['modularity']==4]

pos = nx.spring_layout(Gplaene, k=0.05,iterations=20)
plt.figure(figsize=(10,10))
nx.draw_networkx_nodes(Gplaene, pos=pos, nodelist= eins, node_size = 50, node_color = 'orange', label ='Community 1')
nx.draw_networkx_nodes(Gplaene, pos=pos, nodelist= zwei, node_size = 50, node_color = 'm', label = 'Community 2')
nx.draw_networkx_nodes(Gplaene, pos=pos, nodelist= drei, node_size = 50, node_color = 'b', label = 'Community 3')
nx.draw_networkx_nodes(Gplaene, pos=pos, nodelist= vier, node_size = 50, node_color = 'y', label = 'Community 4')
nx.draw_networkx_nodes(Gplaene, pos=pos, nodelist= fuenf, node_size = 50, node_color = 'g', label = 'Community 5')
nx.draw_networkx_edges(Gplaene, pos=pos, width=edge_width)
plt.legend(numpoints = 1, loc='lower right', frameon=0)
plt.axis('off')
plt.savefig('20192801_plaenegraph_communities.pdf')
plt.show()

# =============================================================================
#        Tabellarische Darstellung der jeweiligen Communityattribute
# =============================================================================
# Umwandlung der Nodesattribute in ein Dataframe, auch für Inspektion
tab = pd.DataFrame.from_dict(dict(Gplaene.nodes(data=True)), orient='index')
tab_com = tab.drop(columns = ['bipartite', 'Uni', 'Kategorie', 'Kurstitel', 'Modultitel']).reset_index().rename(columns = 
              {'index': 'Syllabus ID'}).sort_values(by=['modularity'], ascending=True).rename(columns={'modularity':'Community'})
# Knotenzahl
syll_attr = tab_com.groupby('Community')['Syllabus ID'].count().reset_index(level=0).rename(columns= {'Syllabus ID':'n Knoten (Syllabi)'})
syll_attr['Community'] = [1, 2, 3, 4, 5] # Da Python sonst bei 0 zu zählen beginnt.
# Kanten
kanten0 = len(list(Gplaene.subgraph(eins).edges))
kanten1 = len(list(Gplaene.subgraph(zwei).edges))
kanten2 = len(list(Gplaene.subgraph(drei).edges))
kanten3 = len(list(Gplaene.subgraph(vier).edges)) # die letzten beiden haben natürlich keine Kanten
kanten4 = len(list(Gplaene.subgraph(fuenf).edges))
kanten = [kanten0, kanten1, kanten2, kanten3, kanten4]
kanten_prop = [round(x / sum(kanten)*100, 1) for x in kanten]

# Dichte
density0 = round(nx.density(Gplaene.subgraph(eins)), 2)
density1 = round(nx.density(Gplaene.subgraph(zwei)), 2)
density2 = round(nx.density(Gplaene.subgraph(drei)), 2)
density3 = round(nx.density(Gplaene.subgraph(vier)), 2)
density4 = round(nx.density(Gplaene.subgraph(fuenf)), 2)
density = [density0, density1, density2, density3, density4]

# durchschnittliche Zentralitätswerte der Knoten pro Community
grad = tab_com.groupby('Community')['degree'].mean().reset_index(level=0)
close = tab_com.groupby('Community')['closeness centrality'].mean().reset_index(level=0)

syll_attr['n Kanten'] = kanten
syll_attr['Dichte'] = density
syll_attr['Grad'] = round(grad['degree'], 2)
syll_attr['Closeness'] = round(close['closeness centrality'], 2)

syll_attr.to_csv("20192801_Plaene_Cummunities_Attr.csv", header=True, encoding='utf-8-sig', index=False)
# Für den Artikel wurde diese Tabelle in http://www.tablesgenerator.com/latex_tables
# eingelesen und für die Darstellung im Latex Dokument aufbereitet.

# =============================================================================
#            Piechart für die Veranstaltungskategorien pro Community
# =============================================================================
# Noch Anteil der Communitymitglieder am Gesamtnetzwerk
knoten_prop = [round(x / sum(syll_attr['n Knoten (Syllabi)'])*100, 1) for x in syll_attr['n Knoten (Syllabi)']]

# Einlesen der proportionalen Zusammensetzung der Communities nach Veranstaltungskategorien.
with open('Kategorie_pro_Com', 'rb') as kat_file:
    kat = pickle.load(kat_file)

# Aufbereitung der Tabelle kat für graphische Darstellung. Kategorienwert und
# Anteilswert werden in einzelne Variablen eingelesen.
# Com1
labels1 = list(kat[0].index)
fracs1 = list(kat[0])
# 2
labels2 = list(kat[1].index)
fracs2 = list(kat[1])
# 3
labels3 = list(kat[2].index)
fracs3 = list(kat[2])

labels4 = list(kat[3].index)
fracs4 = list(kat[3])

labels5 = list(kat[4].index)
fracs5 = list(kat[4])

####
plt.figure(1, figsize=(10,10))
the_grid = GridSpec(4, 4)

plt.subplot(the_grid[:2, :2], aspect=1, title='Community 1 (15,9 %*)')
plt.pie(fracs1, labels=labels1, autopct='%1.1f%%', shadow=True)

plt.subplot(the_grid[:2, 2:], aspect=1, title='Community 2 (49,4 %)')
plt.pie(fracs2,labels=labels2, autopct='%.0f%%', shadow=True)

plt.subplot(the_grid[2:4, 1:3], aspect=1, title='Community 3 (33,5 %)')
plt.pie(fracs3,labels=labels3, autopct='%.0f%%', shadow=True)
plt.savefig('20192801_KatproCom_Pie.pdf', bbox_inches='tight')
plt.show()

# =============================================================================
#                  Visualisierungen zur den Literaturnetzwerken
# =============================================================================
# Laden der Communitymitglieder und Literaturnetzwerke der Communities
with open('Com0_members', 'rb') as com0_file:
    com0 = pickle.load(com0_file)
with open('LitGraph_com0', 'rb') as Glit0_file:
    Glit0 = pickle.load(Glit0_file)

with open('Com1_members', 'rb') as com1_file:
    com1 = pickle.load(com1_file)
with open('LitGraph_com1', 'rb') as Glit1_file:
    Glit1 = pickle.load(Glit1_file)
    
with open('Com2_members', 'rb') as com2_file:
    com2 = pickle.load(com2_file)
with open('LitGraph_com2', 'rb') as Glit2_file:
    Glit2 = pickle.load(Glit2_file)

# Vergleichstabelle der Eigenschaften der Literaturnetzwerke pro Community
    
# Laden der Attribute der Referenzen der ersten Community
with open('Refattribute_com0', 'rb') as ref_attr0_file:
    ref_attr0 = pickle.load(ref_attr0_file)
# Durchschnittsmasse der Literatur dieses ersten Subgraphen der ersten Community
grad_schnitt0 = (ref_attr0['degree'].sum() / len(ref_attr0)).astype(int)
# close_schnitt0 = round(ref_attr0['Closeness'].sum() / len(ref_attr0), 2)

# zweite Community
with open('Refattribute_com1', 'rb') as ref_attr1_file:
    ref_attr1 = pickle.load(ref_attr1_file)
# Durchschnittsmasse der Literatur dieses ersten Subgraphen der zweiten Community
grad_schnitt1 = (ref_attr1['degree'].sum() / len(ref_attr1)).astype(int)
# close_schnitt1 = round(ref_attr1['Closeness'].sum() / len(ref_attr1), 2)

# dritte Community
with open('Refattribute_com2', 'rb') as ref_attr2_file:
    ref_attr2 = pickle.load(ref_attr2_file)
# Durchschnittsmasse der Literatur dieses ersten Subgraphen der ersten Community
grad_schnitt2 = (ref_attr2['degree'].sum() / len(ref_attr2)).astype(int)
# close_schnitt2 = round(ref_attr2['Closeness'].sum() / len(ref_attr2), 2)

com = [1, 2, 3]
syllabi = [len(com0), len(com1), len(com2)]
syllabi_prop = [round(len(com0)/sum(syllabi)*100), round(len(com1)/sum(syllabi)*100), round(len(com2)/sum(syllabi)*100)]
knoten = [len(list(Glit0.nodes)), len(list(Glit1.nodes)), len(list(Glit2.nodes))]
knoten_prop = [round(knoten[0]/sum(knoten)*100), round(knoten[1]/sum(knoten)*100), round(knoten[2]/sum(knoten)*100)]
kanten = [len(list(Glit0.edges)), len(list(Glit1.edges)), len(list(Glit2.edges))]
density = [density0, density1, density2]
grad = [grad_schnitt0, grad_schnitt1, grad_schnitt2]
#closeness = [close_schnitt0, close_schnitt1, close_schnitt2]

################## Länge der Referenzlisten
attr_df = pd.read_csv("20192801_Ref_pro_Lehrplan.csv", index_col = False)

# Filtern der Syllbi der verschiedenen Communities
attr_df['com0'] = attr_df['recnr'].isin(com0).astype(int)
attr_df['com1'] = attr_df['recnr'].isin(com1).astype(int)
attr_df['com2'] = attr_df['recnr'].isin(com2).astype(int)     

com0_attr = attr_df[attr_df['com0'] == 1]
com1_attr = attr_df[attr_df['com1'] == 1]
com2_attr = attr_df[attr_df['com2'] == 1]
# Com1
biblen0_mean = round(com0_attr.groupby('recnr')['Label'].count().mean(), 2) # Durchschnitt
biblen0_std = round(com0_attr.groupby('recnr')['Label'].count().std(), 2) # empirische Standardabweichung
cov0 = round(biblen0_std/biblen0_mean, 2) # normalisierte Standardabweichung
# Com2
biblen1_mean = round(com1_attr.groupby('recnr')['Label'].count().mean(), 2) # Durchschnitt
biblen1_std = round(com1_attr.groupby('recnr')['Label'].count().std(), 2) # empirische Standardabweichung
cov1 = round(biblen1_std/biblen1_mean, 2) # normalisierte Standardabweichung
# Com3
biblen2_mean = round(com2_attr.groupby('recnr')['Label'].count().mean(), 2) # Durchschnitt
biblen2_std = round(com2_attr.groupby('recnr')['Label'].count().std(), 2) # empirische Standardabweichung
cov2 = round(biblen2_std/biblen2_mean, 2) # normalisierte Standardabweichung

biblen = [biblen0_mean, biblen1_mean, biblen2_mean]
cov = [cov0, cov1, cov2]

tab_attr_lit = pd.DataFrame(
    {'Community': com,
     'Syllabi gesamt (\%)': syllabi_prop,
     'n Knoten': knoten,
     'Knoten gesamt (\%)':knoten_prop,
     'n Kanten': kanten,
     'Dichte': density,
     'Grad' : grad,
     'Biblänge' : biblen,
     'norm. SD' : cov
#     'Closeness' : closeness
    })

tab_attr_lit.to_csv("20192801_Litnetz_Com_Attr.csv", header=True, encoding='utf-8-sig', index=False)

######################## Reftypen als Piecharts
# com0
with open('Refattribute_com0', 'rb') as ref_attr0_file:
    ref_attr0 = pickle.load(ref_attr0_file)
    
ref_attr0.replace(to_replace=['Graue Literatur / Bericht / Report', 'Hochschulschrift',
                              'Ton- oder Filmdokument', 'Radio- oder Fernsehsendung', 'Vortrag',
                              'Internetdokument', 'Unklarer Dokumententyp', 'Manuskript']
    , value='Sonstiges', inplace = True)
reftyp0 = ref_attr0['Reftyp'].value_counts()
reftyp0_prop = (round(ref_attr0['Reftyp'].value_counts(normalize = True), 2)*100).astype(int).reset_index().rename(columns={'index': 'Genre', 'Reftyp':'Anteil'})

mono0 = (round(ref_attr0['Unterkat_Mono'].value_counts(normalize = True), 2)*100).astype(int).reset_index().rename(columns={'index': 'Mono_sub', 'Reftyp':'Anteil'})

# com1
with open('Refattribute_com1', 'rb') as ref_attr1_file:
    ref_attr1 = pickle.load(ref_attr1_file)
    
ref_attr1.replace(to_replace=['Internetdokument', 'Unklarer Dokumententyp', 'Manuskript']
    , value='Sonstiges', inplace = True)
reftyp1 = ref_attr1['Reftyp'].value_counts()
reftyp1_prop = (round(ref_attr1['Reftyp'].value_counts(normalize = True), 2)*100).astype(int).reset_index().rename(columns={'index': 'Genre', 'Reftyp':'Anteil'})

mono1 = (round(ref_attr1['Unterkat_Mono'].value_counts(normalize = True), 2)*100).astype(int).reset_index().rename(columns={'index': 'Mono_sub', 'Reftyp':'Anteil'})

# com2
with open('Refattribute_com2', 'rb') as ref_attr2_file:
    ref_attr2 = pickle.load(ref_attr2_file)
    
ref_attr2.replace(to_replace=['Hochschulschrift','Internetdokument', 'Unklarer Dokumententyp', 'Ton- oder Filmdokument', 'Manuskript']
    , value='Sonstiges', inplace = True)
reftyp2 = ref_attr2['Reftyp'].value_counts()
reftyp2_prop = (round(ref_attr2['Reftyp'].value_counts(normalize = True), 2)*100).astype(int).reset_index().rename(columns={'index': 'Genre', 'Reftyp':'Anteil'})

mono2 = (round(ref_attr1['Unterkat_Mono'].value_counts(normalize = True), 2)*100).astype(int).reset_index().rename(columns={'index': 'Mono_sub', 'Reftyp':'Anteil'})

# Pie Charts der Reftypen
# 1
fig = plt.figure(1)
ax1 = fig.add_axes([.1, .1, .8, .8], aspect=1, title='Community 1')
ax1.pie(list(reftyp0_prop['Anteil']), labels=list(reftyp0_prop['Genre']), explode=(0.1, 0, 0, 0, 0), autopct='%1.1f%%', shadow=True)
ax2 = fig.add_axes([.8, .6, .3, .3], aspect=1)  # You can adjust the position and size of the axes for the pie plot
ax2.pie(list(mono0['Unterkat_Mono']),labels=list(mono0['Mono_sub']), autopct='%.0f%%', shadow=True, textprops={'fontsize': 7})
plt.savefig('20192801_Genre_Pie0.pdf', bbox_inches='tight')
#2
fig = plt.figure(2)
ax1 = fig.add_axes([.1, .1, .8, .8], aspect=1, title='Community 2')
ax1.pie(list(reftyp1_prop['Anteil']),labels=list(reftyp1_prop['Genre']), explode=(0.1, 0, 0, 0, 0, 0), autopct='%.0f%%', shadow=True)
ax2 = fig.add_axes([.7, .6, .3, .3], aspect=1)  # You can adjust the position and size of the axes for the pie plot
ax2.pie(list(mono1['Unterkat_Mono']),labels=list(mono1['Mono_sub']), autopct='%.0f%%', shadow=True, textprops={'fontsize': 7}, labeldistance=1.5)
plt.savefig('20192801_Genre_Pie1.pdf', bbox_inches='tight')
#3
fig = plt.figure(3)
ax1 = fig.add_axes([.1, .1, .8, .8], aspect=1, title='Community 3')
ax1.pie(list(reftyp2_prop['Anteil']),labels=list(reftyp2_prop['Genre']), explode=(0.1, 0, 0, 0, 0, 0), autopct='%.0f%%', shadow=True)
ax2 = fig.add_axes([.85, .50, .3, .3], aspect=1)  # You can adjust the position and size of the axes for the pie plot
ax2.pie(list(mono2['Unterkat_Mono']),labels=list(mono2['Mono_sub']), autopct='%.0f%%', shadow=True, textprops={'fontsize': 7}, labeldistance=1.5)
plt.savefig('20192801_Genre_Pie2.pdf', bbox_inches='tight')
plt.show()

##### Häufigste Referenzen samt Art
# Com1
com0_attr_reduz = com0_attr.drop(['uni', 'modultitel', 'kurstitel', 'software', 'kategorie', 'com0', 'com1', 'com2'], axis=1)
zitcount_lit0 = com0_attr_reduz['Label'].value_counts().reset_index().rename(columns={'index': 'Quelle', 'Label': 'Zitationszahl'})
zitcount_lit0['Zitationsanteil in \%'] = round((zitcount_lit0['Zitationszahl']/sum(zitcount_lit0['Zitationszahl'])*100), 2)
zitcount_lit0['kum. Anteil'] = zitcount_lit0['Zitationsanteil in \%'].cumsum()
# Verbinden mit Zentralitätsmassen
lit0_counts = pd.read_csv("20192801_Lit0_measures.csv", index_col = False)
zit0 = zitcount_lit0.merge(lit0_counts)
zit0.to_csv("20192801_lit0.csv", header=True, encoding='utf-8-sig', index=False)
top5_0 = zit0.iloc[0:5]
top5_0.to_csv("20192801_Toplit0.csv", header=True, encoding='utf-8-sig', index=False)

# Com2
com1_attr_reduz = com1_attr.drop(['uni', 'modultitel', 'kurstitel', 'software', 'kategorie', 'com0', 'com1', 'com2'], axis=1)
zitcount_lit1 = com1_attr_reduz['Label'].value_counts().reset_index().rename(columns={'index': 'Quelle', 'Label': 'Zitationszahl'})
zitcount_lit1['Zitationsanteil in \%'] = round((zitcount_lit1['Zitationszahl']/sum(zitcount_lit1['Zitationszahl'])*100), 2)
zitcount_lit1['kum. Anteil'] = zitcount_lit1['Zitationsanteil in \%'].cumsum()
# Verbinden mit Zentralitätsmassen
lit1_counts = pd.read_csv("20192801_Lit1_measures.csv", index_col = False)
zit1 = zitcount_lit1.merge(lit1_counts)
zit1.to_csv("20192801_lit1.csv", header=True, encoding='utf-8-sig', index=False)
top5_1 = zit1.iloc[0:5]
top5_1.to_csv("20192801_Toplit1.csv", header=True, encoding='utf-8-sig', index=False)

# Com3
com2_attr_reduz = com2_attr.drop(['uni', 'modultitel', 'kurstitel', 'software', 'kategorie', 'com0', 'com1', 'com2'], axis=1)
zitcount_lit2 = com2_attr_reduz['Label'].value_counts().reset_index().rename(columns={'index': 'Quelle', 'Label': 'Zitationszahl'})
zitcount_lit2['Zitationsanteil in \%'] = round((zitcount_lit2['Zitationszahl']/sum(zitcount_lit2['Zitationszahl'])*100), 2)
zitcount_lit2['kum. Anteil'] = zitcount_lit2['Zitationsanteil in \%'].cumsum()
# Verbinden mit Zentralitätsmassen
lit2_counts = pd.read_csv("20192801_Lit2_measures.csv", index_col = False)
zit2 = zitcount_lit2.merge(lit2_counts)
zit2.to_csv("20192801_lit2.csv", header=True, encoding='utf-8-sig', index=False)
top5_2 = zit2.iloc[0:5]
top5_2.to_csv("20192801_Toplit2.csv", header=True, encoding='utf-8-sig', index=False)
