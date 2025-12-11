### Programme d'assignation des identifiants des produits copernicus, soient les variables destinées à se retrouver
### stocker dans le dossier "conditions_limitantes_sortie/conditions_marines"

# ==================================================================================================================
# Fonction de récupération de l'identifiant du produit Copernicus contenant la variable : hauteur des vagues 
# ==================================================================================================================

def recuperer_product_id_vagues(
        message = "Entrez l'identifiant du produit Copernicus que vous souhaitez utiliser. "
        "Si vous ne proposez rien, le produit utilisé par les créateurs de ce programme sera exploité par défaut : ",
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
        "Si vous ne proposez rien, le produit utilisé par les créateurs de ce programme sera exploité par défaut : ",
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
        "Si vous ne proposez rien, l'id du dataset du produit utilisé par les créateurs de ce programme sera "
        "exploité par défaut : ") :
    
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
    for ds in dataset_ids:
        print(" -", ds)

    dataset_choisi = input(
        f"Si aucun choix n'est fait (vous appuyez sur Entrée), le choix se fera pour vous :").strip()

    if dataset_choisi == "":
        priorites = ["-m",
                     "-d",
                     "-i"]
        
        for suffixe in priorites :
            candidats = [ds for ds in dataset_ids if ds.endswith(suffixe)]
            if candidats :
                dataset_choisi = candidats[0]
                print(
                    f"Aucun choix n'a été fait, la sélection se fait automatiquement sur le"
                    "dataset mensuel : {dataset_choisi}")
                return dataset_choisi
        
        # si aucun dataset ne se termine avec un suffixe indiquant le pas d'observation :
        raise ValueError("Impossible de sélectionner automatiquement un dataset puisque leurs suffixes"
                         "sont non-existants ou ne permettent pas de connaître la périodicité de la "
                         "mesure ({priorites})."

        )
    
    if dataset_choisi not in dataset_ids:
        raise ValueError(
            f"Le dataset '{}' renseigné ne correspond à aucun de ceux appartenant au produit"
        )
    
    print(f"Le dataset selectionné est {dataset_choisi}")
    return dataset_choisi
