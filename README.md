# Precinct Map Generator

## Design Document

### 1. Overview
The goal of this project is to generate an interactive, visually appealing map of geographic regions (e.g., precincts within a legislative district) directly to a standalone HTML file. Users provide raw geographic boundary data, values tied to each region, and a detailed configuration file. The core application outputs an embedded mapping experience containing data exploration capabilities for straightforward display on a website or local viewing.

### 2. Inputs

Users of the project will provide the following inputs:

**2.1. Geographic Boundaries Data**
Files describing the geographic boundaries of regions within a specific area (e.g., all precincts within a county). The tool supports handling multiple standard formats, primarily observed in municipal data (like King County election precincts):
- **GeoJSON (`.geojson`)**
  - *Pros:* Human-readable, native JSON mapping structure making it extremely easy to work with in web mapping libraries (like Leaflet).
  - *Cons:* Files can be very large (e.g., 40MB+ for a county) and consequently slower to load or parse in big chunks.
- **Shapefiles (`.shp` and associated `.dbf`, `.shx`, `.prj`)**
  - *Pros:* The canonical GIS standard. Heavily optimized and efficient for complex spatial geometries. 
  - *Cons:* Requires a collection of multiple files to function properly. Not natively read by web browsers, requiring processing (which our script will handle).
- **KMZ / KML (`.kmz` / `.kml`)**
  - *Pros:* Compressed (KMZ) format means very small file sizes; native to Google Earth.
  - *Cons:* XML-based parsing can be slightly more opaque, and visual stylings native to Google Earth don't always translate cleanly to custom data viz maps.

**2.2. Region Data (CSV)**
A CSV file containing a specific data value for each region. 
- Values can be numerical (e.g., voter turnout percentage, or percentage of votes for an endorsed candidate).
- Values can be categorical/enums (e.g., "Yes", "No", "Maybe").

**2.3. Configuration File (YAML)**
The project uses **YAML** for its configuration file. Using YAML ensures the file is highly human-readable, enables comments, and comfortably handles complex nested configurations. 

The configuration file tells the script how to stitch everything together. Crucially, it will define:
1. **Subarea Filter**: A property filter to define the subarea. Instead of mapping a whole county, we can isolate to an area like Legislative District 48 by supplying a key-value matching rule. 
2. **Data Joining Keys**: Instructions on how to link the geographic boundaries to the CSV. The config will define both a `geo_join_key` (the property name in the geo-file, e.g., "PRECNAME") and a `csv_join_key` (the column name in the CSV, e.g., "precinct").
3. **Display Configuration**: 
   - Descriptors for the data (tooltips and titles).
   - The data type (numeric vs. enum).
   - The scale of numbers (for numeric distributions).
   - Specific color mappings to associate enums/categories with hex colors.

### 3. Core Application Workflow

The foundation of the project will be a Python script. Users will execute this script via the command line, providing pointers to the data files and the `.yaml` config.

**The script processing steps:**
1. **Load Data**: Ingest the geospatial boundaries utilizing Python parsing libraries (e.g., `geopandas`), standardizing whichever format the user has provided into a uniform dataframe.
2. **Filter Subarea**: Apply the property filter defined in the YAML config to significantly reduce the data down to precisely the subarea of interest.
3. **Perform Data Join**: Merge the geographic dataframe with the CSV values by matching the defined join keys.
4. **Render Map**: Use a Python-to-Leaflet wrapper (like `folium`) to build the choropleth logic based on the user's color ranges and scales.
5. **Compile HTML**: Inject the final web map into a standalone file. 

### 4. Output Constraints & Map Features

The application will output a single, HTML file with embedded CSS and Javascript.

**Features of the Map:**
- **Interactive Tooltips:** When a user hovers over a region (e.g. precinct), an interactive tooltip will display its exact label, its joined data value, and any descriptive text, making visual data drill-downs effortless.
- **Cost-Free Mapping Stack:** To avoid API keys or service payments, the tool will leverage completely free Open-Source dependencies. We will utilize **LeafletJS** loaded via a public CDN, alongside **OpenStreetMap (OSM)** base tiles. This provides high-quality foundational mapping (streets, topologies) natively, without incurring hosted mapping service costs.
- **Dynamic Choropleth Layers:** Beautifully shaded polygons representing the specific region criteria layered over the OSM tiles.
