# :trolleybus: Rome in Transit (GTFS-RT)

![img](https://raw.githubusercontent.com/ivandorte/Rome-in-transit/main/assets/dashboard.png)

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Description

This dashboard displays the near real-time position of any bus, tram, or train (ATAC and Roma TPL operators) within the Metropolitan City of Rome Capital. The stream layers automatically updates every 10 seconds through a **periodic callback** with new data retrieved from the GTFS-RealTime ([Overview](https://developers.google.com/transit/gtfs-realtime)) feed provided and mantained by Roma Mobilità ([website](https://romamobilita.it/))

## Components

Two stream layers (maps):

1. The "Vehicle status" map shows, as the name implies, the current status of the vehicle:
   - In transit `#0077BB`
   - Stopped `#EE7733`

2. The "Delays map" displays whether a vehicle is on time (ahead + on time) or behind schedule (late):
   - On time `#009988`
   - Late `#CC3311`

N.B.: In the hover tooltip the value of the delay field (in minutes) will be zero if the vehicle is on time (A), negative if ahead of schedule (B) or positive if late (C).

![img](https://raw.githubusercontent.com/ivandorte/Rome-in-transit/main/assets/delay.png)

Five number indicators showing:

- The number of currently active vehicles (fleet) divided between in transit or stopped;

- The number of vehicles on time or behind schedule;

## Deployed on

HF: https://huggingface.co/spaces/ivn888/Rome-in-transit

GitHub Pages: https://ivandorte.github.io/Rome-in-transit/gtfs-rt/app.html

Known problems:

- If you view a blank page in HF restart the Space;

- The peridic callback may suddenly stop working (I don't know why) and the data will not be updated, simply refresh the application page;

## Data 

- Public transport data from [Roma Mobilità - Vehicle Positions](https://romamobilita.it/it/tecnologie);

- Administrative boundaries from [ISTAT (2022)](https://www.istat.it/it/archivio/222527);

## Deployment on GitHub pages

1. Loaded my custom Python modules from GitHub:

https://github.com/ivandorte/Rome-in-transit/blob/890b54f0834995e6c024f5dfdc20993c9cde8e2d/docs/gtfs-rt-rome/app.js#L40-L53

2. Loaded protobuf and gtfs-realtime-bindings wheels from a [CDN URL](https://cdn.jsdelivr.net):

   - protobuf is available on pypi: https://pypi.org/project/protobuf/#files

   - gtfs-realtime-bindings (https://pypi.org/project/gtfs-realtime-bindings/#files) was compiled via: `python setup.py bdist_wheel`

3. How I partially solved the CORS problem?

   - Used [corsproxy.io](https://corsproxy.io/) to bypass CORS errors on HTTP requests;

   - Used XMLHttpRequest (js) to make HTTP requests of binary data;

https://github.com/ivandorte/Rome-in-transit/blob/890b54f0834995e6c024f5dfdc20993c9cde8e2d/modules_pyodide/rome_gtfs_rt.py#L58-L76

## Deployment on HF

Just read this [Medium article](https://towardsdatascience.com/how-to-deploy-a-panel-app-to-hugging-face-using-docker-6189e3789718) written by Sophia Yang, Ph.D.

## References

- https://developers.google.com/transit/gtfs-realtime

- https://holoviz.org/

- https://hvplot.holoviz.org

- https://pyodide.org/en/stable/

- https://pyodide.org/en/stable/usage/loading-custom-python-code.html

- https://towardsdatascience.com/how-to-deploy-a-panel-app-to-hugging-face-using-docker-6189e3789718

- https://panel.holoviz.org/how_to/wasm/convert.html

- https://corsproxy.io/

- https://bartbroere.eu/2022/04/25/pyodide-requests-binary-works-update/

- https://examples.pyviz.org/index.html

- https://awesome-panel.org/

- https://awesome-panel.org/sharing_gallery

- https://awesome-panel.org/sharing?app=MarcSkovMadsen%2Fdiscourse-4825-streaming-data

- https://github.com/Ileriayo/markdown-badges

- Dashboard logo from [Material Symbols - Google](https://fonts.google.com/icons)

### Authors

- Ivan D'Ortenzio

[![Twitter](https://img.shields.io/badge/Twitter-%231DA1F2.svg?style=for-the-badge&logo=Twitter&logoColor=white)](https://twitter.com/ivanziogeo)

[![LinkedIn](https://img.shields.io/badge/linkedin-%230077B5.svg?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/ivan-d-ortenzio/)
