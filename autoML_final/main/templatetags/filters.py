# filters.py

from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """Accède à une clé dans un dictionnaire."""
    return dictionary.get(key, 'Clé non trouvée')  # Valeur par défaut si la clé n'existe pas

@register.filter
def dict_get_key_by_value(dictionary, value):
    """Trouve la clé correspondant à une valeur dans un dictionnaire."""
    # Recherche la clé associée à la valeur
    for key, val in dictionary.items():
        if val == value:
            return key
    return 'Valeur non trouvée'