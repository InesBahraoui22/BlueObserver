# création de classe Observation (mais difficile a utiliser car il me faudrait restructurer TOUT le code)
class Observation:
    """Classe ultra-simple sans risque d'erreur."""
    
    def __init__(self, data):
        # 1. Copie les données en sécurité
        if data and isinstance(data, dict):
            self.data = data.copy()
        else:
            self.data = {}
        
        # 2. Ajoute region (valeur simple pour tester)
        self.data['region'] = "Méditerranée"
        
        # 3. Ajoute wave_class (valeur simple pour tester)
        self.data['wave_class'] = 2
    
    def to_dict(self):
        """Retourne les données enrichies."""
        return self.data  