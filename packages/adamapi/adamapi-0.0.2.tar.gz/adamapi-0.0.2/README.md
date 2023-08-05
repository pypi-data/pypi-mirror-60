Adamapi version 0.0.2

# Installation

```bash
sudo apt-get install python3-venv python3-gdal gdal-bin
VENVNAME="adamapi"
python3 -m venv "${VENVNAME}"
source "${VENVNAME}/bin/activate";
python3 -m pip install --upgrade pip
pip install adamapi
deactivate
ln -s "/usr/lib/python3/dist-packages/osgeo" "${VENVNAME}/lib/python3.6/site-packages/osgeo"
source "${VENVNAME}/bin/activate"
```
