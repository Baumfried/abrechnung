#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, json, os, glob

DATENPFAD = 'Abrechnungsdaten'
os.makedirs(DATENPFAD, exist_ok=True)
personen = {}

class Person:
    def __init__(self, name, startsaldo=None, json_laden=False, json_pfad=DATENPFAD):
        if not isinstance(name, str):
            raise ValueError('Erstes Argument muss der Name der Person sein')
        
        global personen
        for person in personen.values():
            if re.match(name, person.name, re.I):
                raise ValueError('Es existiert bereits eine Person namens "' + person.name + '"')
        
        self.name = name
        self.positionen = []
        
        if json_laden:
            pfad_ganz = os.path.join(json_pfad, self.name + '.json')
            with open(pfad_ganz, 'r') as fh:
                self.positionen = json.load(fh)
        
        if startsaldo:
            if not isinstance(startsaldo, dict):
                raise ValueError('Das Argument startsaldo muss vom Typ dict sein')
            for gegenpartei, betrag in startsaldo.items():
                self.neue_position(gegenpartei, betrag)
        
        personen[self.name] = self
    
    def neue_position(self, other, betrag, betreff=None):
        if isinstance(other, Person):
            gegenpartei = other.name
            dynamic = True
        elif isinstance(other, str):
            gegenpartei = other
            dynamic = False
        else:
            raise ValueError('Erstes Argument muss entweder der Name oder die Instanz einer Person sein')
        
        if betreff:
            betreff = str(betreff)
        else:
            betreff = ''
        
        position = {'Gegenpartei': gegenpartei, 'Betrag': betrag, 'Betreff': betreff}
        gegenposition = {'Gegenpartei': self.name, 'Betrag': -betrag, 'Betreff': betreff}
        self.positionen.append(position)
        if dynamic: other.positionen.append(gegenposition)
    
    def zahlt(self, other, betrag, betreff='Zahlung'):
        self.neue_position(other, betrag, betreff)
    
    def bilanz(self, other=None):
        if other:
            if isinstance(other, Person):
                gegenpartei = other.name
            elif isinstance(other, str):
                gegenpartei = other
            else:
                raise ValueError('Erstes Argument muss entweder der Name oder die Instanz einer Person sein')
            return round(sum([position['Betrag'] for position in self.positionen if re.match(position['Gegenpartei'], gegenpartei, re.I)]), 2)
        else:
            return round(sum([position['Betrag'] for position in self.positionen]), 2)
    
    def positionen_speichern(self, pfad=DATENPFAD, verbose=True):
        pfad_ganz = os.path.join(pfad, self.name + '.json')
        if verbose:
            print('Speichere Daten von {:s} in {:s}...'.format(self.name, pfad_ganz), end=' ')
        with open(pfad_ganz, 'w') as fh:
            json.dump(self.positionen, fh)
        if verbose:
            print('✅')

def loesche(person):
    global personen
    if isinstance(person, str):
        instanz = personen.pop(person, None)
        del instanz
    elif isinstance(person, Person):
        personen.pop(person.name, None)
        del person

def rechnung_teilen(glaeubiger, schuldner, betrag, betreff):
    if isinstance(schuldner, Person):
        betrag_pp = round(betrag/2, 2)
        glaeubiger.neue_position(schuldner, betrag_pp, betreff)
    elif isinstance(schuldner, list):
        betrag_pp = round(betrag/(len(schuldner) + 1), 2)
        [glaeubiger.neue_position(s, betrag_pp, betreff) for s in schuldner]
    else:
        raise ValueError('Zweites Argument muss eine Person oder Liste von Personen sein')

def alle_speichern():
    global personen
    for person in personen.values():
        person.positionen_speichern()

def alle_laden(json_pfad=DATENPFAD):
    global personen
    muster_dateiname = re.compile(r'([^/]+)\.json;', re.I)
    gespeicherte_namen = muster_dateiname.findall(';'.join(glob.glob(json_pfad + '/*')) + ';')
    for name in gespeicherte_namen:
        personen[name] = Person(name, json_laden=True, json_pfad=json_pfad)