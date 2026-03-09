# extract_gtfs.py
# Télécharge et extrait les fichiers GTFS depuis les sources réelles
import os
import zipfile
import urllib.request

RAW_DIR = "data/raw"

GTFS_SOURCES = {
    "sncf_ter": {
        "url":         "https://eu.ftp.opendatasoft.com/sncf/gtfs/export-ter-gtfs-last.zip",
        "description": "SNCF TER — trains régionaux France",
        "pays":        "FR",
    },
    "db_germany": {
        "url":         "https://download.gtfs.de/germany/fv_free/latest.zip",
        "description": "Deutsche Bahn — trains longue distance Allemagne",
        "pays":        "DE",
    },
    "sncb_belgium": {
        "url":         "https://gtfs.irail.be/nmbs/gtfs/latest.zip",
        "description": "SNCB/NMBS — trains Belgique",
        "pays":        "BE",
    },
    # "obb_austria": {  # URL morte — source temporairement désactivée
    #     "url":         "https://data.oebb.at/oebb?dataset=gtfs",
    #     "description": "ÖBB — trains Autriche",
    #     "pays":        "AT",
    # },
}

GTFS_FILES_ATTENDUS = [
    "agency.txt",
    "stops.txt",
    "routes.txt",
    "trips.txt",
    "stop_times.txt",
]


def telecharger_gtfs(nom, url, dest_dir):
    """Télécharge un fichier ZIP GTFS et l'extrait dans dest_dir."""
    os.makedirs(dest_dir, exist_ok=True)
    zip_path = os.path.join(dest_dir, f"{nom}.zip")

    print(f"\n📥 Téléchargement : {nom}")
    print(f"   URL : {url}")

    try:
        urllib.request.urlretrieve(url, zip_path)
        taille = os.path.getsize(zip_path)
        print(f"   ✅ Téléchargé ({taille // 1024} Ko)")
    except Exception as e:
        print(f"   ❌ Erreur téléchargement : {e}")
        return False

    print(f"   📦 Extraction dans {dest_dir}...")
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(dest_dir)
        os.remove(zip_path)
        print(f"   ✅ Extraction terminée")
        return True
    except Exception as e:
        print(f"   ❌ Erreur extraction : {e}")
        return False


def verifier_fichiers(dest_dir, source_nom):
    """Vérifie que les fichiers GTFS attendus sont présents."""
    print(f"\n🔍 Vérification [{source_nom}] :")
    ok = True
    for f in GTFS_FILES_ATTENDUS:
        path = os.path.join(dest_dir, f)
        if os.path.exists(path):
            taille = os.path.getsize(path)
            print(f"   ✅ {f} ({taille // 1024} Ko)")
        else:
            print(f"   ❌ {f} — MANQUANT")
            ok = False
    return ok


def run_extract_gtfs():
    print("=" * 60)
    print("EXTRACT — Téléchargement GTFS multi-sources")
    print("=" * 60)

    resultats = {}
    for nom, source in GTFS_SOURCES.items():
        dest_dir = os.path.join(RAW_DIR, nom)
        ok = telecharger_gtfs(nom, source["url"], dest_dir)
        if ok:
            ok = verifier_fichiers(dest_dir, nom)
        resultats[nom] = ok

    print("\n" + "=" * 60)
    print("RÉSUMÉ :")
    for nom, ok in resultats.items():
        statut = "✅" if ok else "❌"
        print(f"  {statut} {nom}")

    if all(resultats.values()):
        print("\n✅ Extract terminé — prêt pour le Transform !")
    else:
        print("\n⚠️  Certaines sources ont échoué.")

    return resultats


if __name__ == "__main__":
    run_extract_gtfs()
