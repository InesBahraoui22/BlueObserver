### Programme d'assignation des identifiants des produits copernicus, soient les variables destinées à se retrouver
### stocker dans le dossier "conditions_limitantes_sortie/conditions_marines"

from datetime import datetime
import shutil
import xarray as xr
import pandas as pd
from pathlib import Path

# =================================================================================================================
# Fonction d'assignation de l'année la plus récente pour la récupération des données
# =================================================================================================================

def renseigner_annee_fin():
    """
    Retourne l'année actuelle et la liste des années allant de 2000 à cette année.
    """
    annee_fin = datetime.now().year
    annees = list(range(2000, annee_fin + 1))
    return annee_fin, annees

# ==================================================================================================================
# Fonction de récupération de l'identifiant du produit Copernicus contenant la variable : hauteur des vagues 
# ==================================================================================================================

def recuperer_product_id_vagues(
        message = "Entrez l'identifiant du produit Copernicus que vous souhaitez utiliser. "
        "\n Si vous ne proposez rien, le produit utilisé par les créateurs de ce programme sera exploité par défaut : ",
        produit_defaut_vagues = "GLOBAL_MULTIYEAR_WAV_001_032"):
    produit_id_vagues = input(f"{message} (défaut ={produit_defaut_vagues}) : ").strip()  # enlève les espaces au début/fin

    if produit_id_vagues == "":
        print(f"Aucun identifiant n'a été donné, utilisation du fichier par défaut : {produit_defaut_vagues}")
        return produit_defaut_vagues
    
    return produit_id_vagues


# =================================================================================================================
# Fonction de récupération de l'identifiant du produit Copernicus contenant la variable : température de la mer
# =================================================================================================================

def recuperer_product_id_temp(
        message = "Entrez l'identifiant du produit Copernicus que vous souhaitez utiliser. "
        "\n Si vous ne proposez rien, le produit utilisé par les créateurs de ce programme sera exploité par défaut : ",
        produit_defaut_temp = "GLOBAL_MULTIYEAR_PHY_ENS_001_031"):
    produit_id_temp = input(f"{message} (défaut ={produit_defaut_temp}) : ").strip()  # enlève les espaces au début/fin

    if produit_id_temp == "":
        print(f"Aucun identifiant n'a été donné, utilisation du fichier par défaut : {produit_defaut_temp}")
        return produit_defaut_temp
    
    return produit_id_temp

# =================================================================================================================
# Fonction de récupération des identifiants des datasets d'un produit Copernicus
# =================================================================================================================

def choisir_dataset_id(
        catalogue,
        message = "Entrez le nom du dataset dont vous souhaitez utiliser le panel de variables."
        "\n Si vous ne proposez rien, l'id du dataset du produit utilisé par les créateurs de ce programme sera "
        "\n exploité par défaut : ") :
    
    """
    Permet à l'utilisateur de choisir un dataset_id parmi ceux d'un catalogue Copernicus.

    - Affiche tous les dataset_id disponibles.
    - Demande à l'utilisateur d'en choisir un.
    - Si l'utilisateur ne choisit rien :
        → sélectionne automatiquement un dataset_id qui se termine par (-m) mensuel, (-d) journalier ou (-i) 
        horaire.
        → s'il n'y en a pas : lève une ValueError.
    - Si l'utilisateur choisit un dataset qui ne finit pas par (-m) mensuel, (-d) journalier ou (-i) horaire :
        → lève une ValueError avec explication.

    Paramètres
    ----------
    catalogue : CopernicusMarineCatalogue
        Résultat de cm.describe(product_id=...).
    suffixe_obligatoire : str
        Suffixe exigé pour le dataset (par défaut "-m").

    Retourne
    --------
    str
        Le dataset_id choisi.
    """

    datasets = catalogue.products[0].datasets
    dataset_ids = [d.dataset_id for d in datasets]

    print("Liste des datasets pour ce produit ; choisissez-en un :")
    for fichier_nc in dataset_ids:
        print(" -", fichier_nc)

    dataset_choisi = input(
        f"Si aucun choix n'est fait (vous appuyez sur Entrée), le choix se fera pour vous :").strip()

    if dataset_choisi == "":
        priorites = ["-m",
                     "-d",
                     "-i"]
        
        for suffixe in priorites :
            candidats = [fichier_nc for fichier_nc in dataset_ids if fichier_nc.endswith(suffixe)]
            if candidats :
                dataset_choisi = candidats[0]
                print(
                    f"Aucun choix n'a été fait, la sélection se fait automatiquement sur le"
                    "\n dataset mensuel : {dataset_choisi}")
                return dataset_choisi
        
        # si aucun dataset ne se termine avec un suffixe indiquant le pas d'observation :
        raise ValueError("Impossible de sélectionner automatiquement un dataset puisque leurs suffixes"
                         "\n sont non-existants ou ne permettent pas de connaître la périodicité de la "
                         "\n mesure ({priorites})."

        )
    
    if dataset_choisi not in dataset_ids:
        raise ValueError(
            f"Le dataset '{dataset_choisi}' renseigné ne correspond à aucun de ceux appartenant au produit")
    
    print(f"Le dataset selectionné est {dataset_choisi}")
    return dataset_choisi

