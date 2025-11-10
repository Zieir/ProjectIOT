import numpy as np

class SimpleGraph:
    """
    Graphe orienté ou non, avec arêtes contenant deux poids : temps_min et temps_max.
    Représentation : adj[u][v] = (temps_min, temps_max)
    """
    def __init__(self, directed=False):
        self.directed = directed
        self.adj = {}

    def add_node(self, v):
        if v not in self.adj:
            self.adj[v] = {}

    def add_edge(self, u, v, temps_min, temps_max):
        """Ajoute une arête u->v avec deux poids (temps_min, temps_max)."""
        # Validate and normalize weights so temps_min <= temps_max
        try:
            # allow types that support comparison (numbers)
            if temps_min is None or temps_max is None:
                raise TypeError('temps_min and temps_max must be numeric and not None')
            if temps_min > temps_max:
                # swap to ensure order and inform the user
                import warnings
                warnings.warn(f'add_edge: temps_min ({temps_min}) > temps_max ({temps_max}) - swapping the values', UserWarning)
                temps_min, temps_max = temps_max, temps_min
        except TypeError:
            raise TypeError('temps_min and temps_max must be comparable numeric values')

        self.add_node(u)
        self.add_node(v)
        self.adj[u][v] = (temps_min, temps_max)
        if not self.directed:
            self.adj[v][u] = (temps_min, temps_max)

    def remove_edge(self, u, v):
        if u in self.adj and v in self.adj[u]:
            del self.adj[u][v]
        if not self.directed and v in self.adj and u in self.adj[v]:
            del self.adj[v][u]

    def remove_node(self, v):
        if v not in self.adj:
            return
        for nbrs in self.adj.values():
            nbrs.pop(v, None)
        del self.adj[v]

    def neighbors(self, v):
        return dict(self.adj.get(v, {}))

    def nodes(self):
        return list(self.adj.keys())

    def edges(self):
        edges = []
        seen = set()
        for u, nbrs in self.adj.items():
            for v, (tmin, tmax) in nbrs.items():
                if self.directed or (v, u) not in seen:
                    edges.append((u, v, tmin, tmax))
                    seen.add((u, v))
        return edges

    def has_node(self, v):
        return v in self.adj

    def has_edge(self, u, v):
        return u in self.adj and v in self.adj[u]

    def degree(self, v):
        return len(self.adj.get(v, {}))

    def noisy_edge_mean_gauss(self, tmin, tmax, noise_scale=1.0, n_samples=1000):
        """
        Utilise Beta pour créer des gaussiennes décentrées de façon contrôlée
        """
        # Choisir aléatoirement la densité de trafic
        profile = np.random.choice(['fluide', 'normal', 'dense'])
        
        if profile == 'fluide':
            # Trafic fluide => pic vers tmin
            alpha, beta = 2, 5
        elif profile == 'dense':
            # Trafic dense => pic vers tmax
            alpha, beta = 5, 2
        else:
            # Normal => pic au centre
            alpha, beta = 2, 2

        # Générer la position du centre
        beta_sample = np.random.beta(alpha, beta)
        mu = tmin + beta_sample * (tmax - tmin)
        
        # Écart-type
        std = (tmax - tmin) / (5 + noise_scale)
        
        # Générer échantillons
        samples = np.random.normal(mu, std, n_samples)
        samples = samples[(samples >= tmin) & (samples <= tmax)]
        
        if len(samples) == 0:
            return mu
        
        return np.mean(samples)

    def noisy_edge_mean_beta(self, tmin, tmax, n_samples=1000, 
                    congestion_speed=0.1, liberation_every=100, liberation_force=0.3):
    
        """
        Simule une route i.i.d avec du trafic qui évolue dans le temps.
        
        Imagine : tu observes cette route pendant 1000 moments différents.
        Le trafic s'accumule progressivement, puis se libère de temps en temps.
        
        Paramètres:
        -----------
        tmin, tmax : temps min et max du trajet (en minutes par exemple)
        n_samples : combien de "moments" on observe
        congestion_speed : vitesse d'accumulation du trafic (0.0 = aucune, 1.0 = rapide)
        liberation_every : tous les combien de moments la route se libère
        liberation_force : intensité de la libération (0.0 = aucune, 1.0 = complète)
        """
    
        initial_state = np.random.choice(['fluide', 'normal', 'dense'])
        
        if initial_state == 'fluide':
            alpha_start, beta_start = 2, 5
            alpha_limit, beta_limit = 5, 2
        elif initial_state == 'dense':
            alpha_start, beta_start = 5, 2
            alpha_limit, beta_limit = 2, 5
        else:
            alpha_start, beta_start = 2, 2
            alpha_limit, beta_limit = 3, 3
        
        observed_times = []
        alpha = alpha_start
        beta = beta_start
        
        for moment in range(n_samples):     
            beta_sample = np.random.beta(alpha, beta)
            travel_time = tmin + beta_sample * (tmax - tmin)
            observed_times.append(travel_time)
            
            if moment > 0 and moment % liberation_every == 0:
                alpha -= (alpha - alpha_start) * liberation_force
                beta -= (beta - beta_start) * liberation_force
            
            progress = moment / n_samples
            alpha += (alpha_limit - alpha) * congestion_speed * 0.01
            beta += (beta_limit - beta) * congestion_speed * 0.01
            
            alpha = np.clip(alpha, 0.5, 10)
            beta = np.clip(beta, 0.5, 10)
        
        valid_times = [t for t in observed_times if tmin <= t <= tmax]
        
        if len(valid_times) == 0:
            return (tmin + tmax) / 2
        
        return np.mean(valid_times)

    def make_converge(self, beta = False, n_samples=1000):
        """
        Pour chaque arête, crée une gaussienne bruitée ou une distribution beta
        et estime la moyenne empirique, ces lois simule la circulation des vehiécules 
        en temps réel.
        On renvoies un nouveau graphe avec ces valeurs.
        """
        g = SimpleGraph(directed=self.directed)
        noise_scale = np.random.uniform(0, 0.5)

        for u, v, tmin, tmax in self.edges():
            if beta:
                mean_estimee = self.noisy_edge_mean_beta(tmin, tmax, n_samples)
            else:
                mean_estimee = self.noisy_edge_mean_gauss(tmin, tmax, noise_scale, n_samples)
            g.add_node(u)
            g.add_node(v)
            g.add_edge(u, v, round(mean_estimee,2), round(mean_estimee,2))
        return g

    # ------------------------------------------------------------------
    # Constructeurs alternatifs et utilitaires
    # ------------------------------------------------------------------
    @classmethod
    def from_edge_list(cls, edges, directed=False, default_weight=(1, 1)):
        """Construire un SimpleGraph à partir d'un itérable d'arêtes.

        Chaque élément de `edges` peut être :
          - (u, v, tmin, tmax)
          - (u, v, w)  -> tmin = tmax = w
          - (u, v)     -> tmin, tmax = default_weight
        """
        g = cls(directed=directed)
        for e in edges:
            if len(e) >= 4:
                u, v, tmin, tmax = e[0], e[1], e[2], e[3]
            elif len(e) == 3:
                u, v, w = e
                tmin = tmax = w
            elif len(e) == 2:
                u, v = e
                tmin, tmax = default_weight
            else:
                # skip malformed entries
                continue
            g.add_edge(u, v, tmin, tmax)
        return g

    @classmethod
    def from_adj_dict(cls, adj_dict, directed=False):
        """Construire un SimpleGraph à partir d'un dictionnaire de dictionnaires
        représentant la structure d'adjacence.

        On s'attend à ce que adj_dict[u][v] soit soit un tuple (tmin, tmax),
        soit une seule valeur (dans ce cas tmin = tmax).
        """
        g = cls(directed=directed)
        for u, nbrs in adj_dict.items():
            for v, w in nbrs.items():
                if isinstance(w, (tuple, list)) and len(w) >= 2:
                    tmin, tmax = w[0], w[1]
                else:
                    tmin = tmax = w
                g.add_edge(u, v, tmin, tmax)
        return g

    @classmethod
    def from_dataframe(cls, df, u_col='u', v_col='v', tmin_col='tmin', tmax_col='tmax', directed=False):
        """Construire un SimpleGraph à partir d'un DataFrame pandas contenant les arêtes en ligne.

        Le DataFrame doit comporter des colonnes pour la source et la destination et au moins une colonne de poids.
        Si `tmax_col` est absente, la valeur de `tmin_col` est utilisée pour les deux poids.
        """
        try:
            import pandas as _pd  # optional dependency
        except Exception:
            _pd = None
        if _pd is None:
            raise RuntimeError('pandas is required to build a graph from a DataFrame')
        if not set([u_col, v_col]).issubset(df.columns):
            raise ValueError(f'DataFrame must contain columns {u_col} and {v_col}')

        g = cls(directed=directed)
        for _, row in df.iterrows():
            u = row[u_col]
            v = row[v_col]
            if tmin_col in df.columns:
                tmin = row[tmin_col]
            elif 'weight' in df.columns:
                tmin = row['weight']
            else:
                raise ValueError('No weight column found (expected tmin or weight)')

            if tmax_col in df.columns:
                tmax = row[tmax_col]
            else:
                tmax = tmin

            g.add_edge(u, v, tmin, tmax)
        return g

    def relabel_to_ints(self, start=1):
        """Return a new graph with nodes relabeled to consecutive integers starting at `start`.

        Returns (new_graph, mapping) where mapping maps old_label -> new_int.
        """
        nodes = list(self.nodes())
        mapping = {old: i for i, old in enumerate(nodes, start)}
        g = SimpleGraph(directed=self.directed)
        for u, v, tmin, tmax in self.edges():
            g.add_edge(mapping[u], mapping[v], tmin, tmax)
        return g, mapping

    @classmethod
    def from_csv(cls, file_path, directed=False, u_col='u', v_col='v', tmin_col='tmin', tmax_col='tmax', has_header=True, default_weight=(1,1)):
        """Charger un graphe depuis un fichier CSV.

        Si `has_header` est True, le CSV doit contenir des colonnes nommées par u_col/v_col
        et au moins une colonne de poids (tmin_col ou 'weight'). Si has_header est False,
        chaque ligne est supposée contenir 2, 3 ou 4 colonnes (u, v[, tmin[, tmax]]).
        """
        import csv
        g = cls(directed=directed)
        with open(file_path, newline='') as fh:
            if has_header:
                reader = csv.DictReader(fh)
                # Vérifier présence des colonnes source/destination
                if not set([u_col, v_col]).issubset(reader.fieldnames):
                    raise ValueError(f'CSV doit contenir les colonnes {u_col} et {v_col}')
                for row in reader:
                    u = row[u_col]
                    v = row[v_col]
                    # Récupérer tmin : préférence à la colonne tmin, sinon 'weight', sinon valeur par défaut
                    if tmin_col in reader.fieldnames and row.get(tmin_col, '') != '':
                        tmin = cls._safe_number(row[tmin_col])
                    elif 'weight' in reader.fieldnames and row.get('weight', '') != '':
                        tmin = cls._safe_number(row['weight'])
                    else:
                        tmin = default_weight[0]

                    # Récupérer tmax : si absent, on reprend tmin (ou valeur par défaut si tmin est None)
                    if tmax_col in reader.fieldnames and row.get(tmax_col, '') != '':
                        tmax = cls._safe_number(row[tmax_col])
                    else:
                        tmax = tmin if tmin is not None else default_weight[1]

                    g.add_edge(u, v, tmin, tmax)
            else:
                reader = csv.reader(fh)
                for row in reader:
                    # Ignorer lignes vides ou mal formées
                    if len(row) >= 4:
                        u, v, tmin, tmax = row[0], row[1], cls._safe_number(row[2]), cls._safe_number(row[3])
                    elif len(row) == 3:
                        u, v, w = row[0], row[1], cls._safe_number(row[2])
                        tmin = tmax = w
                    elif len(row) == 2:
                        u, v = row[0], row[1]
                        tmin, tmax = default_weight
                    else:
                        continue
                    g.add_edge(u, v, tmin, tmax)
        return g

    @classmethod
    def from_json(cls, file_path, directed=False):
        """Charger un graphe depuis un fichier JSON.

        Accepte soit un dictionnaire d'adjacence (u -> {v: poids ou [tmin,tmax]})
        soit une liste d'arêtes ([u,v] ou [u,v,w] ou [u,v,tmin,tmax]).
        """
        import json
        with open(file_path) as fh:
            obj = json.load(fh)

        if isinstance(obj, dict):
            return cls.from_adj_dict(obj, directed=directed)
        elif isinstance(obj, list):
            return cls.from_edge_list(obj, directed=directed)
        else:
            raise ValueError('Format JSON non supporté : attendu dict ou list')

    @classmethod
    def from_edgelist_file(cls, file_path, directed=False, sep=None, default_weight=(1,1)):
        """Charger un fichier d'arêtes simple (séparateur espace ou personnalisé).

        Chaque ligne non vide doit contenir 2, 3 ou 4 tokens : u v [w] [w2].
        """
        g = cls(directed=directed)
        with open(file_path) as fh:
            for line in fh:
                line = line.strip()
                # Ignorer commentaires et lignes vides
                if not line or line.startswith('#'):
                    continue
                parts = line.split() if sep is None else line.split(sep)
                if len(parts) >= 4:
                    u, v, tmin, tmax = parts[0], parts[1], cls._safe_number(parts[2]), cls._safe_number(parts[3])
                elif len(parts) == 3:
                    u, v, w = parts[0], parts[1], cls._safe_number(parts[2])
                    tmin = tmax = w
                elif len(parts) == 2:
                    u, v = parts[0], parts[1]
                    tmin, tmax = default_weight
                else:
                    continue
                g.add_edge(u, v, tmin, tmax)
        return g

    @staticmethod
    def _safe_number(val):
        """Essaye de convertir une valeur en int ou float, renvoie None si vide, lève sinon.

        Retourne int si possible, sinon float. Lève ValueError si conversion impossible.
        """
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return val
        s = str(val).strip()
        if s == '':
            return None
        try:
            # Prioriser int si pas de point décimal ni exposant
            if '.' in s or 'e' in s or 'E' in s:
                return float(s)
            return int(s)
        except Exception:
            try:
                return float(s)
            except Exception:
                raise ValueError(f'Impossible de parser la valeur numérique : {val}')

            

