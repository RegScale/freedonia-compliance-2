# ABOUT

Reference implementation of a component generation pipeline.

Content is maintained in OpenControl YAML files. 

The pipeline converts these files into OSCAL JSON files and uploads the components to GovReady-Q.

## Install

Create a virtual environment and activate.

```
python3 -m venv venv
source venv/bin/activate
```

Update pip and install Python packages.

```
python -m pip install --upgrade pip
python -m pip install rtyaml
python -m pip install natsort
python -m pip install requests
python -m pip install structlog
```

Create a `settings.py` file with following content. Replace `example.com` with your GovReady-Q deployment domain.

```
# settings
INPUTDIR = "/path/to/opencontrol/components/start/dir"
OUTPUTDIR = "/path/to/save/generated/oscal/files"
# GovReady API URL
# API_URL = "https://example.com/api/v2/elements/createOSCAL/"
# API_KEY = 'your_api_key_here'

SERVICES_FILE = "services.txt"
OC_SKELETON_FILE = "oc_skeleton.yaml"
```

## Pipeline usage

### Stage 1 - Create default OpenControl components (files)

```
python3 make_opencontrol.py
```

### Stage 2 - Each service teams maintains their OpenControl content

Each service team maintains their OpenControl files in the `opencontrol` directory inside of respective repositories.

## Stage 3 - Generate OSCAL components from OpenControl components

```
python3 make_oscal.py  
```

### Stage 4 - Deploy/upload OSCAL components to GovReady-Q instance

```
python3 upload_oscal.py  
```

## TO DO

- [ ] Add in support for tags
- [ ] Improve dates of file generation


## Optional - Jupyter Notebook

The initial Jupyter Notebook can be found in the `notebook` folder.

To use Jupyter Notebook also install `notebook`.

```
pip install notebook
```

To launch Jupyter Notebook:

```
cd notebooks
jupyter notebook
```
