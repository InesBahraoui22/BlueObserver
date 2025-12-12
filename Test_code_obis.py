###################################################################################################
######################### Importation des fichiers OBIS par codage ################################
###################################################################################################


# ÉTAPE 1 | Importation des packages nécessaires pour réaliser la manipulation

import os # Pour lire et écrire des fichiers

import csv # Pour fabriquer un fichier csv au lieu de tsv

import time # D'après la documentation, ça évite de surcharger le serveur, 
            # du coup je fais pas les requêtes d'un coup comme une brute

import datetime as dt # Pour pouvoir manipuler une plage temporelle, 
                      # pour que je puisse définir la fin de la période 
                      # par "aujourd'hui"

import requests # LE PLUS IMPORTANT : pour appeler une API web,
                # faire la technique vaudou pour invoquer internet depuis 
                # ce code

from urllib.parse import quote # Pour éviter le problème des caratères 
                               # spéciaux :)))

#________________________________________________________________________________________________


# ÉTAPE 2 | Définition des paramètres de filtration

LON_MIN, LON_MAX = -25.0, 45.0 # Ouest, Est
LAT_MIN, LAT_MAX = 27.0, 69.0 # Sud, Nord

START_DATE = "2000-01-01" # Date définie comme début pour tous les fichiers

END_DATE = dt.date.today().isoformat() # "aujourd'hui" au format AAAA-MM-JJ ou 
                                       # en eng YYYY-MM-DD

SPECIES = "Delphinus delphis" # Un exemple au hasard

OUT_CSV = "Delphinus_delphis.csv" # Nom du fichier 

SIZE    = 10000 # D'après la docu toujours, OBIS autorise au max 10 000 enregistrements
                # par requête donc je dois morceler ma requête total en plusieurs 
                # sous-requêtes.
SLEEP   = 0.2 # Ça va avec la ligne du dessus, si je surcharge le serveur avec mes multiples
              # et lourdes requêtes on m'avertit que je risque de me faire bloquer, 
              # donc faut aussi des pauses (=sleep) entre deux sous-requêtes.

FIELDS = ["scientificName","decimalLongitude","decimalLatitude","eventDate",]
        # En fait j'ai plein de colonnes qui sont téléchargées par défaut, mais toutes 
        # ne sont pas utiles. On a au total :
        # - scientificName   → je garde
        # -	taxonRank        → inutile, je vire
        # - aphiaID          → inutile, je vire
        # - species          → inutile, je vire
        # - decimalLongitude → je garde
        # - decimalLatitude  → je garde	
        # - eventDate	     → je garde, va être très utile par la suite
        # - date_year	     → inutile, je vire
        # - basisOfRecord    → inutile, je vire	
        # - datasetID	     → inutile, je vire
        # - datasetName	     → inutile, je vire
        # - occurrenceID	 → inutile, je vire
        # - institutionCode  → inutile, je vire	
        # - country	         → inutile, je vire
        # - depth	         → inutile, je vire																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																


BASE = "https://api.obis.org/v3/occurrence" # Adresse de l'API OBIS, là où mes requêtes partent

# POLYGÔNE(ordre lon lat obligatoire) AM zone de délimitation
polygone = (f"POLYGON(({LON_MIN} {LAT_MIN},{LON_MAX} {LAT_MIN},"
       f"{LON_MAX} {LAT_MAX},{LON_MIN} {LAT_MAX},{LON_MIN} {LAT_MIN}))")
#________________________________________________________________________________________________


# ÉTAPE 3 |  APPEL SONDE : récupérer du total exact avant de boucler pour éviter de pédaler dans
# le vide
probe_url = (f"{BASE}?scientificname={quote(SPECIES)}"
             f"&geometry={quote(polygone)}" # ma zone de délimitation encodée avec quote()
             f"&startdate={START_DATE}&enddate={END_DATE}" # la période définie
             f"&size=1&offset=0"
             f"&hasCoordinate=true")  # SUPER IMPORTANT APRÈS PLEIN D'ERREURs : si pas de
                                      # coordonnées géographique, la ligne est filtrée



probe = requests.get(probe_url, timeout = 120) # Ça, ça appelle l'API

