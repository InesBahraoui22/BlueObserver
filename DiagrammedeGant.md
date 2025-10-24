``` mermaid
gantt
    title Pipeline et Développement du Projet
    dateFormat  YYYY-MM-DD
    axisFormat  %d/%m

    section  Préparation & Nettoyage des données
    Nettoyage de données                      :a1, 2025-10-24, 3d
    Vérifier cohérence des données temporelles :a2, after a1, 2d
    Identifier le format des données temporelles (limite temporelle) :a3, after a2, 1d
    Matcher les coordonnées géographiques (limite géographique) :a4, after a3, 2d
    Gérer données manquantes / valeurs aberrantes / colonnes inutiles :a5, after a4, 3d
    Ajouter nom vernaculaire (FR/EN) des espèces :a6, after a5, 2d

    section Transformation & Analyse
    Transformer les points en moyennes mensuelles (météo/espèces) :b1, after a6, 3d
    Programme de collaboration des données :b2, after b1, 2d
    Définir zones géographiques / continents / fond de carte :b3, after b2, 3d

    section Implémentation technique
    Implémentation & mise en commun de l’environnement :c1, after b3, 7d
    Création du site (onglets fonctionnels) :c2, after c1, 4d

    section  Rédaction & finalisation
    Rédaction des textes explicatifs :d1, after c2, 3d
    Édition :d2, after d1, 2d
    Relecture finale :d3, after d2, 2d
