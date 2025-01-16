import requests, json

r1 = requests.get('https://api.bdnb.io/v1/bdnb/geocodage?',
             params={'q': "8 Rue de l'Église, 37260 Monts"}) 
a=r1.json()["features"][0]["properties"]['id']

r2 = requests.get('https://api.bdnb.io/v1/bdnb/donnees/batiment_groupe_complet/adresse',
             params={'cle_interop_adr': f'eq.{a}'} )  

print(json.dumps(r2.json(),indent = 4))