# filters.py

from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    """Accède à une clé dans un dictionnaire."""
    return dictionary.get(key, 'Clé non trouvée')  # Valeur par défaut si la clé n'existe pas
