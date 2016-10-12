from gsapi import *


desired_pattern_length = 4
collection_folder = "../../python/test/midi/*.mid"
custom_note_mapping = {"spam":[(35, '*'), 45],
					   "kick":(36),
					   "rimshot":37,
					   "snare":38,
					   "clap":39,
					   "clave":40,
					   "lowTom":41,
					   "closedHH":42,
					   "midTom":43,
					   "shaker":44,
					   "hiTom":45,
					   "openHH":46,
					   "lowConga":47,
					   "hiConga":48,
					   "cymbal":49,
					   "conga":50,
					   "cowbell":51
					   # combination
					   # "lowFrequencies" :[33,34,35,36,63]
					   }


patterns = GSIO.from_midi_collection(collection_folder,
									 custom_note_mapping,
									 tags_from_trackname_events=False)
