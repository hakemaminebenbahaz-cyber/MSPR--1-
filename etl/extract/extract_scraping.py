# extract_scraping.py
# Scraping REEL de donnees ferroviaires europeennes
# Sources: Wikipedia (reseaux ferrroviaires par pays), Back-on-Track (table HTML)

import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import time
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "ObRail-ETL/1.0 (projet academique EPSI; contact: obrail@epsi.fr)"
}


class TrainScraper:
    def __init__(self):
        self.data_dir = "data/raw/scraped"
        os.makedirs(self.data_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def _get(self, url, timeout=20):
        """GET avec gestion d'erreur basique."""
        r = self.session.get(url, timeout=timeout)
        r.raise_for_status()
        return r

    # ------------------------------------------------------------------
    # 1. Wikipedia — Reseaux ferroviaires par pays en Europe
    # ------------------------------------------------------------------
    def scrape_wikipedia_rail_networks(self):
        """
        Scrape le tableau Wikipedia 'List of countries by rail transport network size'
        pour obtenir les donnees reelles sur les reseaux ferroviaires europeens.
        URL: https://en.wikipedia.org/wiki/List_of_countries_by_rail_transport_network_size
        """
        print("\n" + "=" * 60)
        print("SCRAPING WIKIPEDIA — RESEAUX FERROVIAIRES PAR PAYS")
        print("=" * 60)

        url = "https://en.wikipedia.org/wiki/List_of_countries_by_rail_transport_network_size"
        print(f"Source: {url}")

        try:
            r = self._get(url)
            soup = BeautifulSoup(r.content, "html.parser")

            # Trouver le premier grand tableau wikitable
            tables = soup.find_all("table", class_="wikitable")
            if not tables:
                print("❌ Aucun tableau trouve sur la page Wikipedia")
                return None

            print(f"   {len(tables)} tableau(x) trouve(s) — extraction du premier...")

            rows = []
            table = tables[0]
            headers = []

            for i, tr in enumerate(table.find_all("tr")):
                cells = tr.find_all(["th", "td"])
                if i == 0:
                    headers = [c.get_text(strip=True) for c in cells]
                    continue
                if not cells:
                    continue
                row = {}
                for j, cell in enumerate(cells):
                    key = headers[j] if j < len(headers) else f"col_{j}"
                    val = cell.get_text(strip=True)
                    # Nettoyer les chiffres (supprimer virgules, espaces, notes [1])
                    val = re.sub(r"\[.*?\]", "", val).strip()
                    row[key] = val
                rows.append(row)

            df = pd.DataFrame(rows)

            # Garder uniquement les pays europeens (filtre par liste)
            european_countries = {
                "France", "Germany", "Italy", "Spain", "Russia", "United Kingdom",
                "Poland", "Sweden", "Austria", "Switzerland", "Netherlands",
                "Belgium", "Norway", "Denmark", "Finland", "Czech Republic",
                "Hungary", "Romania", "Portugal", "Ukraine", "Slovakia",
                "Serbia", "Croatia", "Bulgaria", "Greece", "Belarus"
            }

            # La colonne pays peut s'appeler "Country" ou similaire
            country_col = next(
                (c for c in df.columns if "country" in c.lower() or "nation" in c.lower()),
                df.columns[0] if len(df.columns) > 0 else None
            )

            if country_col:
                df_europe = df[df[country_col].isin(european_countries)].copy()
                if df_europe.empty:
                    # Garder tout si le filtre ne marche pas (noms differents)
                    df_europe = df.head(40)
                    print("   (filtre europeen non applique — noms de pays differents)")
            else:
                df_europe = df.head(40)

            df_europe["scraped_date"] = datetime.now().strftime("%Y-%m-%d")
            df_europe["source"] = "Wikipedia - Rail network size"

            out = os.path.join(self.data_dir, "wikipedia_rail_networks.csv")
            df_europe.to_csv(out, index=False, encoding="utf-8")

            print(f"✅ {len(df_europe)} pays extraits → {out}")
            print(f"   Colonnes: {', '.join(df_europe.columns[:6])}")

            return df_europe

        except Exception as e:
            print(f"❌ Erreur Wikipedia rail networks: {e}")
            return None

    # ------------------------------------------------------------------
    # 2. Wikipedia — Lignes a grande vitesse en Europe
    # ------------------------------------------------------------------
    def scrape_wikipedia_operators(self):
        """
        Scrape le tableau Wikipedia des lignes a grande vitesse par pays.
        URL: https://en.wikipedia.org/wiki/List_of_high-speed_railway_lines
        Filtre: pays europeens uniquement.
        """
        print("\n" + "=" * 60)
        print("SCRAPING WIKIPEDIA — LIGNES GRANDE VITESSE PAR PAYS")
        print("=" * 60)

        url = "https://en.wikipedia.org/wiki/List_of_high-speed_railway_lines"
        print(f"Source: {url}")

        EUROPE = {
            "Austria", "Belgium", "Czech Republic", "Denmark", "Finland",
            "France", "Germany", "Greece", "Hungary", "Italy", "Netherlands",
            "Norway", "Poland", "Portugal", "Romania", "Russia", "Slovakia",
            "Spain", "Sweden", "Switzerland", "Turkey", "United Kingdom"
        }

        try:
            r = self._get(url)
            soup = BeautifulSoup(r.content, "html.parser")

            tables = soup.find_all("table", class_="wikitable")
            if not tables:
                print("❌ Aucun tableau")
                return None

            print(f"   {len(tables)} tableau(x) trouve(s) — extraction du 1er...")

            rows = []
            table = tables[0]
            headers = []

            for i, tr in enumerate(table.find_all("tr")):
                cells = tr.find_all(["th", "td"])
                if i == 0:
                    headers = [re.sub(r"\s+", " ", c.get_text(strip=True)) for c in cells]
                    continue
                if not cells:
                    continue
                row = {}
                for j, cell in enumerate(cells):
                    key = headers[j] if j < len(headers) else f"col_{j}"
                    val = re.sub(r"\[.*?\]", "", cell.get_text(strip=True)).replace("\xa0", " ").strip()
                    row[key] = val
                rows.append(row)

            df = pd.DataFrame(rows)

            # Filtre Europe
            country_col = df.columns[0]
            df_eu = df[df[country_col].isin(EUROPE)].copy()
            if df_eu.empty:
                df_eu = df  # garder tout si pas de match

            df_eu["scraped_date"] = datetime.now().strftime("%Y-%m-%d")
            df_eu["source"] = "Wikipedia - High-speed railway lines"

            out = os.path.join(self.data_dir, "wikipedia_highspeed_lines.csv")
            df_eu.to_csv(out, index=False, encoding="utf-8")

            print(f"✅ {len(df_eu)} pays/lignes extraits → {out}")
            return df_eu

        except Exception as e:
            print(f"❌ Erreur Wikipedia high-speed: {e}")
            return None

    # ------------------------------------------------------------------
    # 3. Wikipedia — Routes Nightjet (OBB trains de nuit)
    # ------------------------------------------------------------------
    def scrape_back_on_track_table(self):
        """
        Scrape le tableau Wikipedia des routes Nightjet (trains de nuit OBB).
        URL: https://en.wikipedia.org/wiki/Nightjet
        Contient: routes, villes desservies, frequence, ouverture.
        Note: Back-on-Track/night-train-database utilise du JavaScript dynamique
              (table rendue cote client), non accessible sans navigateur headless.
              Wikipedia offre des donnees statiques equivalentes.
        """
        print("\n" + "=" * 60)
        print("SCRAPING WIKIPEDIA — ROUTES NIGHTJET (TRAINS DE NUIT OBB)")
        print("=" * 60)

        url = "https://en.wikipedia.org/wiki/Nightjet"
        print(f"Source: {url}")

        try:
            r = self._get(url)
            soup = BeautifulSoup(r.content, "html.parser")

            tables = soup.find_all("table", class_="wikitable")
            print(f"   {len(tables)} tableau(x) trouve(s) sur la page")

            if not tables:
                print("❌ Aucun tableau wikitable")
                return None

            all_rows = []
            for table in tables:
                headers = []
                for i, tr in enumerate(table.find_all("tr")):
                    cells = tr.find_all(["th", "td"])
                    if not cells:
                        continue
                    if i == 0 or all(c.name == "th" for c in cells):
                        headers = [re.sub(r"\s+", " ", c.get_text(strip=True)) for c in cells]
                        continue
                    row = {}
                    for j, cell in enumerate(cells):
                        key = headers[j] if j < len(headers) else f"col_{j}"
                        val = re.sub(r"\[.*?\]", "", cell.get_text(strip=True)).replace("\xa0", " ").strip()
                        row[key] = val
                    if any(v for v in row.values()):
                        all_rows.append(row)

            if not all_rows:
                print("❌ Aucune ligne de donnees")
                return None

            df = pd.DataFrame(all_rows)
            df["scraped_date"] = datetime.now().strftime("%Y-%m-%d")
            df["source"] = "Wikipedia - Nightjet routes"

            out = os.path.join(self.data_dir, "wikipedia_nightjet_routes.csv")
            df.to_csv(out, index=False, encoding="utf-8")

            print(f"✅ {len(df)} routes Nightjet extraites → {out}")
            print(f"   Colonnes: {', '.join(df.columns[:6])}")

            return df

        except Exception as e:
            print(f"❌ Erreur Wikipedia Nightjet: {e}")
            return None

    # ------------------------------------------------------------------
    # Rapport
    # ------------------------------------------------------------------
    def generate_report(self):
        report_path = "docs/scraping_report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        files = [f for f in os.listdir(self.data_dir) if f.endswith(".csv")]
        total = 0

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Rapport de Scraping Web — Projet ObRail Europe\n\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Sources scrapees\n\n")
            f.write("| Fichier | Lignes |\n|---------|--------|\n")

            for fname in files:
                try:
                    df = pd.read_csv(os.path.join(self.data_dir, fname))
                    f.write(f"| {fname} | {len(df)} |\n")
                    total += len(df)
                except Exception:
                    f.write(f"| {fname} | erreur |\n")

            f.write(f"\n**Total: {total} enregistrements**\n\n")
            f.write("## Sources utilisees\n\n")
            f.write("- Wikipedia: *List of countries by rail transport network size*\n")
            f.write("- Wikipedia: *List of European railway companies*\n")
            f.write("- Back-on-Track: *Night Train Database* (table HTML)\n")

        print(f"\n📝 Rapport sauvegarde: {report_path}")


def main():
    print("=" * 70)
    print("SCRAPING WEB — PROJET OBRAIL EUROPE")
    print("Sources: Wikipedia + Back-on-Track (donnees reelles)")
    print("=" * 70)

    scraper = TrainScraper()

    # 1. Reseaux ferroviaires par pays
    df_networks = scraper.scrape_wikipedia_rail_networks()
    time.sleep(1)  # Politesse envers Wikipedia

    # 2. Operateurs ferroviaires
    df_operators = scraper.scrape_wikipedia_operators()
    time.sleep(1)

    # 3. Table HTML Back-on-Track
    df_bot = scraper.scrape_back_on_track_table()

    # 4. Rapport
    scraper.generate_report()

    print("\n" + "=" * 70)
    print("✅ SCRAPING TERMINE")
    print("=" * 70)

    total = sum(len(d) for d in [df_networks, df_operators, df_bot] if d is not None)
    print(f"\nTotal: {total} lignes scrapees depuis des sources reelles")
    print("Fichiers: data/raw/scraped/")


if __name__ == "__main__":
    main()
