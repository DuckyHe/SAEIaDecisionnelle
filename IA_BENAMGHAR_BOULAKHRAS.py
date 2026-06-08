##############################################################################
# votre IA : à vous de coder
# Rappel : ne pas changer les paramètres des méthodes
# vous pouvez ajouter librement méthodes, fonctions, champs, ...
##############################################################################
    
import random

class IA_Bomber:
    """
    Classe représentant une IA pour le jeu Bomber.
    
    Cette IA utilise une stratégie basée sur la recherche de minerais tout en évitant les dangers.
    Elle peut alterner entre différents modes : recherche de minerai, fuite, et attente.
    
    Attributes:
        num_joueur (int): Numéro identifiant le joueur (requis par BB_IA_start.py)
        largeur (int): Largeur de la carte de jeu
        hauteur (int): Hauteur de la carte de jeu
        derniere_bombe (int): Tour où la dernière bombe a été posée
        objectif_actuel (tuple): Coordonnées (x,y) de l'objectif actuel
        chemin_vers_objectif (list): Liste des directions à suivre pour atteindre l'objectif
        mode_actuel (str): Mode actuel de l'IA ("CHERCHER_MINERAI", "FUIR", "ATTENDRE")
        cache_chemins (dict): Cache des chemins sûrs précédemment calculés
    """
    
    def __init__(self, num_joueur: int, game_dic: dict, timerglobal: int, timerfantôme: int) -> None:
        """
        Initialise l'IA du Bomber.
        
        Args:
            num_joueur (int): Numéro du joueur
            game_dic (dict): Dictionnaire contenant l'état du jeu
            timerglobal (int): Timer global du jeu
            timerfantôme (int): Timer des fantômes
        """
        self.num_joueur = num_joueur
        self.largeur = len(game_dic['map'][0])
        self.hauteur = len(game_dic['map'])
        self.derniere_bombe = -5
        self.objectif_actuel = None
        self.chemin_vers_objectif = []
        self.mode_actuel = "CHERCHER_MINERAI"
        self.cache_chemins = {}
        
    def calculer_chemin(self, debut: tuple, fin: tuple, game_dict: dict) -> list:
        """
        Trouve le chemin le plus court et sûr entre deux points sur la carte.
        
        Utilise un algorithme BFS (Breadth-First Search) modifié pour tenir compte
        des dangers et des obstacles.
        
        Args:
            debut (tuple): Coordonnées (x,y) de départ
            fin (tuple): Coordonnées (x,y) d'arrivée
            game_dict (dict): État actuel du jeu
            
        Returns:
            list: Liste des directions ('H','B','G','D') pour atteindre la destination,
                 liste vide si aucun chemin n'est trouvé
        """
        if debut == fin:
            return []
            
        visites = set()  # Ensemble des positions déjà visitées
        queue = [(debut, [])]  # File pour le BFS: (position, chemin)
        
        # Dictionnaire des directions possibles avec leurs deltas (dx, dy)
        directions = {'H': (0,-1), 'B': (0,1), 'G': (-1,0), 'D': (1,0)}
        
        while queue:
            (x, y), chemin = queue.pop(0)
            
            if (x, y) == fin:
                return chemin
                
            # Explorer chaque direction possible
            for direction, (dx, dy) in directions.items():
                nx, ny = x + dx, y + dy  # Nouvelle position
                # Vérifier si la nouvelle position est valide et sûre
                if ((nx, ny) not in visites and 
                    0 <= nx < self.largeur and 
                    0 <= ny < self.hauteur and 
                    game_dict['map'][ny][nx] != 'C' and  # Pas de collision avec un mur
                    self.calculer_niveau_danger(nx, ny, game_dict) < 2):  # Position suffisamment sûre
                    visites.add((nx, ny))
                    nouveau_chemin = chemin + [direction]
                    queue.append(((nx, ny), nouveau_chemin))
        return []

    def calculer_niveau_danger(self, x: int, y: int, game_dict: dict) -> float:
        """
        Évalue le niveau de danger d'une position donnée.
        
        Prend en compte les bombes, les fantômes et les autres joueurs.
        
        Args:
            x (int): Coordonnée x de la position à évaluer
            y (int): Coordonnée y de la position à évaluer
            game_dict (dict): État actuel du jeu
            
        Returns:
            float: Score de danger (0 = sûr, 999 = danger mortel)
        """
        danger = 0
        # Danger mortel si dans la portée d'une bombe
        for bombe in game_dict['bombes']:
            bx, by = bombe['position']
            portee = bombe['portée']
            # Si sur la même ligne ou colonne que la bombe et dans sa portée
            if (x == bx and abs(y - by) <= portee) or (y == by and abs(x - bx) <= portee):
                return 999
        
        # Danger croissant à proximité des fantômes
        for fantome in game_dict['fantômes']:
            fx, fy = fantome['position']
            distance = abs(x - fx) + abs(y - fy)
            if distance <= 2:  # Danger si fantôme à 2 cases ou moins
                danger += (3 - distance) * 2  # Plus le fantôme est proche, plus le danger est grand
                
        # Léger danger à proximité des autres joueurs
        for bomber in game_dict['bombers']:
            if bomber['num_joueur'] != self.num_joueur:
                bx, by = bomber['position']
                distance = abs(x - bx) + abs(y - by)
                if distance <= 2:  # Danger si autre joueur à 2 cases ou moins
                    danger += 1
                    
        return danger

    def localiser_meilleur_minerai(self, x: int, y: int, game_dict: dict) -> tuple:
        """
        Trouve le minerai le plus accessible et le moins dangereux à partir d'une position.
        
        Args:
            x (int): Coordonnée x de la position actuelle
            y (int): Coordonnée y de la position actuelle
            game_dict (dict): État actuel du jeu
            
        Returns:
            tuple: Coordonnées (x,y) du meilleur minerai trouvé, None si aucun minerai accessible
        """
        meilleur_score = float('inf')
        meilleur_minerai = None
        
        for yi in range(self.hauteur):
            for xi in range(self.largeur):
                if game_dict['map'][yi][xi] == 'M':
                    distance = abs(x - xi) + abs(y - yi)
                    danger = self.calculer_niveau_danger(xi, yi, game_dict)
                    chemin = self.calculer_chemin((x, y), (xi, yi), game_dict)
                    
                    if chemin:  # Si un chemin existe
                        score = len(chemin) + danger * 2
                        if score < meilleur_score:
                            meilleur_score = score
                            meilleur_minerai = (xi, yi)
        
        return meilleur_minerai

    def action(self, game_dict: dict) -> str:
        """
        Détermine la prochaine action à effectuer par l'IA.
        
        Cette méthode est requise par BB_IA_start.py et implémente la logique principale
        de l'IA, alternant entre la recherche de minerai et la fuite selon le niveau de danger.
        
        Args:
            game_dict (dict): État actuel du jeu
            
        Returns:
            str: Action à effectuer ('H','B','G','D','X','N')
                 H=Haut, B=Bas, G=Gauche, D=Droite, X=Poser une bombe, N=Ne rien faire
        """
        # Trouver notre position
        ma_position = None
        for bomber in game_dict['bombers']:
            if bomber['num_joueur'] == self.num_joueur:
                ma_position = bomber['position']
                break
        
        if not ma_position:
            return 'N'  # Si position non trouvée, ne rien faire
            
        x, y = ma_position
        danger_actuel = self.calculer_niveau_danger(x, y, game_dict)
        
        # Passer en mode FUIR si niveau de danger trop élevé
        if danger_actuel > 2:
            self.mode_actuel = "FUIR"
            self.objectif_actuel = None
            self.chemin_vers_objectif = []
            
            # Recherche de la direction la plus sûre pour fuir
            meilleur_danger = float('inf')
            meilleure_direction = None
            
            for direction, (dx, dy) in {'H': (0,-1), 'B': (0,1), 'G': (-1,0), 'D': (1,0)}.items():
                nx, ny = x + dx, y + dy
                # Vérifier si la nouvelle position est valide
                if (0 <= nx < self.largeur and 
                    0 <= ny < self.hauteur and 
                    game_dict['map'][ny][nx] != 'C'):
                    danger = self.calculer_niveau_danger(nx, ny, game_dict)
                    if danger < meilleur_danger:
                        meilleur_danger = danger
                        meilleure_direction = direction
            
            return meilleure_direction if meilleure_direction else 'N'
        
        # Mode normal : chercher des minerais
        self.mode_actuel = "CHERCHER_MINERAI"
        
        # Si pas d'objectif ou objectif atteint, en chercher un nouveau
        if not self.objectif_actuel or ma_position == self.objectif_actuel:
            self.objectif_actuel = self.localiser_meilleur_minerai(x, y, game_dict)
            if self.objectif_actuel:
                self.chemin_vers_objectif = self.calculer_chemin((x, y), self.objectif_actuel, game_dict)
        
        # Si adjacent à un minerai, poser une bombe
        if self.objectif_actuel:
            mx, my = self.objectif_actuel
            if abs(x - mx) + abs(y - my) == 1:
                if game_dict['compteur_tour'] - self.derniere_bombe >= 5:
                    # Vérifier une sortie sûre
                    for direction, (dx, dy) in {'H': (0,-1), 'B': (0,1), 'G': (-1,0), 'D': (1,0)}.items():
                        nx, ny = x + dx, y + dy
                        if ((nx, ny) != (mx, my) and 
                            0 <= nx < self.largeur and 
                            0 <= ny < self.hauteur and
                            game_dict['map'][ny][nx] != 'C' and
                            self.calculer_niveau_danger(nx, ny, game_dict) < 1):
                            self.derniere_bombe = game_dict['compteur_tour']
                            return 'X'
        
        # Suivre le chemin si disponible
        if self.chemin_vers_objectif:
            return self.chemin_vers_objectif.pop(0)
            
        return 'N'



