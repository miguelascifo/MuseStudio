from csv import DictReader, DictWriter
from mne import io
from mne_bids import BIDSPath, write_raw_bids
from os import remove, path
from platform import system
from tempfile import gettempdir
from warnings import warn

def create_bids_path(setup = None):
    '''Create paths for BIDS.

    Args:
        setup : array
            The setup of each recording. Template available in README.
    Returns:
        Array containing the BIDS paths as MNE-BIDS BIDSPath instances.
    Raises:
        ValueError: if no setup is specified.
    '''
    if setup is None:
        raise(ValueError('Enter BIDS setup parameter array.'))
    
    setup = [setup] if not isinstance(setup, list) else setup

    bids_paths = []

    # Iterate over the recordings setup
    for config in setup:
        root_folder = r'%s' % config['root']
        if system() == 'Windows':
            if root_folder[-1] == '\\':
                root_folder = root_folder + 'dataset_description.json'
            else:
                root_folder = root_folder + '\\dataset_description.json'
        else:
            if root_folder[-1] == '/':
                root_folder = root_folder + 'dataset_description.json'
            else:
                root_folder = root_folder + '/dataset_description.json'
        
        if not path.exists(root_folder):
            warn('This is the first time you create a dataset in this folder. Add a detailed description with mne-bids.make_dataset_description. A generic description was created in: ' + root_folder)

        # Add a BIDS path for each setup
        bids_paths.append(
            BIDSPath(
                subject=(config['subject'] if 'subject' in config else None),
                session=(config['session'] if 'session' in config else None),
                task=(config['task'] if 'task' in config else None),
                acquisition=(config['acquisition'] if 'acquisition' in config else None),
                run=(config['run'] if 'run' in config else None),
                processing=(config['processing'] if 'processing' in config else None),
                recording=(config['recording'] if 'recording' in config else None),
                space=(config['space'] if 'space' in config else None),
                split=(config['split'] if 'split' in config else None),
                suffix=(config['suffix'] if 'suffix' in config else None),
                extension=(config['extension'] if 'extension' in config else None),
                root=(config['root'] if 'root' in config else None),
                datatype='eeg',
                check=True
            )
        )
    
    return bids_paths

def export_bids(raweeg = None, bids_paths = None, participants = None, overwrite = False, verbose=False):
    '''Export recordings in BIDS format.

    Args:
        raweeg : array
            EEG streams previously imported as MNE RawArray instances.
        bids_paths : array
            BIDS paths as MNE-BIDS BIDSPath instances.
        participants : array
            The participants in recordings. Template available in README.
        overwrite : bool
            Overwrite existing BIDS recordings.
        verbose : bool
            Show process while exporting.
    Raises:
        ValueError: if no stream is specified in raweeg, or raweeg and bids_paths do not have the same lenght.
    See also:
        create_bids_path
    '''
    if raweeg is None or bids_paths is None:
        raise ValueError('You must enter EEG recording and BIDS path array parameters.')

    raweeg = [raweeg] if not isinstance(raweeg, list) else raweeg
    bids_paths = [bids_paths] if not isinstance(bids_paths, list) else bids_paths
    participants = [participants] if not isinstance(participants, list) else participants

    if len(raweeg) != len(bids_paths):
        raise ValueError('BIDS path and eeg arrays must have the same length.')

    # Create BIDS 
    for index, recording in enumerate(raweeg):
        if system() == 'Windows':
            temporal_file_path = gettempdir() + '\\dummy_raw.fif'
        else:
            temporal_file_path = gettempdir() + '/dummy_raw.fif'
        
        if path.exists(temporal_file_path):
            remove(temporal_file_path)

        # Temporal file storing because of package requirements
        recording.save(temporal_file_path)
        file_rec = io.Raw(fname=temporal_file_path)

        # Create BIDS structure with EEG data
        write_raw_bids(
            raw=file_rec,
            bids_path=bids_paths[index],
            events_data=None,
            event_id=None,
            anonymize=None,
            overwrite=overwrite,
            verbose=verbose
        )
        
        remove(temporal_file_path)
        print('Exported recording: ', recording.annotations.description)

    # Fill participants info file
    if participants != 'None':
        for subject in participants:
            root_folder = r'%s' % subject['root']
            if system() == 'Windows':
                if root_folder[-1] == '\\':
                    root_folder = root_folder + 'participants.tsv'
                else:
                    root_folder = root_folder + '\\participants.tsv'
            else:
                if root_folder[-1] == '/':
                    root_folder = root_folder + 'participants.tsv'
                else:
                    root_folder = root_folder + '/participants.tsv'
        
        with open(root_folder, mode='r+', encoding='utf-8-sig') as tsvfile:
            reader = DictReader(tsvfile, dialect='excel-tab')

            data = []
            for par in reader:
                del par['weight']
                del par['height']
                for par2 in participants:
                    if par['participant_id'] == 'sub-'+par2['participant_id']:
                        par['age'] = par2['age']
                        par['sex'] = par2['sex']
                        par['hand'] = par2['hand']
                        break
                data.append(par)
            
            tsvfile.seek(0)
            tsvfile.truncate()
            
            writer = DictWriter(tsvfile, dialect='excel-tab', fieldnames=['participant_id', 'age', 'sex', 'hand'])
            writer.writeheader()
            for row in data:
                writer.writerow(row)
