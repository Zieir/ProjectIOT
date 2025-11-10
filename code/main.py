from GraphStruct import create_example_graph, count_routes, SimpleGraph
from Display import show_all_heuristics, show_colorful


# Exemple A : graphe d'exemple existant
g = create_example_graph()
print("Graphe d'exemple : affichage coloré et nombre de routes")
show_colorful(g)
print("Nombre de routes de 1 à 11 :", count_routes(g, 1, 11))


# Exemple B : construction à partir d'une liste d'arêtes (formats flexibles)
edge_list = [
    ("A", "B", 2, 5),
    ("B", "C", 3),        # poids unique -> tmin = tmax
    ("C", "D"),           # pas de poids -> utilise la valeur par défaut
]
g2 = SimpleGraph.from_edge_list(edge_list, directed=True, default_weight=(1, 1))
print("Graphe construit depuis la liste d'arêtes, noeuds :", g2.nodes())
show_colorful(g2)


# Exemple C : construction à partir d'un dictionnaire d'adjacence
adj = {
    "x": {"y": (3, 7), "z": 4},  # mélange tuple et scalaire
    "y": {"z": (2, 6)},
}
g3 = SimpleGraph.from_adj_dict(adj, directed=False)
print("Graphe depuis dict d'adjacence, arêtes :", g3.edges())
show_colorful(g3)
# Optionnel : renommer en entiers consécutifs (utile pour certains algorithmes/visualiseurs)
g3_int, mapping = g3.relabel_to_ints(start=1)
print("Renommage des noeuds :", mapping)

# --- Optional: demonstrate loading graphs from files if present ---
import os
here = os.path.dirname(__file__)
csv_path = os.path.join(here, 'example_edges.csv')
json_path = os.path.join(here, 'example_graph.json')
edgelist_path = os.path.join(here, 'example_edgelist.txt')

if os.path.exists(csv_path):
    print('Loading graph from CSV:', csv_path)
    gf = SimpleGraph.from_csv(csv_path, has_header=True)
    print('Loaded', len(gf.nodes()), 'nodes from CSV')
elif os.path.exists(json_path):
    print('Loading graph from JSON:', json_path)
    gf = SimpleGraph.from_json(json_path)
    print('Loaded', len(gf.nodes()), 'nodes from JSON')
elif os.path.exists(edgelist_path):
    print('Loading graph from edge-list file:', edgelist_path)
    gf = SimpleGraph.from_edgelist_file(edgelist_path)
    print('Loaded', len(gf.nodes()), 'nodes from edge-list')
else:
    print('No example graph files found (put example_edges.csv, example_graph.json or example_edgelist.txt in code/)')





#========================================= interactive HTML display ======================================
show_all_heuristics(g, 1, 11, port=8050)


#g = create_example_graph()
#g.show_colorful()
##g.draw_plotly()
#g_mean = g.make_converge(n_samples=1000)
#g_mean.show_colorful()
#
#g.draw_dash(port=8050)
#
#
#
#
##============================================ Additional criteria =================================================
##Empirical mean minimisation citeria
#path, val = best_path(g_mean, 1, 11, cost_min, maximize=False)
#print("Itinéraire optimiste :", path, "→ Temps min total :", val)
#g_mean.draw_dash(port=8050, path=path, heuristic_name="Gaussian Path", path_length=val)
#
#
##=========================================== Non abstract algorithms ===========================================
#print("\nNon-abstract algorithms results:")
#path, time = worst_case(g, 1, 11)
#g.draw_dash(port=8050, path=path, heuristic_name="Worst Case", path_length=time)
#
#print("Plus long chemin de 1 à 11 :", path, ". Temps max :", time)
#path, marge = most_stable_path(g, 1, 11)
#print("Itinéraire stable (1 → 11) :", path, "Marge de fluctuation minimale :", marge)
#g.draw_dash(port=8050, path=path, heuristic_name="Most Stable Path", path_length=marge)
#
##============================================= Abstract Algorithms ===============================================
#print("\n\nAbstract algorithms results:")
## Itinéraire optimiste (plus court chemin, minimisant le temps min)
#path, val = best_path(g, 1, 11, cost_min, maximize=False)
#print("Itinéraire optimiste :", path, "→ Temps min total :", val)
#g.draw_dash(port=8050, path=path, heuristic_name="Optimistic Path", path_length=val)
#
## Itinéraire prudent (plus long chemin, minimisant le temps max)
#path, val = best_path(g, 1, 11, cost_max, maximize=False)
#print("Itinéraire prudent :", path, "→ Temps max total :", val)
#g.draw_dash(port=8050, path=path, heuristic_name="Prudent Path", path_length=val)
#
## Itinéraire stable (plus court chemin, minimisant la marge)
#path, val = best_path(g, 1, 11, cost_marge, maximize=False)
#print("Itinéraire stable :", path, "→ Marge totale :", val)
#g.draw_dash(port=8050, path=path, heuristic_name="Stable Path", path_length=val)
#
## Itinéraire pire cas (plus long chemin, maximisant le temps max)
#path, val = best_path(g, 1, 11, cost_max, maximize=True)
#print("Pire Itinéraire :", path, "→ Temps max total :", val)
#g.draw_dash(port=8050, path=path, heuristic_name="Worst Path", path_length=val)
#
