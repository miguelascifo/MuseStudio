import numpy as np
import pandas as pd
from datetime import datetime
from mne import channels, create_info, io, Annotations

def to_mne_eeg(eegstream = None, line_freq = None,  filenames = None, nasion = None, lpa = None, rpa = None):
    '''Convert recordings to MNE format.

    Args:
        eegstream : array
            EEG streams previously imported.
        line_freq : int
            Powerline frequency (50 or 60).
        filenames : array
            Full path of XDF files. Used for recording identification.
        nasion : array, shape(3,)
            Position of the nasion fiducial point.
            If specified, the array must have the same lenght of eegstream.
            Format for every recording (X, Y, Z) in meters: [0,0,0]
        lpa : array, shape(3,)
            Position of the left periauricular fiducial point.
            If specified, the array must have the same lenght of eegstream.
            Format for every recording (X, Y, Z) in meters: [0,0,0]
        rpa : array, shape(3,)
            Position of the right periauricular fiducial point.
            If specified, the array must have the same lenght of eegstream.
            Format for every recording (X, Y, Z) in meters: [0,0,0]
    Returns:
        Array of MNE RawArray instances with the recordings specified in eegstream.
    Raises:
        ValueError: if no stream is specified in eegstream or powerline frequency is not 50 or 60.
    See also:
        read_raw_xdf
        read_raw_xdf_dir
    '''
    if eegstream is None:
        raise(ValueError('Enter parameter array of EEG recordings.'))
    
    if line_freq is None or line_freq not in [50, 60]:
        raise(ValueError('Enter the powerline frequency of your region (50 Hz or 60 Hz).'))
    
    eegstream = [eegstream] if not isinstance(eegstream, list) else eegstream

    raweeg = []
    
    # Get the names of the channels
    ch_names = [eegstream[0]['info']['desc'][0]['channels'][0]['channel'][i]['label'][0] for i in range(len(eegstream[0]['time_series'][0]))]
    
    # Define sensor coordinates
    sensor_coord = [[-0.0856192, -0.0465147, -0.0457070], [-0.0548397, 0.0685722, -0.0105900], [0.0557433, 0.0696568, -0.0107550], [0.0861618, -0.0470353, -0.0458690]]
    
    for index, stream in enumerate(eegstream):
        # Get channels position
        dig_montage = channels.make_dig_montage(ch_pos=dict(zip(ch_names, sensor_coord)), nasion=nasion if nasion is not None else None, lpa=lpa if lpa is not None else None, rpa=rpa if rpa is not None else None, coord_frame='head')
        # Create raw info for processing
        info = create_info(ch_names=dig_montage.ch_names, sfreq=float(stream['info']['nominal_srate'][0]), ch_types='eeg')
        # Add channels position to info
        info.set_montage(dig_montage)
        # Convert data from microvolts to volts
        conv_data = stream["time_series"] * 1e-6
        # Reorder channels
        ord_data = [[sublist[1][item] for item in [1, 2, 3, 0]] for sublist in enumerate(conv_data)]
        # Create raw data for mne
        raw = io.RawArray(np.array(ord_data).T, info)
        # Get the information of each stream
        stream_info = stream['info']['name'][0][:9] + ' ' + (filenames[index] if filenames is not None else '')
        # Print the information of each stream
        print('\nInfo: ' + str(index) + ' ' + stream_info + '\n')
        # Add the powerline frequency of each stream
        raw.info['line_freq'] = line_freq
        # Create annotation to store the name of the device and the filenames
        annotations = Annotations(0, 0, stream_info)
        # Add the annotations to raw data
        raw.set_annotations(annotations)
        # Add the RawArray object to list of eeg recordings
        raweeg.append(raw)
    
    return raweeg

def to_df(mne_eeg = None, eegstream = None, accstream = None, ppgstream = None, gyrstream = None):
    '''Convert recordings to Pandas DataFrame.

    Args:
        mne_eeg : array
            EEG streams as MNE RawArray instances.
        eegstream : array
            EEG streams. Used for timestamps.
        accstream : array
            Accelerometer streams.
        gyrstream : array
            Gyroscope streams.
        ppgstream : array
            PPG streams.
    Returns:
        An array containing the dataframes for the streams specified.
    Raises:
        ValueError: if mne_eeg or eegstream are not specified.
    See also:
        to_mne_eeg
    '''
    if mne_eeg is None or eegstream is None:
        raise(ValueError('Enter EEG recordings in MNE and array formats.'))
    
    mne_eeg = [mne_eeg] if not isinstance(mne_eeg, list) else mne_eeg
    eegstream = [eegstream] if not isinstance(eegstream, list) else eegstream
    accstream = [accstream] if not isinstance(accstream, list) and accstream is not None else accstream
    gyrstream = [gyrstream] if not isinstance(gyrstream, list) and gyrstream is not None else gyrstream
    ppgstream = [ppgstream] if not isinstance(ppgstream, list) and ppgstream is not None else ppgstream

    df_array = []
    # Iterate through each stream, convert them into dataframes and merge them
    for index, stream in enumerate(mne_eeg):
        df = stream \
            .to_data_frame(scalings=dict(eeg=1)) \
            .reset_index() \
            .join(pd.Series(eegstream[index]['time_stamps']).rename('timestamp')) \
            .drop('time', axis=1)
        df['timestamp'] = df['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
        df = df[['timestamp', 'AF7', 'AF8', 'TP9', 'TP10']]
        df.index.rename('index', inplace=True)

        if accstream is not None:
            df_acc = pd.DataFrame(accstream[index]['time_series'], columns=['X_acc', 'Y_acc', 'Z_acc'])
            # Multiply the indexes to match the incoming eeg data rate from the device (256/50 = 5.12)
            df_acc.index = df_acc.index * 5
            df_acc.index.rename('index', inplace=True)
            df = pd.merge_asof(df, df_acc, on='index', by='index')

        if gyrstream is not None:
            df_gyr = pd.DataFrame(gyrstream[index]['time_series'], columns=['X_gyr', 'Y_gyr', 'Z_gyr'])
            df_gyr.index = df_gyr.index * 5
            df_gyr.index.rename('index', inplace=True)
            df = pd.merge_asof(df, df_gyr, on='index', by='index')

        if ppgstream is not None:
            df_ppg = pd.DataFrame(ppgstream[index]['time_series'], columns=['1_ppg', '2_ppg', '3_ppg'])
            df_ppg.index = df_ppg.index * 4
            df_ppg.index.rename('index', inplace=True)
            df = pd.merge_asof(df, df_ppg, on='index', by='index')
        
        if accstream is not None or gyrstream is not None or ppgstream is not None:
            df.drop('index', axis=1, inplace=True)
        #df.interpolate(method='linear', limit_direction='forward', axis=0, inplace=True)
        
        df_array.append(df)
    return df_array