def create_example_graph():
    g = SimpleGraph(directed=True)

    for n in range(1, 12):
        g.add_node(n)
        
    g.add_edge(1, 2, 3, 7)
    g.add_edge(1, 3, 4, 6)
    g.add_edge(1, 4, 3, 8)
    g.add_edge(2, 5, 2, 5)
    g.add_edge(3, 5, 5, 8)
    g.add_edge(3, 6, 4, 6)
    g.add_edge(4, 6, 7, 10)
    g.add_edge(4, 7, 3, 8)
    g.add_edge(5, 8, 4, 9)
    g.add_edge(6, 8, 2, 4)
    g.add_edge(6, 9, 5, 6)
    g.add_edge(7, 9, 2, 4)
    g.add_edge(7, 10, 4, 7)
    g.add_edge(8, 11, 3, 7)
    g.add_edge(9, 11, 3, 6)
    g.add_edge(10, 11, 3, 4)

    return g


#################Partie 1 - Question 1######################
def count_routes(graph, start, end):
    """Compte le nombre de routes de start à end, seulement sur les graphs acycliques."""
    def dfs(node, stops):
        if node == end and stops > 0:
            return 1
        count = 0
        for neighbor in graph.neighbors(node):
            count += dfs(neighbor, stops + 1)
        return count
    return dfs(start, 0)