probe.raise_for_status() # ligne aussi super importante, s'il y a une erreur du côté d'internet,
                         # mon programme boucle pas dans le vide

meta = probe.json()      # Convertit la réponse à ma requête en langage python

TOTAL = meta.get("total", 0) # LIGNE SUPER IMPORTANTE : le programme pédale pas dans le vide en
                             # m'inventant des observations qui n'existent pas. Elle me donne 
                             # le vrai nombre d'occurrences que je peux voir sur la page web et
                             # le garde pour se limiter.
print(f"Total annoncé par l'API pour ces filtres : {TOTAL}")


#________________________________________________________________________________________________

# ÉTAPE 4 | Pré-fabrication du fichier : sécurité si le programme crash ou internet crash pour 
# par recommencer du début

STATE = "offset.state" # Fichier texte dans lequel s'inscrit le offset = le nombre de lignes 
                       # déjà produites
OFFSET = int(open(STATE).read()) if os.path.exists(STATE) else 0


#________________________________________________________________________________________________

# ÉTAPE 5 | Pagination contrôlée par TOTAL : fabrication du CSV

writer = None # outil qui écrit, il commence par le début = vide, rien
enregistrees = 0 if OFFSET == 0 else OFFSET  # Mon compteur des lignes qui se téléchargent au
                                           # fur-et-à-mesure

with open(OUT_CSV, "a", newline="", encoding="utf-8") as f: # "a" = ajout soit dans un 
                                                            # fichier tout nouveau, soit qui 
                                                            # reprend là où le fichier
                                                            # aurait été interrompu
    while OFFSET < TOTAL:  # Fonctionne avec l'ÉTAPE 4, pour justement me limiter aux occurences
                           # qui existent vraiment 
        remaining = TOTAL - OFFSET
        page_size = SIZE if remaining >= SIZE else remaining # cette ligne et la précédente
                                                             # permettent de respecter la taille
                                                             # limite d'une page imposée par 
                                                             # OBIS

        url = (f"{BASE}?scientificname={quote(SPECIES)}"
               f"&geometry={quote(polygone)}" # prend la zone qui m'intéresse
               f"&startdate={START_DATE}&enddate={END_DATE}"
               f"&size={page_size}&offset={OFFSET}" # prend le nombre d'occurences (TOUTES) qui 
                                                    # m'interréssent
               f"&fields={quote(','.join(FIELDS))}" # prend les colonnes qui m'intéressent
               f"&hasCoordinate=true")



        requete = requests.get(url,
                               timeout = 180, # me dit si ça marche pas au bout de 2 min de 
                                              # tentative
                               headers = {"Accept-Encoding":"gzip"}) # compresse en gzip
                                                                     # pour gagner du temps
                                                                     # d'exécution
        requete.raise_for_status()
        data = requete.json() # D'après la docu, ça m'assure que ça sert à convertir en python la
                              # la réponse de l'API OBIS.

        nbre_lignes = data.get("results", []) # récupération des résultats, y compris s'il n'y en
                                              # a pas. S'il n'y en a pas, ça interrompt la boucle
        if not nbre_lignes:
            print("Page vide renvoyée. On s'arrête.")
            break

        # Ce if sert à faire comprendre qu'OBIS a des titres pour les colonnes
        if writer is None:
            headers = list({k for row in nbre_lignes for k in row.keys()})
            ordered = [c for c in FIELDS if c in headers] + [c for c in headers if c not in FIELDS]
            writer = csv.DictWriter(f, fieldnames = ordered)
            writer.writeheader()

        # Ce for permet d'écrire les lignes une par une
        for ligne in nbre_lignes :
            writer.writerow(ligne)

        n = len(nbre_lignes)
        enregistrees += n # Met à jour le compteur de lignes enregistrées
        #  La ligne ci-dessous me donne des infos sur l'avancement de la manip
        print(f"Page offset={OFFSET} -> {n} lignes (cumul={enregistrees}/{TOTAL})")

        OFFSET += n  # Met à jour le pas de la boucle
        with open(STATE, "w") as s: s.write(str(OFFSET))
        time.sleep(SLEEP)

print(f"✅ Terminé (ou stoppé proprement). Lignes écrites : {enregistrees}/{TOTAL}")

