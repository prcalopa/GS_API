from gsapi import *

crawledFolder = "../../python/test/midi/*.mid"


customNoteMapping = {
		"spam":[(35,'*'),45],
		"Kick":(36),
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
		"CowBell":51

# combination
	# "lowFrequencies" :[33,34,35,36,63]

}


desiredPatternLength = 4;

patterns = GSIO.fromMidiCollection(crawledFolder,customNoteMapping,TagsFromTrackNameEvents=False)


	
