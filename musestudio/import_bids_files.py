from mne_bids import BIDSPath, read_raw_bids

def import_bids(setup=None):
    '''Import recordings in BIDS format.

    Args:
        setup : array
            The setup of each recording. Template available in README.
    Returns:
        Two arrays: the recordings as MNE RawArray instances, and the bids paths as MNE-BIDS BIDSPath instances.
    Raises:
        ValueError: if no setup is specified.
    '''
    if setup is None:
        raise(ValueError('Enter BIDS setup parameter array.'))

    setup = [setup] if not isinstance(setup, list) else setup

    raweeg, bids_paths = [], []

    # Iterate over the recordings setup to import from BIDS format
    for config in setup:
        import_path = BIDSPath(
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

        bids_paths.append(import_path)

        raweeg.append(read_raw_bids(import_path))

    return raweeg, bids_paths
