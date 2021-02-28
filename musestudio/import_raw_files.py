import ntpath
from glob import glob
from platform import system
from pyxdf import load_xdf

def read_raw_xdf(filename = None):
    '''Import a single XDF file format that contains one recording.

    Args:
        filename : string
            full path to a single recording
    Returns:
        Four arrays containing the data for these streams: EEG, Accelerometer, PPG, Gyroscope.
        Additionally, another array is returned with the filename.
    Raises:
        ValueError: if filename is not specified.
        RuntimeError: if filename is not in XDF format or not file found.
    See also:
        read_raw_xdf_dir
    '''
    if filename is None:
        raise(ValueError('Enter XDF file path.'))

    if system() == 'Windows':
        filename = r'%s' % filename
    
    if not filename.endswith('.xdf'):
        raise(RuntimeError('File type must be XDF.'))
    
    if len(glob(filename)) == 0:
        raise(RuntimeError('XDF file not found.'))

    return get_files(filename)

def read_raw_xdf_dir(dirname = None):
    '''Import a directory with multiple recordings in XDF format.

    Args:
        dirname : string
            full path to directory
    Returns:
        Four arrays containing the data for these streams: EEG, Accelerometer, PPG, Gyroscope.
        Additionally, another array is returned with the filenames
    Raises:
        ValueError: if dirname is not specified
        RuntimeError: if files are not found
    See also:
        read_raw_xdf
    '''
    if dirname is None:
        raise(ValueError('Enter XDF files directory name.'))

    if system() == 'Windows':
        dirname = r'%s' % dirname
        if dirname[-1] == '\\':
            dirname_xdf = dirname + '*.xdf'
        else:
            dirname_xdf = dirname + '\\*.xdf'
    else:
        if dirname[-1] == '/':
            dirname_xdf = dirname + '*.xdf'
        else:
            dirname_xdf = dirname + '/*.xdf'

    if len(glob(dirname_xdf)) == 0:
        raise(RuntimeError('XDF files not found in directory.'))
    
    return get_files(dirname_xdf)

def load_data(filename):
    '''Get recordings from a single XDF file and order streams by device.'''
    # Load XDF file
    streams = load_xdf(filename)
    
    streameeg, streamacc, streamppg, streamgyr, device_name = [], [], [], [], []
    
    # Get the individual names of every Muse device
    for stream in streams[0]:
        name = stream['info']['name'][0][:9]
        if name not in device_name:
            device_name.append(name)
    
    # Order the streams in a new list based on the name of the device
    streams_ordered = []
    for item in device_name:
        if len(streams_ordered) < (len(device_name)*4)+len(device_name):
            for stream in streams[0]:
                if item == stream['info']['name'][0][:9]:
                    streams_ordered.append(stream)
    
    # Insert each stream inside a file into the corresponding list
    for stream in streams_ordered:
        if 'EEG' in stream['info']['type'][0]:
            streameeg.append(stream)
        if 'Accelerometer' in stream['info']['type'][0]:
            streamacc.append(stream)
        if 'Gyroscope' in stream['info']['type'][0]:
            streamgyr.append(stream)
        if 'PPG' in stream['info']['type'][0]:
            streamppg.append(stream)
    
    return streameeg, streamacc, streamppg, streamgyr

def get_files(files):
    '''Get files from directory and insert recordings into arrays.'''
    # Get files from directory path
    files = sorted(glob(files))
    
    streameeg, streamacc, streamppg, streamgyr, filename = [], [], [], [], []
    
    # Search XDF files and add individual channels to the corresponding list. Store the name of the file.
    for f in files:
        streameeg_file, streamacc_file, streamppg_file, streamgyr_file = load_data(f)
        for item in streameeg_file:
            streameeg.append(item)
            filename.append(ntpath.basename(f))
        for item in streamacc_file:
            streamacc.append(item)
        for item in streamppg_file:
            streamppg.append(item)
        for item in streamgyr_file:
            streamgyr.append(item)
    
    return streameeg, streamacc, streamppg, streamgyr, filename
