import os
import glob
import logging
from gsapi import *

datasetLog = logging.getLogger("GSDataset")


class GSDataset(object):
    """
    Helper to hold a list of patterns imported from specific gpath (glob style).

    TODO: documentation.
    """
    default_midi_folder = os.path.abspath(__file__ + "../../../../test/midiDatasets/")
    default_midi_glob = "*/*.mid"
    default_drum_midi_map = {"Kick": 36,
                             "Rimshot":37,
                             "Snare":38,
                             "Clap":39,
                             "Clave":40,
                             "LowTom":41,
                             "ClosedHH":42,
                             "MidTom":43,
                             "Shake":44,
                             "HiTom":45,
                             "OpenHH":46,
                             "LowConga":47,
                             "HiConga":48,
                             "Cymbal":49,
                             "Conga":50,
                             "CowBell":51}


    def __init__(self,
                 midi_folder = default_midi_folder,
                 midi_glob = default_midi_glob,
                 midi_map = default_drum_midi_map,
                 check_for_overlapped = True):
        self.midi_folder = midi_folder
        self.midi_map = midi_map
        self.check_for_overlapped = check_for_overlapped
        self.set_midi_glob(midi_glob)
        self.import_midi()


    def set_midi_glob(self, glob_pattern):
        if '.mid' in glob_pattern[-4:]: glob_pattern = glob_pattern[:-4]
        self.midi_glob = glob_pattern + '.mid'
        self.glob_path = os.path.abspath(os.path.join(self.midi_folder,
                                                      self.midi_glob))
        self.files = glob.glob(self.glob_path)
        if  len(self.files) == 0:
            datasetLog.error("no files found for path " + self.glob_path)
        else:
            self.idx = random.randint(0, len(self.files) - 1)


    def get_all_slice_of_duration(self, desired_duration):
        res = []
        for p in self.patterns:
            res += p.splitInEqualLengthPatterns(desired_length=desired_duration)
        return res


    def import_midi(self, file_name=""):

        if file_name:
            set_midi_glob(file_name)

        self.patterns = []

        for p in self.files:
            datasetLog.info('using ' + p)
            p = GSIO.from_midi(p,
                               self.midi_map,
                               tracksToGet=[],
                               check_for_overlapped=self.check_for_overlapped)
            self.patterns += [p]

        return self.patterns
