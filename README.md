# MuseStudio

[![DOI](https://zenodo.org/badge/334904649.svg)](https://zenodo.org/badge/latestdoi/334904649) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/miguelascifo/MuseStudio.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/miguelascifo/MuseStudio/context:python)
![PyPI](https://img.shields.io/pypi/v/musestudio)
![PyPI - License](https://img.shields.io/pypi/l/musestudio)

MuseStudio allows managing data associated to a single or multiple sessions with Muse devices. Additionally, the library allows viewing brain activity data in real time from individuals wearing Muse.

Features:
* Import raw data from recordings (in XDF file format)
* Convert brain activity data to MNE and Pandas compatible formats
* Import and export following the BIDS standard
* View real time data in web browser

Templates are necessary for BIDS import and export.

This library is compatible with all Muse hardware versions.

## Templates
```python
setup = [
    {
        'subject': None,
        'session': None,
        'task': None,
        'acquisition': None,
        'run': None,
        'processing': None,
        'recording': None,
        'space': None,
        'split': None,
        'root': None,
        'suffix': None,
        'extension': None
    }
]

participants = [
    {
        'subject': None,
        'age': None,
        'sex': None,
        'hand': None,
        'root': None
    }
]
```
