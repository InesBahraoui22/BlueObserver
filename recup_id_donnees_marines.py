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

def choisir_dataset_id_temp(
        catalogue
        suffixe_obligatoire = "-m",
        message = "Entrez le nom du dataset dont vous souhaitez utiliser le panel de variables."
        "Si vous ne proposez rien, l'id du dataset du produit utilisé par les créateurs de ce programme sera exploité"
        "par défaut : ",                          
        dataset_id_defaut_temp = "cmems_mod_glo_phy-all_my_0.25deg_P1D-m") :
    
    dataset_id_temp = input(f"{message} (défaut ={dataset_id_defaut_temp}) : ").strip()

    if dataset_id_temp == "":
        print(f"Aucun identifiant n'a été donné, utilisation du du dataset du fichier par défaut : {dataset_id_defaut_temp}")
        return dataset_id_defaut_temp
    
    return dataset_id_temp

def choisir_dataset_id(catalogue, suffixe_obligatoire="-m"):
    """
    Permet à l'utilisateur de choisir un dataset_id parmi ceux disponibles 
    dans un catalogue Copernicus.

    Paramètres
    ----------
    catalogue : CopernicusMarineCatalogue
        Catalogue obtenu via cm.describe().
    suffixe_obligatoire : str
        Le suffixe que doit obligatoirement contenir le dataset_id (ex : '-m').

    Retourne
    --------
    str
        Le dataset_id choisi par l'utilisateur.

    Exceptions
    ----------
    ValueError : si le choix n'existe pas ou ne respecte pas le suffixe requis.
    """

    # Extraction de tous les datasets disponibles
    datasets = catalogue.products[0].datasets  
    dataset_ids = [d.dataset_id for d in datasets]

    print("\n📌 Datasets disponibles :")
    for ds in dataset_ids:
        print("  -", ds)

    # Demander à l'utilisateur
    choix = input("\nEntrez le dataset_id souhaité : ").strip()

    # Vérifier l'existence
    if choix not in dataset_ids:
        raise ValueError(f"Dataset inconnu : '{choix}'. Choisissez parmi la liste affichée.")

    # Vérifier le suffixe obligatoire
    if not choix.endswith(suffixe_obligatoire):
        raise ValueError(
            f"Le dataset '{choix}' ne termine pas par '{suffixe_obligatoire}'. "
            "Ce dataset n'est pas compatible avec la climatologie mensuelle."
        )

    print(f"→ Dataset sélectionné : {choix}")
    return choix