# =================================================================================================================
# Fonction d'assignation automatique du dataset par défaut si détection du produit par défaut
# =================================================================================================================

def choisir_id_dataset_sachant_par_defaut(
        catalogue,
        product_id,
        mapping_defaut) :
    """
    Choisit un dataset_id pour un produit Copernicus, avec gestion de cas par défaut.

    - Si product_id est dans mapping_defauts :
        → on essaie de choisir le dataset indiqué dans mapping_defauts[product_id].
        → si ce dataset n'existe pas dans le catalogue : on bascule sur choisir_dataset_id().
    - Sinon :
        → on appelle directement choisir_dataset_id().

    Paramètres
    ----------
    catalogue : CopernicusMarineCatalogue
        Résultat de cm.describe(product_id=...).
    product_id : str
        Identifiant du produit choisi (par l'utilisateur ou par défaut).
    mapping_defauts : dict
        Dictionnaire {product_id: dataset_id_defaut}.

    Retourne
    --------
    str
        Le dataset_id retenu.
    """

    datasets = catalogue.products[0].datasets
    dataset_ids = [d.dataset_id for d in datasets]

    # Cas où on a un dataset par défaut associé à ce product_id
    if product_id in mapping_defaut :
        dataset_defaut = mapping_defaut[product_id]
        if dataset_defaut in dataset_ids :
            print(
                f"Le produit utilisé par les créateurs a été détecté ({product_id})."
                f"\n Par conséquent, le dataset concordant est utilisé par défaut : {dataset_defaut}"
            )
            return dataset_defaut
        else:
            print(
                f"Attention : le dataset par défaut '{dataset_defaut}' n'existe pas "
                "\ndans ce catalogue pour product_id = {product_id}.")
    return choisir_dataset_id(catalogue)

# ==============================================================================================================
# Fonction d'exploration et de choix des variables exploitées pour hauteur des vagues et température de la mer
# ==============================================================================================================

