### Programme d'assignation des identifiants des produits copernicus, soient les variables destinées à se retrouver
### stocker dans le dossier "conditions_limitantes_sortie/conditions_marines"

# =================================================================================================================
# Fonction d'assignation de l'année la plus récente pour la récupération des données
# =================================================================================================================

def renseigner_dates_de_fin(date_fin,annee_fin) :
    date_fin = "2025-01-01T00:00:00"

    
    annee_fin = 2025
    annees = list(range(2000, annee_fin + 1))

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
                f"  Par conséquent, le dataset concordant est utilisé par défaut : {dataset_defaut}"
            )
            return dataset_defaut
        else:
            print(
                f"Attention : le dataset par défaut '{dataset_defaut}' n'existe pas "
                "dans ce catalogue pour product_id = {product_id}.")
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
    str
        Le shortname de la variable à utiliser.

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
            "Vérifiez éventuellement l'orthographe."
        )
    
    variables_disponibles = dataset_trouve?


