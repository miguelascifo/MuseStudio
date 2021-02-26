# MuseStudio

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