def choisir_variable_dans_dataset(
        catalogue,
        dataset_id,
        type_variable,
        mapping_vars_par_defaut = None) :
        
        
    """
    Affiche les variables d'un dataset donné et permet à l'utilisateur d'en choisir une.

    Paramètres
    ----------
    catalogue : CopernicusMarineCatalogue
        Résultat de cm.describe(product_id=...).
    dataset_id : str
        Nom du dataset (par ex. 'cmems_mod_glo_phy-all_my_0.25deg_P1D-m').
        En pratique : la valeur renvoyée par choisir_id_dataset_sachant_par_defaut().
    type_variable : str
        'temp' pour température de la mer, 'vagues' pour les vagues.
        Sert à faire un choix intelligent si l'utilisateur ne tape rien.
    mapping_vars_par_defaut : dict[str, str]
        Dictionnaire optionnel : {dataset_id: shortname_variable_par_defaut}.

    Retourne
    --------
    (str, str)
        (shortname de la variable à utiliser, unité associée)
    """
         
    if mapping_vars_par_defaut is None:
        mapping_vars_par_defaut = {}
    
    datasets = catalogue.products[0].datasets
    dataset_trouve = None
    for d in datasets :
        if d.dataset_id == dataset_id:
            dataset_trouve = d
            break
    
    if dataset_trouve is None :
        raise ValueError(
            f"Le dataset '{dataset_id}' est introuvable dans le catalogue."
            "\nVérifiez éventuellement l'orthographe."
        )
    
    variables_disponibles = dataset_trouve.versions[0].parts[0].services[0].variables
    shortnames_disponibles = [var.short_name for var in variables_disponibles]

    print(f"Variables disponibles dans le dataset '{dataset_id}' :")
    for var in variables_disponibles :
        print(f"Standard name : {var.standard_name}")
        print(f"Shortname     : {var.short_name}")
        print(f"Unité         : {var.units}")
        print(" ")

    var_defaut_dataset = mapping_vars_par_defaut.get(dataset_id, None)
    
    message = "Veuillez renseigner le short name de la variable que vous souhaitez retenir."
    if var_defaut_dataset is not None :
        message += f"Par défaut, la variable sera {var_defaut_dataset}"
    message += " : "

    short_name = input(message).strip()

    if short_name != "" :
        if short_name not in shortnames_disponibles :
            raise ValueError(f"La variable '{short_name}' n'existe pas dans le dataset retenu"
                             "\nVérifiez éventuellement l'orthographe."
            )
        print(f"La variable choisie est : {short_name}")
        unite = next(var.units for var in variables_disponibles if var.short_name == short_name)
        return short_name, unite

    if (var_defaut_dataset is not None) and (var_defaut_dataset in shortnames_disponibles) :
        print(
        "Aucun short_name n'a été renseigné et le dataset des créateurs du programme"
        "\nest détecté. Celui-ci et la variable ({var_defaut_dataset}) qu'ils ont utilisés vont être utilisés."
        )
        unite = next(var.units for var in variables_disponibles if var.short_name == var_defaut_dataset)
        return var_defaut_dataset, unite
    
    if type_variable == "vagues" :
        ["VHM0",
         "VHM0_WW",
         "VHM0_SW1", 
         "VHM0_SW2"]
    elif type_variable == "temp" :
        preferences = ["thetao_cglo",
                       "thetao_oras",
                       "thetao_glor",
                       "thetao",
                       "sst",
                       "tos"]
    else :
        preferences = []
    
    for candidat in preferences :
        if candidat in shortnames_disponibles :
            print(
                "Aucun short name n'a été renseigné mais le dataset utilisé est différent "
                f"\nde celui utilisé par les créateurs du programme pour le type '{type_variable}"
                f"\n : {candidat}"
            )
            unite = next(v.units for v in variables_disponibles if v.short_name == candidat)
            return candidat, unite
    
    raise ValueError(
        "Impossible de choisir automatiquement une variable. Il est nécessaire"
        "\n de renseigner manuellement le short name de la variable souhaitée,"
        "\n éventuellement de vérifier l'orthographe."
        
    )

# ==============================================================================================================
# Fonction de moyennage des fichiers .nc récupéré
# ==============================================================================================================


def moyennage_mensuelle_donnees_nc(dossier_nc : Path,
                                   variable_interet : str,
                                   dossier_sortie: Path) -> Path :
    """
    Prend tous les .nc d'un dossier, calcule la moyenne mensuelle
    toutes années confondues par point GPS, et écrit un CSV.
    Retourne le chemin du CSV créé.
    """

    # Ouvrir tous les fichiers NetCDF d'un coup, un par un c'est trop long et ça fait
    # planter le programme
    fichier_nc = xr.open_mfdataset(
        os.path.join(dossier_nc, "*.nc"),
        chunks = {'time': 100},
        combine = 'by_coords'
    )

    id_var_interet = fichier_nc[variable_interet]

    # Moyennes mensuelles (Conversion des données journalières/horaires en données mensuelles)
    id_var_mensuelle = id_var_interet.resample(time = '1MS').mean()

    # Moyennes toutes années confondues PAR MOIS et PAR POINT GPS
    moy_mensuelle = id_var_mensuelle.groupby("time.month").mean("time")

    # Conversion en tableau (avec latitude, longitude, mois)
    table_moy_mensuelle = moy_mensuelle.to_dataframe().reset_index()

    table_moy_mensuelle["month_name"] = pd.to_datetime(table_moy_mensuelle["month"], format="%m").dt.month_name()

    colonnes = ["month",
                "month_name"]
    if "latitude" in table_moy_mensuelle.columns :
        colonnes.extend(["latitude",
                         "longitude"])
    colonnes.append(variable_interet)
    table_moy_mensuelle = table_moy_mensuelle[colonnes]

    # Sauvegarde en CSV dans le dossier de sortie
    dossier_sortie.mkdir(parents = True,
                         exist_ok = True)
    fichier_sortie = dossier_sortie / f"moyennes_mensuelles_par_GPS_{variable_interet}.csv"
    table_moy_mensuelle.to_csv(fichier_sortie,
                               index = False)

    print(f"Fichier créé : {fichier_sortie}")

    fichier_nc.close()
    return fichier_sortie
