# az_ozone
Continuation of my thesis work for surface ozone modeling. Expanding to allow for automated ML processing of raster data.

                ┌────────────────────────────┐
                │        Data Sources        │
                │                            │
                │  EPA AQS API               │
                │  NOAA Weather API          │
                │  NASA Satellite Data       │
                │  Wildfire Data (NIFC)      │
                └──────────────┬─────────────┘
                               │
                               ▼
                ┌────────────────────────────┐
                │     Data Ingestion Layer   │
                │                            │
                │  Python ETL scripts        │
                │  Cron jobs / schedulers    │
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
surface-ozone-intelligence-platform
├── docs
│   ├── architecture.md
│   ├── api_documentation.md
│   ├── modeling_methods.md
│   └── deployment_guide.md
│
├── frontend
│   ├── public
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── src
│   │   ├── App.js
│   │   ├── index.js
│   │   │
│   │   ├── pages
│   │   │   ├── Dashboard.jsx
│   │   │   ├── ModelingPage.jsx
│   │   │   └── ResultsPage.jsx
│   │   │
│   │   ├── components
│   │   │   ├── MapViewer.jsx
│   │   │   ├── AOIUploader.jsx
│   │   │   ├── PollutantSelector.jsx
│   │   │   ├── PredictorSelector.jsx
│   │   │   ├── ModelSelector.jsx
│   │   │   ├── TimeSeriesChart.jsx
│   │   │   ├── RasterSlider.jsx
│   │   │   └── ModelExplanation.jsx
│   │   │
│   │   ├── services
│   │   │   ├── api.js
│   │   │   └── jobService.js
│   │   │
│   │   ├── styles
│   │   │   └── main.css
│   │   │
│   │   └── utils
│   │       ├── mapUtils.js
│   │       └── chartUtils.js
│   │
│   └── package.json
│
├── backend
│   ├── server.js
│   │
│   ├── routes
│   │   ├── uploadRoutes.js
│   │   ├── modelingRoutes.js
│   │   └── resultsRoutes.js
│   │
│   ├── controllers
│   │   ├── uploadController.js
│   │   ├── modelingController.js
│   │   └── resultsController.js
│   │
│   ├── services
│   │   ├── jobQueueService.js
│   │   └── pythonService.js
│   │
│   ├── middleware
│   │   ├── authMiddleware.js
│   │   └── validationMiddleware.js
│   │
│   └── config
│       ├── database.js
│       └── redis.js
│
├── ai_engine
│   ├── main.py
│   ├── api.py
│   │
│   ├── pipelines
│   │   ├── modeling_pipeline.py
│   │   └── prediction_pipeline.py
│   │
│   ├── data_ingestion
│   │   ├── epa_api_aqnow.py
│   │   ├── monitor_processing.py
│   │   └── station_filtering.py
│   │
│   ├── raster_processing
│   │   ├── gee_data.py
│   │   ├── raster_extraction.py
│   │   └── raster_preprocessing.py
│   │
│   ├── modeling
│   │   ├── models.py
│   │   ├── model_training.py
│   │   ├── model_prediction.py
│   │   └── model_evaluation.py
│   │
│   ├── surface_generation
│   │   ├── surface_plot.py
│   │   ├── grid_generation.py
│   │   └── raster_export.py
│   │
│   ├── recommendations
│   │   ├── model_recommender.py
│   │   └── predictor_recommender.py
│   │
│   ├── validation
│   │   ├── input_validation.py
│   │   └── spatial_validation.py
│   │
│   └── config
│       ├── model_config.py
│       └── predictor_catalog.py
│
├── workers
│   ├── worker.py
│   ├── tasks
│   │   ├── run_model_task.py
│   │   ├── data_download_task.py
│   │   └── raster_prediction_task.py
│   │
│   └── queue_config.py
│
├── geospatial_platform
│   ├── database
│   │   ├── postgis_schema.sql
│   │   └── migrations
│   │
│   ├── raster_tiles
│   │   ├── cog_generation.py
│   │   └── tile_server_config.py
│   │
│   └── vector_services
│       ├── monitor_service.py
│       └── aoi_service.py
│
├── storage
│   ├── uploads
│   │   └── shapefiles
│   │
│   ├── monitor_data
│   │   └── epa_downloads
│   │
│   ├── predictors
│   │   └── gee_exports
│   │
│   ├── model_outputs
│   │   ├── predictions
│   │   ├── surfaces
│   │   └── metrics
│   │
│   └── logs
│       ├── api_logs
│       └── worker_logs
│
├── infrastructure
│   ├── docker
│   │   ├── Dockerfile.backend
│   │   ├── Dockerfile.ai
│   │   └── Dockerfile.frontend
│   │
│   ├── kubernetes
│   │   ├── frontend-deployment.yaml
│   │   ├── backend-deployment.yaml
│   │   ├── ai-engine-deployment.yaml
│   │   └── redis-deployment.yaml
│   │
│   └── terraform
│       ├── aws_infrastructure.tf
│       └── storage_setup.tf
│
└── tests
    ├── api_tests
    ├── model_tests
    └── integration_tests