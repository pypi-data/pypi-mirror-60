import os
import numpy as np
import unittest
from datetime import datetime
from pynwb import NWBHDF5IO, NWBFile
from pynwb.device import Device
from pynwb.ophys import OpticalChannel
from ndx_fret import FRET, FRETSeries


class FRETTest(unittest.TestCase):

    def setUp(self):
        self.nwbfile = NWBFile('description', 'id', datetime.now().astimezone())

    def test_add_fretseries(self):
        # Create and add device
        device = Device(name='Device')
        self.nwbfile.add_device(device)

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
            data=np.random.randn(20, 5, 5),
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
            data=np.random.randn(20, 5, 5),
            rate=60.,
            unit='',
        )

        fret = FRET(
            name='FRET',
            excitation_lambda=482.,
            donor=fs_d,
            acceptor=fs_a
        )
        self.nwbfile.add_acquisition(fret)

        filename = 'test_fret.nwb'

        with NWBHDF5IO(filename, 'w') as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(filename, mode='r') as io:
            io.read()

        #assert(all(cs.find_compartments(0, [1, 3]) == [1, 3]))
        #assert(all(cs.find_compartments(1) == 5))

        os.remove(filename)