"""
Unused Codes
#import networkx as nx
#import matplotlib.pyplot as plt
#import dash
#from dash import html
#import dash_cytoscape as cyto
#import scipy.stats

    def show(self):
            print(f"{'Graphe orienté' if self.directed else 'Graphe non orienté'} :")
            for u, nbrs in self.adj.items():
                if self.directed:
                    arrows = ", ".join(
                        f"→ {v} ({tmin}-{tmax})" for v, (tmin, tmax) in nbrs.items()
                    )
                else:
                    arrows = ", ".join(
                        f"{v} ({tmin}-{tmax})" for v, (tmin, tmax) in nbrs.items()
                    )
                print(f"  {u}: {arrows}")
            print(f"→ {len(self.nodes())} sommets, {len(self.edges())} arêtes\n")

    def noisy_edge_mean(self, tmin, tmax, noise_scale, n_samples=1000):
        mu = np.mean([tmin, tmax])
        std = (tmax - tmin) / 6
        # Ajout de bruit à la moyenne
        mu_bruite = mu + np.random.normal(0, noise_scale * std)
        # Générer des échantillons de la gaussienne
        samples = np.random.normal(mu_bruite, std, n_samples)
        samples = samples[(samples >= tmin) & (samples <= tmax)]
        # Estimer la nouvelle moyenne
        if len(samples) == 0:
            return np.clip(mu_bruite, tmin, tmax)
        return np.mean(samples)


    def draw(self, layout="spring"):
        Dessine le graphe joliment, avec choix du layout.
        G = nx.DiGraph() if self.directed else nx.Graph()

        for u, nbrs in self.adj.items():
            for v, (tmin, tmax) in nbrs.items():
                G.add_edge(u, v, label=f"{tmin}-{tmax}")

        # --- Choix du layout ---
        if layout == "spring":
            pos = nx.spring_layout(G, seed=42, k=0.8)  # layout "élastique"
        elif layout == "circular":
            pos = nx.circular_layout(G)
        elif layout == "planar":
            pos = nx.planar_layout(G)
        else:
            pos = nx.kamada_kawai_layout(G)

        # --- Création du graphe ---
        plt.figure(figsize=(7, 6))
        nx.draw_networkx_nodes(G, pos, node_size=2000, node_color="#5DADE2", edgecolors="black")
        nx.draw_networkx_labels(G, pos, font_color="white", font_weight="bold")

        nx.draw_networkx_edges(
            G, pos,
            arrowstyle="->" if self.directed else "-",
            arrowsize=20,
            width=2,
            edge_color="#34495E"
        )

        edge_labels = nx.get_edge_attributes(G, "label")
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color="#1B2631", font_size=9)

        # --- Ajustement et titre ---
        plt.title("Graphe orienté" if self.directed else "Graphe non orienté", fontsize=14, fontweight="bold")
        plt.axis("off")
        plt.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.05)
        plt.show()
    
"""


