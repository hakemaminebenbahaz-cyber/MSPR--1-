# extract_gtfs.py
# Analyse des fichiers GTFS deja extraits

import pandas as pd
import os
import json

class GTFSLoader:
    def __init__(self, data_dir="data/raw"):
        self.data_dir = data_dir
        self.data = {}
        
    def load_gtfs_files(self):
        """
        Charge tous les fichiers GTFS du dossier data/raw
        """
        print(f"Chargement des fichiers GTFS depuis: {self.data_dir}")
        
        if not os.path.exists(self.data_dir):
            print(f"ERREUR: Dossier {self.data_dir} non trouve")
            return False
        
        # Liste des fichiers GTFS standard
        gtfs_files = {
            'stops': 'stops.txt',
            'routes': 'routes.txt',
            'trips': 'trips.txt',
            'stop_times': 'stop_times.txt',
            'agency': 'agency.txt',
            'calendar_dates': 'calendar_dates.txt'
        }
        
        loaded_count = 0
        for data_name, file_name in gtfs_files.items():
            file_path = os.path.join(self.data_dir, file_name)
            
            if os.path.exists(file_path):
                try:
                    # Charge le fichier CSV
                    self.data[data_name] = pd.read_csv(file_path)
                    loaded_count += 1
                    print(f"  ✅ {file_name}: {len(self.data[data_name])} lignes")
                    
                except Exception as e:
                    print(f"  ❌ {file_name}: Erreur de chargement - {e}")
            else:
                print(f"  ⚠️  {file_name}: Non trouve")
        
        print(f"\nTotal: {loaded_count} fichiers GTFS charges avec succes")
        return loaded_count > 0
    
    def analyze_gtfs(self):
        """
        Analyse complete des donnees GTFS chargees
        """
        print("\n" + "="*70)
        print("ANALYSE COMPLETE DES DONNEES GTFS")
        print("="*70)
        
        analysis = {}
        
        # 1. Analyse des GARES
        if 'stops' in self.data:
            stops_df = self.data['stops']
            print("\n🔍 1. GARES (stops.txt):")
            print(f"   📊 Total: {len(stops_df)} gares")
            print(f"   📋 Colonnes: {', '.join(stops_df.columns)}")
            
            # Statistiques importantes
            if 'stop_name' in stops_df.columns:
                print(f"   🏷️  Exemples de gares:")
                unique_stations = stops_df['stop_name'].unique()
                for station in unique_stations[:5]:
                    print(f"      - {station}")
            
            analysis['stops'] = {
                'count': len(stops_df),
                'columns': list(stops_df.columns)
            }
        
        # 2. Analyse des LIGNES
        if 'routes' in self.data:
            routes_df = self.data['routes']
            print("\n🔍 2. LIGNES (routes.txt):")
            print(f"   📊 Total: {len(routes_df)} lignes")
            print(f"   📋 Colonnes: {', '.join(routes_df.columns)}")
            
            if 'route_type' in routes_df.columns:
                route_types = routes_df['route_type'].unique()
                print(f"   🚆 Types de transport:")
                for rt in route_types:
                    count = len(routes_df[routes_df['route_type'] == rt])
                    type_name = self.get_route_type_name(rt)
                    print(f"      - {type_name} ({rt}): {count} lignes")
            
            analysis['routes'] = {
                'count': len(routes_df),
                'route_types': routes_df['route_type'].unique().tolist() if 'route_type' in routes_df.columns else []
            }
        
        # 3. Analyse des TRAJETS
        if 'trips' in self.data:
            trips_df = self.data['trips']
            print("\n🔍 3. TRAJETS (trips.txt):")
            print(f"   📊 Total: {len(trips_df)} trajets")
            print(f"   📋 Colonnes: {', '.join(trips_df.columns)}")
            
            analysis['trips'] = {
                'count': len(trips_df)
            }
        
        # 4. Analyse des HORAIRES
        if 'stop_times' in self.data:
            stop_times_df = self.data['stop_times']
            print("\n🔍 4. HORAIRES (stop_times.txt):")
            print(f"   📊 Total: {len(stop_times_df)} entrees horaires")
            print(f"   ⏰ Premier horaire: {stop_times_df['arrival_time'].iloc[0] if 'arrival_time' in stop_times_df.columns else 'N/A'}")
            
            analysis['stop_times'] = {
                'count': len(stop_times_df)
            }
        
        # 5. Analyse des OPERATEURS
        if 'agency' in self.data:
            agency_df = self.data['agency']
            print("\n🔍 5. OPERATEURS (agency.txt):")
            print(f"   📊 Total: {len(agency_df)} operateurs")
            if 'agency_name' in agency_df.columns:
                print(f"   🏢 Operateurs:")
                for _, agency in agency_df.iterrows():
                    print(f"      - {agency['agency_name']}")
        
        print("\n" + "="*70)
        print("SYNTHESE POUR LE PROJET OBRAIL:")
        print("="*70)
        
        # Recherche d'indicateurs pour trains de jour/nuit
        self.find_day_night_indicators()
        
        return analysis
    
    def get_route_type_name(self, route_type_code):
        """
        Convertit le code route_type en nom comprehensible
        """
        route_types = {
            0: "Tramway",
            1: "Metro",
            2: "Train (Rail)",  # C'est ce qu'on cherche!
            3: "Bus",
            4: "Ferry",
            7: "Funiculaire"
        }
        return route_types.get(route_type_code, f"Type {route_type_code}")
    
    def find_day_night_indicators(self):
        """
        Cherche des indicateurs pour distinguer trains jour/nuit
        """
        print("\n🔎 RECHERCHE D'INDICATEURS TRAINS JOUR/NUIT:")
        
        # Methode 1: Par le nom des lignes
        if 'routes' in self.data:
            routes_df = self.data['routes']
            if 'route_long_name' in routes_df.columns:
                routes_df['route_lower'] = routes_df['route_long_name'].str.lower()
                
                # Mots-cles pour trains de nuit
                night_keywords = ['night', 'nacht', 'nuit', 'nocturne', 'sleeper']
                night_lines = routes_df[routes_df['route_lower'].str.contains('|'.join(night_keywords), na=False)]
                
                if len(night_lines) > 0:
                    print("   ✅ Trains de nuit detectes par nom de ligne:")
                    for _, line in night_lines.iterrows():
                        print(f"      - {line.get('route_long_name')}")
                else:
                    print("   ℹ️  Aucun train de nuit detecte par nom de ligne")
        
        # Methode 2: Par les horaires extremes
        if 'stop_times' in self.data:
            stop_times_df = self.data['stop_times']
            if 'arrival_time' in stop_times_df.columns:
                # Extrait l'heure
                times = stop_times_df['arrival_time'].str.extract(r'(\d+):')
                if not times.empty:
                    times_numeric = pd.to_numeric(times[0], errors='coerce')
                    night_times = stop_times_df[times_numeric >= 22]  # Apres 22h
                    early_times = stop_times_df[times_numeric <= 4]   # Avant 4h
                    
                    if len(night_times) > 0 or len(early_times) > 0:
                        print(f"   ✅ Horaires nocturnes detectes:")
                        print(f"      - Apres 22h: {len(night_times)} horaires")
                        print(f"      - Avant 4h: {len(early_times)} horaires")
    
    def save_analysis_report(self, output_path="docs/gtfs_analysis_report.md"):
        """
        Sauvegarde un rapport d'analyse detaille
        """
        print(f"\n💾 Creation du rapport d'analyse...")
        
        analysis = self.analyze_gtfs()
        
        report = "# Rapport d'Analyse GTFS - Projet ObRail Europe\n\n"
        report += "## Resume des Donnees\n\n"
        
        if 'stops' in analysis:
            report += f"- **Gares**: {analysis['stops']['count']} stations\n"
        
        if 'routes' in analysis:
            report += f"- **Lignes**: {analysis['routes']['count']} lignes\n"
            if analysis['routes']['route_types']:
                report += f"- **Types de transport**: {', '.join(map(str, analysis['routes']['route_types']))}\n"
        
        report += "\n## Prochaines Etapes pour le Projet\n"
        report += "1. Nettoyer les donnees de gares (clean_gares.py)\n"
        report += "2. Identifier les trains de jour vs trains de nuit\n"
        report += "3. Harmoniser les formats de donnees\n"
        report += "4. Preparer pour l'analyse comparative\n"
        
        # Sauvegarde le rapport
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Rapport sauvegarde dans: {output_path}")

# Fonction principale
def main():
    print("="*70)
    print("🔧 ANALYSEUR GTFS - PROJET OBRAIL EUROPE")
    print("="*70)
    
    # Initialise le chargeur GTFS
    loader = GTFSLoader("data/raw")
    
    # Charge les fichiers
    if loader.load_gtfs_files():
        # Analyse les donnees
        loader.analyze_gtfs()
        
        # Sauvegarde un rapport
        loader.save_analysis_report()
        
        print("\n" + "="*70)
        print("✅ ANALYSE TERMINEE AVEC SUCCES!")
        print("="*70)
        print("\nProchaines actions pour ton role Data Engineer:")
        print("1. Lancer le nettoyage des gares: python etl/transform/clean_gares.py")
        print("2. Preparer la normalisation des horaires")
        print("3. Documenter le processus ETL")
    else:
        print("\n❌ Echec du chargement des fichiers GTFS")

if __name__ == "__main__":
    main()