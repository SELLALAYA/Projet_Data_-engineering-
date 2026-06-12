from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'credentials.json'
client = bigquery.Client(project='project-32a82952-90fa-4dd7-b9c')

ALLOWED_BQ_CATS = ['Informatique', 'Telephones & Smartphones', 'Electromenager']
START_JUNK = ['pochette', 'coque', 'etui', 'étui', 'protecteur', 'verre trempé', 'incassable', 'film', 'cable', 'câble', 'adaptateur', 'chargeur', 'batterie externe', 'power bank', 'station de charge', 'tapis de souris', 'sac à dos', 'sacoche', 'housse', 'cartouche', 'toner', 'encre', 'papier photo', 'porte-clés', 'mousqueton', 'support mural', 'support pc', 'support rotatif']
START_JUNK_REGEX = r'(?i)^(' + '|'.join(START_JUNK) + r')\b'

CONTAINS_JUNK = [
    'livre', 'livres', 'roman', 'romans', 'histoire', 'histoires', 'history', 'book', 'books',
    'magazine', 'journal', 'coran', 'quran', 'chapelet', 'fable', 'fables', 'conte', 'contes',
    'manga', 'bd', 'bande dessinée', 'encyclopédie', 'dictionnaire', 'cahier', 'nouvelle',
    'cravate', 'djellaba', 'chemise', 'pantalon', 'robe', 't-shirt', 'chaussures', 'chaussure',
    'nike', 'rolex', 'parfum', 'cosmétique', 'bijoux', 'montre', 'lunettes', 'sac', 'valise',
    'vêtement', 'vetement', 'veste', 'manteau', 'tricot', 'poche', 'auteur', 'écrivain',
    'villa', 'appartement', 'terrain', 'maison', 'sarout', 'local', 'fonds de commerce', 'bureau',
    'voiture', 'auto', 'moto', 'vélo', 'velo', 'dacia', 'renault', 'peugeot', 'mercedes', 'bmw',
    'audi', 'hyundai', 'kia', 'fiat', 'véhicule', 'vehicule', 'camion', 'moteur', 'jantes',
    'pneu', 'pare-choc', 'pare choc', 'volkswagen', 'ford', 'nissan', 'toyota', 'golf', 'clio',
    'jouet', 'meuble', 'salon', 'canapé', 'lit', 'chaise', 'table', 'armoire', 'pack monde',
    'pièces', 'pieces', 'pièce', 'piece', 'chambres', 'chambre', 'salon', 'étage', 'etage',
    'm2', 'm²', 'vente', 'location', 'louer', 'immobilier', 'résidence', 'residence', 'lotissement',
    'rivet', 'clip', 'pneu', 'frein', 'amortisseur', 'phare', 'calandre', 'rétroviseur', 'enjoliveur',
    'vendre', 'achat', 'acheter', 'occasion', 'km', 'kilométrage', 'boite', 'vitesse', 'diesel',
    'essence', 'hybride', 'portes', 'cylindrée', 'chevaux', 'cv', 'fiscal', 'marrakech', 'casablanca',
    'rabat', 'tanger', 'agadir', 'fès', 'meknès', 'oujda', 'kénitra', 'tétouan', 'temara',
    'mètre', 'metre', 'hectare', 'titré', 'titre', 'r+1', 'r+2', 'r+3', 'r+4', 'r+5', 'zone',
    'industriel', 'commercial', 'façade', 'facade', 'modèle', 'modéle', 'automatique', 'manuelle'
]
BOUNDED_JUNK = [
    'moto', 'auto', 'm2', 'cv', 'vitesse', 'boite', 'poche', 'vente', 'achat', 'location', 
    'local', 'bureau', 'étage', 'etage', 'chambre', 'pièce', 'piece', 'pièces', 'pieces',
    'mètre', 'metre', 'km', 'modèle', 'modéle', 'zone', 'titre', 'titré'
]
UNBOUNDED_JUNK = [w for w in CONTAINS_JUNK if w not in BOUNDED_JUNK]
CONTAINS_JUNK_REGEX = r'(?i)(\b(' + '|'.join(BOUNDED_JUNK) + r')\b|(' + '|'.join(UNBOUNDED_JUNK) + r'))'

EXCLUDE_FILTERS = [
    "price > 100",
    "price < 150000",
    f"(category IN ({', '.join([f"'{c}'" for c in ALLOWED_BQ_CATS])}) OR (LOWER(name) LIKE '%tv%' OR LOWER(name) LIKE '%tablet%' OR LOWER(name) LIKE '%ipad%'))",
    f"NOT REGEXP_CONTAINS(LOWER(name), r'{START_JUNK_REGEX}')",
    f"NOT REGEXP_CONTAINS(LOWER(name), r'{CONTAINS_JUNK_REGEX}')",
    "LENGTH(name) < 300",
    "(source != 'avito.ma' OR (price BETWEEN 250 AND 50000))",
    "LOWER(name) NOT LIKE '%appartement%'",
    "LOWER(name) NOT LIKE '%villa%'",
    "LOWER(name) NOT LIKE '%terrain%'"
]
EXCLUDE_WHERE = " AND ".join(EXCLUDE_FILTERS)
TABLE = '`project-32a82952-90fa-4dd7-b9c.price_intelligence_dbt.prices_cleaned`'

query = f"SELECT COUNT(*) as total FROM {TABLE} WHERE {EXCLUDE_WHERE}"
print(f"Executing query: {query}")
try:
    res = list(client.query(query).result())
    print(f"Total results: {res[0].total}")
except Exception as e:
    print(f"Query FAILED: {e}")
