
# Un diagramme en barres montre la relation entre une variable numérique et une variable catégorielle. 
# Chaque entité de la variable catégorielle est représentée par une barre. La taille de la barre représente sa 
# valeur numérique.

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt




def plot_Diagramme(valeurs, categories, title="Diagramme en Barres", x_label="Categories", y_label="Values"):
    """
    Crée un diagramme en barres avec des données personnalisées.
    Parameters:
    heights (list): Liste des valeurs numériques pour la hauteur des barres.
    categories (list): Liste des noms des catégories pour chaque barre.
    title (str): Titre du graphique (facultatif).
    x_label (str): Libellé de l'axe des x (facultatif).
    y_label (str): Libellé de l'axe des y (facultatif).
    """
    # Vérification de la cohérence des données
    if len(valeurs) != len(categories):
        raise ValueError("Le nombre de hauteurs et de catégories doit être identique.")

    # Générer les positions sur l'axe des x
    y_pos = np.arange(len(categories))
    plt.bar(y_pos, valeurs)# Créer les barres
    plt.xticks(y_pos, categories)# Ajouter les noms sur l'axe des x

    # Ajouter le titre et les labels
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # Afficher le graphique
    plt.show()

