# pipeline.py
# Orchestre la pipeline ETL complète : Extract → Transform → Load
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from extract.extract_gtfs        import run_extract_gtfs
from extract.extract_opendata    import OpenNightTrainExtractor
from extract.extract_scraping    import TrainScraper
from transform.transform_gtfs        import transform_operateurs, transform_gares, transform_dessertes
from transform.transform_night_trains import transform as transform_night_trains
from load.load_to_postgresql     import run_load_pipeline


def run_pipeline(skip_extract=False):
    print("=" * 60)
    print("  PIPELINE ETL — ObRail Europe")
    print("  Extract → Transform → Load → PostgreSQL")
    print("=" * 60)

    # ── EXTRACT ──
    if not skip_extract:
        print("\n[1/3] EXTRACT — GTFS")
        resultats = run_extract_gtfs()
        if not all(resultats.values()):
            print("❌ Extract GTFS incomplet — abandon.")
            return False

        print("\n[1/3] EXTRACT — Open Data")
        extractor = OpenNightTrainExtractor()
        extractor.extract_back_on_track()

        print("\n[1/3] EXTRACT — Web Scraping")
        scraper = TrainScraper()
        scraper.scrape_wikipedia_rail_networks()
        scraper.scrape_wikipedia_operators()
        scraper.scrape_back_on_track_table()
    else:
        print("\n[1/3] EXTRACT — ignoré (--skip-extract)")

    # ── TRANSFORM ──
    print("\n[2/3] TRANSFORM")
    operateurs = transform_operateurs()
    gares      = transform_gares()
    dessertes  = transform_dessertes(operateurs, gares)

    nt_ops, nt_gares, nt_dessertes = transform_night_trains()

    print(f"\n  Résumé transform :")
    print(f"    Opérateurs GTFS      : {len(operateurs)}")
    print(f"    Opérateurs nuit      : {len(nt_ops)}")
    print(f"    Gares GTFS           : {len(gares)}")
    print(f"    Gares nuit           : {len(nt_gares)}")
    print(f"    Dessertes GTFS       : {len(dessertes)}")
    print(f"    Dessertes nuit       : {len(nt_dessertes)}")

    # ── LOAD ──
    print("\n[3/3] LOAD")
    ok = run_load_pipeline()
    if not ok:
        print("❌ Load échoué.")
        return False

    print("\n" + "=" * 60)
    print("  ✅ PIPELINE TERMINÉE AVEC SUCCÈS !")
    print("=" * 60)
    return True


if __name__ == "__main__":
    skip = "--skip-extract" in sys.argv
    run_pipeline(skip_extract=skip)
