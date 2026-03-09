# extract_opendata.py
# Extraction REELLE depuis l'Open Night Train Database (Back-on-Track)
# Source: https://back-on-track.eu/projects/open-night-train-database/
# Donnees: Google Sheets public - 400+ trains de nuit europeens

import sys
import requests
import pandas as pd
import csv
import io
import os
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")


SHEET_ID = "15zsK-lBuibUtZ1s2FxVHvAmSu-pEuE0NDT6CAMYL2TY"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

USEFUL_COLUMNS = [
    "route_id", "agency_id", "trip_id",
    "trip_origin", "origin_departure_time",
    "trip_headsign", "destination_arrival_time",
    "trip_short_name", "countries", "is_active",
    "classes", "duration", "distance",
    "emissions_co2e", "co2_per_km", "via"
]


class OpenNightTrainExtractor:
    def __init__(self):
        self.data_dir = "data/raw/opendata"
        os.makedirs(self.data_dir, exist_ok=True)

    def extract_back_on_track(self):
        """
        Extrait les donnees reelles sur les trains de nuit europeens
        depuis l'Open Night Train Database (Back-on-Track / Google Sheets public).
        ~400 trajets actifs et inactifs en Europe.
        """
        print("\n" + "=" * 60)
        print("EXTRACTION - OPEN NIGHT TRAIN DATABASE (BACK-ON-TRACK)")
        print("=" * 60)
        print(f"Source: {SHEET_URL}")

        try:
            print("Telechargement du Google Sheet public...")
            r = requests.get(
                SHEET_URL,
                headers={"User-Agent": "ObRail-ETL/1.0"},
                timeout=30
            )
            r.raise_for_status()

            # Parse CSV
            content = r.content.decode("utf-8", errors="replace")
            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)

            if not rows:
                print("❌ Aucune ligne recue")
                return None

            print(f"   → {len(rows)} lignes telechargees")

            df = pd.DataFrame(rows)

            # Garder uniquement les colonnes utiles qui existent
            cols_present = [c for c in USEFUL_COLUMNS if c in df.columns]
            df = df[cols_present].copy()

            # Nettoyage de base
            df["is_active"] = df["is_active"].str.strip().str.upper()
            df_active = df[df["is_active"] == "Y"].copy()

            # Nettoyer les champs numeriques
            for col in ["distance", "duration", "emissions_co2e", "co2_per_km"]:
                if col in df_active.columns:
                    df_active[col] = pd.to_numeric(df_active[col], errors="coerce")

            # Sauvegarder (tous les trajets)
            all_path = os.path.join(self.data_dir, "night_trains_all.csv")
            df.to_csv(all_path, index=False, encoding="utf-8")

            # Sauvegarder (actifs uniquement)
            active_path = os.path.join(self.data_dir, "night_trains_active.csv")
            df_active.to_csv(active_path, index=False, encoding="utf-8")

            print(f"\n✅ {len(df)} trains extraits ({len(df_active)} actifs)")
            print(f"   Sauvegarde: {all_path}")
            print(f"   Sauvegarde: {active_path}")

            # Statistiques rapides
            if "countries" in df_active.columns:
                pays = set()
                for c in df_active["countries"].dropna():
                    pays.update(c.split(","))
                print(f"\n   Pays couverts: {', '.join(sorted(pays))}")

            if "agency_id" in df_active.columns:
                operateurs = df_active["agency_id"].value_counts().head(8)
                print("\n   Top operateurs:")
                for op, count in operateurs.items():
                    print(f"     {op}: {count} trajets")

            return df_active

        except requests.RequestException as e:
            print(f"❌ Erreur reseau: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return None

    def create_summary_report(self, df_active):
        """
        Cree un rapport de synthese markdown.
        """
        report_path = "docs/opendata_extraction_report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Rapport d'Extraction - Open Night Train Database\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Source\n\n")
            f.write("- **Organisme**: Back-on-Track (association europeenne pro train de nuit)\n")
            f.write(f"- **URL**: {SHEET_URL}\n")
            f.write("- **Licence**: Open Data\n\n")
            f.write("## Statistiques\n\n")

            if df_active is not None:
                f.write(f"- Trains actifs: **{len(df_active)}**\n")
                if "distance" in df_active.columns:
                    f.write(f"- Distance moyenne: **{df_active['distance'].mean():.0f} km**\n")
                if "duration" in df_active.columns:
                    f.write(f"- Duree moyenne: **{df_active['duration'].mean():.1f} h**\n")
                if "emissions_co2e" in df_active.columns:
                    f.write(f"- CO2 moyen par trajet: **{df_active['emissions_co2e'].mean():.1f} kg**\n")

            f.write("\n## Colonnes disponibles\n\n")
            f.write("| Colonne | Description |\n|---------|-------------|\n")
            f.write("| trip_origin | Gare de depart |\n")
            f.write("| trip_headsign | Gare d'arrivee |\n")
            f.write("| agency_id | Operateur (OBB, SNCF, DB...) |\n")
            f.write("| countries | Pays traverses |\n")
            f.write("| distance | Distance en km |\n")
            f.write("| duration | Duree du trajet |\n")
            f.write("| emissions_co2e | Emissions CO2 en kg |\n")
            f.write("| classes | Types de places (seat, couchette, sleeper) |\n")

        print(f"\n📝 Rapport sauvegarde: {report_path}")


def main():
    print("=" * 70)
    print("EXTRACTEUR OPENDATA - PROJET OBRAIL EUROPE")
    print("Source: Open Night Train Database (Back-on-Track)")
    print("=" * 70)

    extractor = OpenNightTrainExtractor()

    df_active = extractor.extract_back_on_track()
    extractor.create_summary_report(df_active)

    print("\n" + "=" * 70)
    print("✅ EXTRACTION TERMINEE")
    print("=" * 70)
    if df_active is not None:
        print(f"\nResultat: {len(df_active)} trains de nuit actifs en Europe")
        print("Fichiers: data/raw/opendata/night_trains_active.csv")
        print("          data/raw/opendata/night_trains_all.csv")


if __name__ == "__main__":
    main()
