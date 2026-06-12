from google.cloud import bigquery
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'api/credentials.json'
project_id = 'project-32a82952-90fa-4dd7-b9c'
client = bigquery.Client(project=project_id)

TABLE = f"`{project_id}.price_intelligence_dbt.prices_cleaned`"
ALLOWED_BQ_CATS = ['Informatique', 'Telephones & Smartphones', 'Electromenager']

# JUNK WORDS
CONTAINS_JUNK = [
    'livre', 'livres', 'roman', 'romans', 'histoire', 'histoires', 'history', 'book', 'books',
    'magazine', 'journal', 'oran', 'quran', 'chapelet', 'fable', 'fables', 'conte', 'contes',
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

# NUCLEAR REGEX (CURRENT)
NUCLEAR_REGEX = r'(?i)(' + '|'.join(CONTAINS_JUNK) + r')'

# SMART REGEX (PROPOSED - with boundaries but selective)
# Words that should ALWAYS have boundaries (like 'moto', 'auto', 'vitesse')
BOUNDED_JUNK = ['moto', 'auto', 'vitesse', 'boite', 'poche', 'vente', 'achat', 'location', 'local', 'cv', 'm2']
UNBOUNDED_JUNK = [w for w in CONTAINS_JUNK if w not in BOUNDED_JUNK]

SMART_REGEX = r'(?i)(\b(' + '|'.join(BOUNDED_JUNK) + r')\b|(' + '|'.join(UNBOUNDED_JUNK) + r'))'

print("Diagnosing False Positives...")

try:
    # Check how many are lost due to NUCLEAR vs SMART
    q_nuclear = f"SELECT name FROM {TABLE} WHERE REGEXP_CONTAINS(LOWER(name), r'{NUCLEAR_REGEX}')"
    q_smart = f"SELECT name FROM {TABLE} WHERE REGEXP_CONTAINS(LOWER(name), r'{SMART_REGEX}')"
    
    names_nuclear = set([row.name for row in client.query(q_nuclear).result()])
    names_smart = set([row.name for row in client.query(q_smart).result()])
    
    recovered = names_nuclear - names_smart
    print(f"Products lost to Nuclear but saved by Smart: {len(recovered)}")
    
    print("\nSample recovered products (should be technical):")
    for name in list(recovered)[:10]:
        print(f" - {name}")

    # Check Name Length impact
    q_len = f"SELECT name FROM {TABLE} WHERE LENGTH(name) >= 100 AND NOT REGEXP_CONTAINS(LOWER(name), r'{SMART_REGEX}')"
    long_names = list(client.query(q_len).result())
    print(f"\nProducts lost to Name Length (>100 chars): {len(long_names)}")
    for row in long_names[:10]:
        print(f" - {row.name}")

except Exception as e:
    print(f"Error: {e}")
