# az_ozone
Continuation of my thesis work for surface ozone modeling. Expanding to allow for automated ML processing of raster data.
The Goal:


                ┌────────────────────────────┐
                │        Data Sources        │
                │                            │
                │  EPA AQS API               │
                │  Google Earth Engine       │
                └──────────────┬─────────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │     Data Ingestion Layer   │
                │                            │
                │  Python scripts            │
                │  Data cleaning             │
                └──────────────┬─────────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │  Data Processing / Models  │
                │                            │
                │  Ozone prediction ML       │
                │  Spatial interpolation     │
                │  Feature engineering       │
                └──────────────┬─────────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │        Data Storage        │
                │                            │
                │  PostgreSQL + PostGIS      │
                │  GeoJSON layers            │
                │  Raster data               │
                └──────────────┬─────────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │         API Layer          │
                │                            │
                │  Node.js + Express         │
                │  REST API endpoints        │
                │  GeoJSON services          │
                └──────────────┬─────────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │      GIS Service Layer     │
                │                            │
                │  Mapbox / Leaflet          │
                │  Tile generation           │
                │  Spatial queries           │
                └──────────────┬─────────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │        Frontend UI         │
                │                            │
                │  React dashboard           │
                │  Vue visualization         │
                │  Interactive GIS maps      │
                └────────────────────────────┘
