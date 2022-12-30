from setuptools import find_packages, setup

setup(
    name='musestudio',
    packages=find_packages(),
    version='0.2.0',
    description='Import Muse recordings. Convert data to MNE and Pandas. View brain data in real time.',
    url='https://github.com/miguelascifo/MuseStudio',
    author='Miguel Ángel Sánchez Cifo',
    author_email='code@miguelascifo.com',
    license='MIT',
    install_requires=[
        'dash',
        'dash_daq',
        'mne',
        'mne_bids',
        'numpy',
        'pandas',
        'plotly',
        'pybv',
        'pylsl',
        'pyxdf'
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development'
    ],
    keywords='neuroscience neuroevaluation EEG brain muse',
    platforms='any'
)
