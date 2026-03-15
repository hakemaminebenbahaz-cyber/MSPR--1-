# find_sources.py - Version avec sources directes
import urllib.request
import csv
import os

def get_direct_gtfs_sources():
    """
    Retourne une liste de sources GTFS ferroviaires fiables
    """
    
    print("Compilation des sources GTFS ferroviaires fiables...")
    
    # Sources GTFS ferroviaires connues et fiables
    direct_sources = [
        {
            'name': 'SNCF French Rail',
            'url': 'https://eu.ftp.opendatasoft.com/sncf/gtfs/export-ter-gtfs-last.zip',
            'country': 'FR',
            'description': 'Donnees TER SNCF France - trains regionaux'
        },
        {
            'name': 'SNCF Transilien',
            'url': 'https://eu.ftp.opendatasoft.com/sncf/gtfs/export-transilien-gtfs-last.zip',
            'country': 'FR', 
            'description': 'Reseau Transilien Ile-de-France'
        },
        {
            'name': 'DB German Rail',
            'url': 'https://download.gtfs.de/germany/fv_free/latest.zip',
            'country': 'DE',
            'description': 'Deutsche Bahn - trains longue distance'
        },
        {
            'name': 'OBB Austrian Rail',
            'url': 'https://static.data.gv.at/ogd/9c4a7f2d-8b96-4b5f-8b6a-8b6b4b5f8b6b/GTFS.zip',
            'country': 'AT',
            'description': 'OBB Austria - reseau ferroviaire autrichien'
        },
        {
            'name': 'Back-on-Track Night Trains',
            'url': 'https://back-on-track.eu/night-trains/',
            'country': 'EU',
            'description': 'Base de donnees des trains de nuit europeens (site web a scraper)'
        }
    ]
    
    print(f"SUCCES: {len(direct_sources)} sources ferroviaires compilees !")
    print("\nSources disponibles :")
    
    for i, source in enumerate(direct_sources, 1):
        print(f"   {i}. {source['name']} ({source['country']})")
        print(f"      URL: {source['url']}")
        print(f"      Description: {source['description']}")
        print()
    
    # Sauvegarde la liste
    save_sources_to_csv(direct_sources)
    
    return direct_sources

def test_download_gtfs():
    """
    Test le telechargement d'un petit GTFS pour verification
    """
    print("\nTest de telechargement GTFS...")
    
    # URL de test (SNCF TER - relativement petit)
    test_url = "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-ter-gtfs-last.zip"
    output_path = "data/raw/test_sncf_ter.zip"
    
    try:
        # Cree le dossier si besoin
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"Telechargement depuis: {test_url}")
        urllib.request.urlretrieve(test_url, output_path)
        
        # Verifie la taille du fichier
        file_size = os.path.getsize(output_path)
        print(f"SUCCES: Fichier telecharge - {file_size} octets")
        print(f"Emplacement: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"ERREUR telechargement: {e}")
        return False

def save_sources_to_csv(sources, filename="data/raw/sources_list.csv"):
    """Sauvegarde les sources en CSV"""
    if not sources:
        return
        
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'url', 'country', 'description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for source in sources:
            writer.writerow(source)
    
    print(f"Liste des sources sauvegardee dans: {filename}")

if __name__ == "__main__":
    print("=" * 60)
    print("SOURCES GTFS FERROVIAIRES - VERSION DIRECTE")
    print("Utilisation de sources fiables pre-identifiees")
    print("=" * 60)
    
    sources = get_direct_gtfs_sources()
    
    if sources:
        # Test de telechargement
        print("TEST DE CONNEXION:")
        download_ok = test_download_gtfs()
        
        print("\nPROCHAINES ETAPES:")
        print("1. Les URLs ci-dessus sont directement utilisables")
        print("2. Le test de telechargement montre si la connexion fonctionne")
        print("3. Explorer le fichier GTFS telecharge dans data/raw/")
        
        if download_ok:
            print("\n✅ Pret pour l'etape suivante: extraction des donnees GTFS!")
        else:
            print("\n❌ Probleme de connexion - verifie ton acces internet")