# :trolleybus: Rome in Transit (WIP)

![img](https://raw.githubusercontent.com/ivandorte/Rome-in-transit/main/assets/dashboard.png)

[![License: CC BY-SA 4.0](https://img.shields.io/badge/License-CC%20BY--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Description

This dashboard displays the real-time position of any bus, tram, or train (ATAC and Roma TPL operators) within the Metropolitan City of Rome Capital.

## Deployed on
- HF: https://huggingface.co/spaces/ivn888/Rome-in-transit
- GitHub Pages: -

## Data 

- Public transport data from [Roma Mobilità - Vehicle Positions](https://romamobilita.it/it/tecnologie);

- Administrative boundaries from [ISTAT (2022)](https://www.istat.it/it/archivio/222527);

## What I've done here

- Loaded custom Python code from GitHub;

https://github.com/ivandorte/Rome-in-transit/blob/890b54f0834995e6c024f5dfdc20993c9cde8e2d/docs/gtfs-rt-rome/app.js#L40-L53

- Loaded [protobuf](https://pypi.org/project/protobuf/) and [gtfs-realtime-bindings](https://pypi.org/project/gtfs-realtime-bindings/) wheels (not available on pyodide) from a [CDN URL](https://cdn.jsdelivr.net);

- Used [corsproxy.io](https://corsproxy.io/) to bypass CORS errors on HTTP requests;

- Used XMLHttpRequest (js) to make HTTP requests of binary data;

https://github.com/ivandorte/Rome-in-transit/blob/890b54f0834995e6c024f5dfdc20993c9cde8e2d/modules_pyodide/rome_gtfs_rt.py#L58-L76

## References

- https://holoviz.org/

- https://hvplot.holoviz.org

- https://pyodide.org/en/stable/

- https://pyodide.org/en/stable/usage/loading-custom-python-code.html

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
