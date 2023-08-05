from pynwb import NWBFile, NWBHDF5IO
from pynwb.device import Device
from pynwb.ophys import OpticalChannel
from ndx_fret import FRET, FRETSeries

from datetime import datetime
import numpy as np

nwb = NWBFile('session_description', 'identifier', datetime.now().astimezone())

# Create and add device
device = Device(name='Device')
nwb.add_device(device)

# Create optical channels
opt_ch_d = OpticalChannel(
    name='optical_channel',
    description='',
    emission_lambda=450.
)
opt_ch_a = OpticalChannel(
    name='optical_channel',
    description='',
    emission_lambda=500.
)

# Create FRET
fs_d = FRETSeries(
    name='donor',
    fluorophore='mCitrine',
    optical_channel=opt_ch_d,
    device=device,
    emission_lambda=0.0,
    description='',
    data=np.random.randn(100, 10, 10),
    rate=60.,
    unit='',
)
fs_a = FRETSeries(
    name='acceptor',
    fluorophore='mKate2',
    optical_channel=opt_ch_a,
    device=device,
    emission_lambda=0.0,
    description='',
    data=np.random.randn(100, 10, 10),
    rate=60.,
    unit='',
)

fret = FRET(
    name='FRET',
    excitation_lambda=482.,
    donor=fs_d,
    acceptor=fs_a
)
nwb.add_acquisition(fret)
print(nwb)

# Write nwb file
with NWBHDF5IO('test_fret.nwb', 'w') as io:
    io.write(nwb)
    print('NWB file written')

# Read nwb file and check its content
with NWBHDF5IO('test_fret.nwb', 'r', load_namespaces=True) as io:
    nwb = io.read()
    print(nwb)