"""
    def to_cytoscape_elements(self):
        Convertit le graphe en format Cytoscape (nodes + edges).
        elements = []
        # Nodes
        for node in self.adj:
            elements.append({"data": {"id": node, "label": node}})
        # Edges
        for u, nbrs in self.adj.items():
            for v, (tmin, tmax) in nbrs.items():
                # Pour les graphes non orientés, éviter les doublons
                if not self.directed and any(e for e in elements if e.get("data", {}).get("source") == v and e.get("data", {}).get("target") == u):
                    continue
                elements.append({"data": {"source": u, "target": v, "label": f"{tmin}-{tmax}"}})
        return elements

    def draw_dash(self, port=8050, path=None, heuristic_name=None, path_length=None):
        app = dash.Dash(__name__)
        elements = self.to_cytoscape_elements()

        # Repérer les arêtes et nœuds du chemin
        path_edges = set()
        path_nodes = set(path) if path else set()
        if path and len(path) > 1:
            for i in range(len(path) - 1):
                path_edges.add((str(path[i]), str(path[i+1])))
                if not self.directed:
                    path_edges.add((str(path[i+1]), str(path[i])))

        # Stylesheet avec coloration du chemin
        stylesheet = [
            {'selector': 'node',
            'style': {
                'content': 'data(label)',
                'background-color': '#4e79a7',
                'color': 'white',
                'text-valign': 'center',
                'text-halign': 'center',
                'width': 50,
                'height': 50,
                'font-size': 14,
                'font-weight': 'bold'
            }},
            {'selector': 'edge',
            'style': {
                'label': 'data(label)',
                'curve-style': 'bezier',
                'target-arrow-shape': 'vee' if self.directed else 'none',
                'line-color': '#34495E',
                'target-arrow-color': '#34495E',
                'font-size': 16,
                'text-background-color': '#FFFFFF',
                'text-background-opacity': 0.8,
                'text-margin-y': -10,
                'color': '#FF5733'
            }},
        ]

        for node in path_nodes:
            stylesheet.append({
                'selector': f'node[id = "{node}"]',
                'style': {
                    'background-color': '#27ae60',
                    'border-width': 4,
                    'border-color': '#145a32'
                }
            })

        for u, v in path_edges:
            stylesheet.append({
                'selector': f'edge[source = "{u}"][target = "{v}"]',
                'style': {
                    'line-color': '#e040fb',
                    'target-arrow-color': '#e040fb',
                    'width': 5
                }
            })

        # Affichage du nom de l'heuristique et de la taille du chemin
        header = []
        if heuristic_name:
            header.append(html.H3(f"Heuristique : {heuristic_name}", style={"color": "#e67e22"}))
        if path_length is not None:
            header.append(html.H4(f"Taille du chemin : {path_length}", style={"color": "#27ae60"}))

        app.layout = html.Div(
            header + [
                cyto.Cytoscape(
                    id='cytoscape-graph',
                    elements=elements,
                    style={'width': '100%', 'height': '600px'},
                    layout={'name': 'cose'},
                    userZoomingEnabled=True,
                    userPanningEnabled=True,
                    boxSelectionEnabled=True,
                    autoungrabify=False,
                    stylesheet=stylesheet
                )
            ]
        )

        print(f"\nOuvrez navigateur à http://127.0.0.1:{port} pour voir le graphe interactif")
        app.run(debug=False, port=port)
"""
