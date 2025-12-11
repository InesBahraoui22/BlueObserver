### Programme d'assignation des identifiants des produits copernicus, soient les variables destinées à se retrouver
### stocker dans le dossier "conditions_limitantes_sortie/conditions_marines"


# Fonction de récupération de l'identifiant du produit Copernicus contenant la variable : hauteur des vagues 

def recuperer_product_id_vagues(message = "Entrez l'identifiant du produit Copernicus que vous souhaitez utiliser. "
"Si vous ne proposez rien, le produit utilisé par les créateurs de ce programme sera exploité par défaut : ",
    produit_defaut_vagues = "GLOBAL_MULTIYEAR_WAV_001_032"):
    produit_id_vagues = input(f"{message} (défaut ={produit_defaut_vagues}) : ").strip()  # enlève les espaces au début/fin

    if produit_id_vagues == "":
        print(f"Aucun identifiant n'a été donné, utilisation du fichier par défaut : {produit_defaut_vagues}")
        return produit_defaut_vagues
    
    return produit_id_vagues

# Fonction de récupération de l'identifiant du produit Copernicus contenant la variable : température de la mer
def recuperer_product_id_temp(message = "Entrez l'identifiant du produit Copernicus que vous souhaitez utiliser. "
"Si vous ne proposez rien, le produit utilisé par les créateurs de ce programme sera exploité par défaut : ",
    produit_defaut_temp = "GLOBAL_MULTIYEAR_PHY_ENS_001_031"):
    produit_id_temp = input(f"{message} (défaut ={produit_defaut_temp}) : ").strip()  # enlève les espaces au début/fin

    if produit_id_vagues == "":
        print(f"Aucun identifiant n'a été donné, utilisation du fichier par défaut : {produit_defaut_temp}")
        return produit_defaut_temp
    
    return produit_id_temp
