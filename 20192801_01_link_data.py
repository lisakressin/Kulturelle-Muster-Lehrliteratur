# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 16:03:26 2018
@author: KressinL

In dem Skript merge ich einen von mir erstellten Uniidentifier mit 
den Universitätsnamen einer anderen Tabelle. Die erste Tabelle
ist mein Datensatz mit allen tabellierten Syllabi aus der Methodenlehre.
"""
import os
import pandas as pd
import numpy as np

# Einlesen meiner Excel-Tabelle mit den Unicodes
identifier = pd.read_excel("031118 Modulverantwortliche_kurz.xlsx", sheet_name = "unis")
identifier.drop_duplicates(inplace = True)
identifier.dropna(how = "all", inplace = True)
identifier["uninr"] = identifier["uninr"].astype('int')
identifier = identifier.reset_index(drop=True)

# Dies Taelle enthält die Syllabi, die den Semesterzeitraum von WiSe15-SoSe18 abdecken.
df = pd.read_excel("271118_Lehrpläne_kurz.xlsx")

## Matchen von docnummer mit unicoder - uni als neue Spalte in den df einfügen

# die ersten zwei Ziffern der Docnummer verweisen auf den Unicode
docnr = df["Docnr."].str.extract("(^\d{2})|[?<=_]([^_]{2})")
docnr.columns = ["uninr", "out"]
docnr = docnr["uninr"].fillna(docnr["out"])

# Uninr an df andocken und für die Übersichtlichkeit an den Anfang der Tabelle.
df["uninr"] = docnr.astype("int")
cols = df.columns.tolist()
cols = cols[:1] + [cols[-1]] + cols[1:len(cols)-1]
df = df[cols]

# Nun über "uninr" (der Unicode) den df mit den Uninamen zusammenfügen.
df = pd.merge(df, identifier, on=['uninr'])
cols = df.columns.tolist()
cols = cols[:2] + [cols[-1]] + cols[2:len(cols)-1]
df = df[cols]
df.columns

## Matchen von docnummer mit BA oder MA Studieninfo
df["stufe"] = df["Docnr."].str.extract("(\d{2})[?=\s]")
df["stufe"] = np.where((df['stufe'] == "10") | (df['stufe'] == "11"), "BA", "MA")
cols = df.columns.tolist()
cols = cols[:3] + [cols[-1]] + cols[3:len(cols)-1]
df = df[cols]
df.columns

os.chdir("P:\SWITCHdrive\Datenauswertung\Python_Zeug\Zitationsnetzwerke\Datensaetze")
df.to_excel("20190128_lehrplaene_linked.xlsx", encoding='utf-8-sig', index = False)
