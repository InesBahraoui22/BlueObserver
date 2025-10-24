``` mermaid
gantt
    title  Pipeline et Développement du Projet — Finalisé avec Deadline & Oral
    dateFormat  YYYY-MM-DD
    axisFormat  %d/%m

    %% === Phase 1 : Préparation & Nettoyage ===
    section  Préparation & Nettoyage des données
    Nettoyage de données                      :a1, 2025-10-24, 3d
    Vérifier cohérence des données temporelles :a2, after a1, 2d
    Identifier le format des données temporelles (limite temporelle) :a3, after a2, 1d
    Matcher les coordonnées géographiques (limite géographique) :a4, after a3, 2d
    Gérer données manquantes / valeurs aberrantes / colonnes inutiles :a5, after a4, 3d
    Ajouter nom vernaculaire (FR/EN) des espèces :a6, after a5, 2d

    %% === Phase 2 : Transformation & Analyse ===
    section  Transformation & Analyse
    Transformer les points en moyennes mensuelles (météo/espèces) :b1, after a6, 3d
    Programme de collaboration des données :b2, after b1, 2d
    Définir zones géographiques / continents / fond de carte :b3, after b2, 3d

    %% === Phase 3 : Implémentation ===
    section  Implémentation technique
    Implémentation & mise en commun de l’environnement :c1, after b3, 7d
    Création du site (onglets fonctionnels) :c2, after c1, 4d

    %% === Phase 4 : Finalisation & Tests ===
    section  Tests, rédaction et relecture
    Rédaction des textes explicatifs :d1, after c2, 3d
    Tests & validation du site :d2, after d1, 3d
    Édition :d3, after d2, 2d
    Relecture finale :d4, after d3, 2d

    %% === Phase 5 : Soutenance ===
    section  Soutenance & préparation
    Préparation de l’oral :e1, after d4, 2d

    %% === Milestones ===
    Deadline (livrable final) :milestone_deadline, milestone, 2025-12-10, 0d
    Oral (soutenance)         :milestone_oral, milestone, 2025-12-12, 0d
