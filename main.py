import argparse
import sys
from config import Config
from loader import load_geodata, load_csv
from mapper import create_map

def main():
    parser = argparse.ArgumentParser(description="Generate a Precinct Map from Geographic and CSV data")
    parser.add_argument('--geo', required=True, help='Path to geographic boundaries file (.geojson, .shp, .kml)')
    parser.add_argument('--data', required=True, help='Path to region data file (.csv)')
    parser.add_argument('--config', required=True, help='Path to YAML configuration file')
    parser.add_argument('--out', default='-', help='Path to output HTML file. Defaults to standard output `-`')
    
    args = parser.parse_args()
    
    try:
        config = Config.from_yaml(args.config)
        
        gdf = load_geodata(args.geo, config.subarea_filter)
        df = load_csv(args.data)
        
        create_map(gdf, df, config, args.out)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
