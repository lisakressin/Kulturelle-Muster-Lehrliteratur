# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 16:41:46 2018
@author: KressinL

In diesem Skript werden aus dem bereits mit den UniIDs gelinkte Lehrplandatensatz
"date_lehrplaene_linked.xlsx" die Bibliographien der Syllabi extrahiert und anschliessend
werden aus diesen wiederum die einzelnen Referenzen isoliert. Der wichtigste Teil besteht
im Matching dieser Referenzen mit einer händisch erstellten Literaturtabelle aus Citavi,
in der die Referenzen der Syllabi ihren "sauberen" Gegenpart finden. Der Endoutput
dieses Skiptes ist eine Tabelle mit allen Referenzen pro Syllabus, inklusive einiger
Variablen aus Citavi, die den Literaturtypus näher beschreiben (z.B. Monographie etc.).

Gefiltert werden nur jene Bachelor-Pflichtveranstaltungen aus dem Zeitraum Wintersemester 2015/16 - Sommer 2018.
"""

import pandas as pd
import numpy as np
import re
import Levenshtein
from fuzzywuzzy import fuzz, process
from nltk import metrics
from itertools import chain
import itertools
from string import punctuation
import sys
import csv
import os

# Einlesen meiner Lehrplan-Tabelle
# die bereits gelinkte Version mit Uni und Stufe
df = pd.read_excel("20190128_lehrplaene_linked.xlsx")

# Filtern der relevanten Spalten
# Hier filtere ich nach Pflichtkursen in Pflichtmodulen aus den Semestern Wi1617 und So17.
sub_pflicht = df.query("WiSe1516 == 'x' | SoSe16 == 'x' | WiSe1617 == 'x' | SoSe17 == 'x' | WiSe1718 == 'x' | SoSe18 == 'x'").query("P_W_modul == 'P' and P_W_kurs == 'P'").query("stufe == 'BA'")
# neuer Index
sub_pflicht = sub_pflicht.reset_index(drop=True)

"""Erst einmal muss ich meine relevante Literaturspalte, die in Python eine
Series darstellt, die man nicht splitten kann, in eine Liste verwanden.
Dabei filtere ich schon nur die Zeilen mit Literaturangaben."""
# Loop für das Splitten der Referenzen
referenzen_basis = []
referenzen_weitere = []

for i in sub_pflicht["basisliteratur"]:
    if pd.notnull(i) == True:
        referenzen_basis.append(i.split("\n\n"))
    else:
        referenzen_basis.append(np.NaN)
        
for i in sub_pflicht["weitere literatur"]:
    if pd.notnull(i) == True:
        referenzen_weitere.append(i.split("\n\n"))
    else:
        referenzen_weitere.append(np.NaN)

sub_pflicht["referenzen_basis"] = referenzen_basis
sub_pflicht["referenzen_weitere"] = referenzen_weitere

# Nun der Loop für die "Basisreferenzen". (Ich hatte bei der Extraktion der Bibliographien zunächst
# zwischen "Basisliteratur" und "weiterer Literatur" unterschieden, wenn sich diese Unterscheidung aus den Informationen der Syllabi ableiten liess.)
# Metadaten, wie Modultitel etc, übernehme ich im Loop.

REF = []
R_NR = []
uni = []
modultitel = []
kurstitel = []
software = []
kategorie = []

for i, doc in enumerate(sub_pflicht["referenzen_basis"]):
    if isinstance(doc, float) == True:
        continue
    else:
        for count, ref in enumerate(doc):
            REF.append(doc[count])
            nr_refs = len(doc)
        uni.append(np.repeat(sub_pflicht["uniname"][i], nr_refs))
        modultitel.append(np.repeat(sub_pflicht["modultitel"][i], nr_refs))
        kurstitel.append(np.repeat(sub_pflicht["kurstitel"][i], nr_refs))
        software.append(np.repeat(sub_pflicht["software"][i], nr_refs))
        kategorie.append(np.repeat(sub_pflicht["kategorie"][i], nr_refs))
        R_NR.append(np.repeat(sub_pflicht["referenzen_basis"].index[i], nr_refs)) # record number

R_NR = list(chain.from_iterable(R_NR))
uni = list(chain.from_iterable(uni))
modultitel = list(chain.from_iterable(modultitel))
kurstitel = list(chain.from_iterable(kurstitel))
software = list(chain.from_iterable(software))
kategorie = list(chain.from_iterable(kategorie))

# Speichern die Referenzen in einem data.frame ref:
# Spalte 1: Nummer des records rec.nr
# Spalte 2: Referenz all

ref_basis = pd.DataFrame(
        {"recnr": R_NR, "referenzen": REF, "uni": uni, "modultitel" : modultitel,
         "kurstitel" : kurstitel, "software" : software, "kategorie" : kategorie
         })

# Loop für die zusätzlichen Referenzen
    
REF = []
R_NR = []
uni = []
modultitel = []
kurstitel = []
software = []
kategorie = []

for i, doc in enumerate(sub_pflicht["referenzen_weitere"]):
    if isinstance(doc, float) == True:
        continue
    else:
        for count, ref in enumerate(doc):
            REF.append(doc[count])
            nr_refs = len(doc)
        uni.append(np.repeat(sub_pflicht["uniname"][i], nr_refs))
        modultitel.append(np.repeat(sub_pflicht["modultitel"][i], nr_refs))
        kurstitel.append(np.repeat(sub_pflicht["kurstitel"][i], nr_refs))
        software.append(np.repeat(sub_pflicht["software"][i], nr_refs))
        kategorie.append(np.repeat(sub_pflicht["kategorie"][i], nr_refs))
        R_NR.append(np.repeat(sub_pflicht["referenzen_weitere"].index[i], nr_refs))


R_NR = list(chain.from_iterable(R_NR))
uni = list(chain.from_iterable(uni))
modultitel = list(chain.from_iterable(modultitel))
kurstitel = list(chain.from_iterable(kurstitel))
software = list(chain.from_iterable(software))
kategorie = list(chain.from_iterable(kategorie))

ref_weitere = pd.DataFrame(
        {"recnr": R_NR, "referenzen": REF, "uni": uni, "modultitel" : modultitel,
         "kurstitel" : kurstitel, "software" : software, "kategorie" : kategorie
         })
    
# Mergen beider dataframes (1x "Basisliteratur", 1x "zusätzliche Literatur" via Zeile
ref = pd.concat([ref_basis, ref_weitere])

# Sichern als csv.file
ref.to_csv("20192801_Ref_pro_Syll_BA_Pflicht_15_18.csv", encoding='utf-8-sig', index= False)

# Splitten nach Herausgeber, als Trick, um das Matchen mit Sammelbandbeiträgen zu verbessern
ref["referenzen"] = ref["referenzen"].str.split("Hg|Hrsg|hrsg|Eds|eds\s|eds\.\s|eds\.\)|\sed\.\s|\sed\s").str.get(0)

## Matchen meiner Referenzliste mit der Citaviliste (https://osf.io/x6m5v/)
citavi = pd.read_excel("20192801_Citavi_Ref_clean.xlsx")
citavi.rename(columns ={'Autor, Herausgeber oder Institution': 'autorin', 'Jahr ermittelt': 'jahr', 'Übergeordneter Titeleintrag (In:)': 'In'}, inplace = True)
citavi.In.fillna("", inplace = True)
citavi.Untertitel.fillna("", inplace = True)

# Zusammenfügen der Inhalte aus autorin und titel und In (falls vorhanden) für erfolgreicheres Matchen
citavi["autorin titel In"] = citavi["autorin"] + " " + citavi["Titel"] + " " + citavi["Untertitel"] + " " + citavi["In"]
citavi["autorin titel In"] = citavi["autorin titel In"].str.lower().str.replace(u" \u2013 ", "").str.replace("[(),;.-]", "").str.replace("/", " ").str.replace("ß", "ss").str.replace("\d", "")

# Processing
ref["processed"] = ref["referenzen"].str.lower().str.replace("[(),;:.-]", "").str.replace(u"\u2013", "").str.replace("^\s+", "").str.replace("/", " ").str.replace("ß", "ss").str.replace("\d", "")
ref["processed"] = ref["processed"].str.replace("überarbeitete|überarb|auflage|\bund\b|verlag|aufl|verl|\bin\b|\bed|hrsg|hg|dies|\bmit\b|\beine\b|\bein\b|\bbei|\bder\b|\bdie\b", "")

# Fuzzy Matching
def fuzzy_match(x, choices, scorer, cutoff):
    return process.extractOne(
        x, choices=choices, scorer=scorer, score_cutoff=cutoff
    )

matching_results = ref["processed"].apply(
    fuzzy_match,
    args=(citavi["autorin titel In"], 
        fuzz.token_set_ratio,
        61
    )
)
    
ref["matching results"] = matching_results

# noch die ratios raus, um eindeutige Referenzen zu haben
ref["matching_results_rein"] = ref["matching results"].str[0]
# Löschen der nicht relevanten Spalten
ref_df = ref.drop(['referenzen', 'processed', 'matching results'], axis =1)
# Sicherheitshalber Dubletten suchen und entfernen (damit nicht aus Versehen, dieselbe Referenz mehrmals auf einem Lehrplan auftaucht.)
nodup = ref_df.drop_duplicates()
df_sub = nodup.rename(columns = {'matching_results_rein': 'Label'})
df_sub = df_sub.reset_index(drop= True)

# Speichern als csv.file
df_sub.to_csv("20192801_CitaviMatching_result.csv", encoding='utf-8-sig', index = False)

# gematchte Referenzen (df_sub) mit der Citavispalte 'Dokumententypus' mergen, um 
# später die Information verfügbar zu haben, worum es sich bei der Referenz handelt (Buch, Artikel etc.).
citnodup = citavi[['autorin titel In','Dokumententyp', 'Unterkat_Mono (= Freitext 1)']].drop_duplicates(subset='autorin titel In')
cit = citnodup.rename(columns = {'autorin titel In': 'Label', 'Dokumententyp':'Reftyp', 'Unterkat_Mono (= Freitext 1)' : 'Unterkat_Mono'})

mergedf = pd.merge(df_sub, cit, how='inner', on='Label').sort_values(by=['recnr'])
mergedf['Label'].isna().value_counts() # Es ist ein NA enthalten, muss raus.
mergedf_nonull = mergedf[pd.notnull(mergedf['Label'])]

# Anzahl der enthaltenen Lehrpläne
len(mergedf_nonull.recnr.value_counts())
# 169

# Speichern der 
mergedf_nonull.to_csv("20192801_Ref_pro_Lehrplan.csv", encoding='utf-8-sig', index = False)
