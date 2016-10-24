# Read Midi Folders from style

import numpy as np
import GSBassmineMarkov as markov
import GSIO
import pickle


def strip_suffix(filename, suffix=None):
    """
    Strip off the suffix of the given filename or string.

    Parameters
    ----------
    filename : str
        Filename or string to strip.
    suffix : str, optional
        Suffix to be stripped off (e.g. '.txt' including the dot).

    Returns
    -------
    str
        Filename or string without suffix.

    """
    if suffix is not None and filename.endswith(suffix):
        return filename[:-len(suffix)]
    return filename


def match_files(filename, match_list, suffix=None, match_suffix=None):
    """
    Match a filename or string against a list of other filenames or strings.

    Parameters
    ----------
    filename : str
        Filename or string to strip.
    match_list : list
        Match to this list of filenames or strings.
    suffix : str, optional
        Suffix of `filename` to be ignored.
    match_suffix
        Match only files from `match_list` with this suffix.

    Returns
    -------
    list
        List of matched files.

    """
    import os
    import fnmatch

    # get the base name without the path
    basename = os.path.basename(strip_suffix(filename, suffix))
    # init return list
    matches = []
    # look for files with the same base name in the files_list
    if match_suffix is not None:
        pattern = "*%s*%s" % (basename, match_suffix)
    else:
        pattern = "*%s" % basename
    for match in fnmatch.filter(match_list, pattern):
        # base names must match exactly
        if basename == os.path.basename(strip_suffix(match, match_suffix)):
            matches.append(match)
    # return the matches
    return matches


def search_files(path, suffix=None):
    """
    Returns a list of files in `path` matching the given `suffix` or filters
    the given list to include only those matching the given suffix.

    Parameters
    ----------
    path : str or list
        Path or list of files to be searched / filtered.
    suffix : str, optional
        Return only files matching this suffix.

    Returns
    -------
    list
        List of files.

    """
    import os
    import glob

    # determine the files
    if isinstance(path, list):
        # a list of files or paths is given
        file_list = []
        # recursively call the function
        for f in path:
            file_list.extend(search_files(f, suffix))
    elif os.path.isdir(path):
        # use all files in the given path
        if suffix is None:
            file_list = glob.glob("%s/*" % path)
        elif isinstance(suffix, list):
            file_list = []
            for s in suffix:
                file_list.extend(glob.glob("%s/*%s" % (path, s)))
        else:
            file_list = glob.glob("%s/*%s" % (path, suffix))
    elif os.path.isfile(path):
        file_list = []
        # no matching needed
        if suffix is None:
            file_list = [path]
        # a list of suffices is given
        elif isinstance(suffix, list):
            for s in suffix:
                if path.endswith(s):
                    file_list = [path]
        # a single suffix is given
        elif path.endswith(suffix):
            file_list = [path]
    else:
        raise IOError("%s does not exist." % path)
    # remove duplicates
    file_list = list(set(file_list))
    # sort files
    file_list.sort()
    # return the file list
    return file_list


def write2pickle(name,data, path='../../models/'):
	"""
	Export numpy array to pickle
	:param name: filename
	:param data: allowed pickle data
	:param path: output folder
	:return:
	"""
	#path = 'rhythmic_analysis/graph_models/pickle/'

	with open(path + name + '.pickle', 'wb') as f:
		# Pickle the 'data' dictionary using the highest protocol available.
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def binaryBeatPattern(pattern, noBeats_bass, RES=4):
	"""
	Quantize array of note start times to 1/16 bar resolution
	Loop lengthn is quantized to multiples of whole bars

	:param pattern: array of start times in beats
	:return: array of binary onsets
	"""
	#RES = 4
	#noBeats_bass = uf.numberOfBeats(pattern)  # Bass files length set the global length of analysis
	print '\n# of beats: ', noBeats_bass
	#beat_subdiv = np.arange(start=0, step=0.25, stop=(noBeats_bass * RES) - 1)
	subdiv_aux = np.array([0., 0.25, 0.5, 0.75])
	# Matrix to store the binary representation of the midi files
	# Basslines -> 1 matrix
	rhythm = np.zeros((noBeats_bass, RES), dtype=int)

	for o in pattern:
		# quantize to the closest subdivision
		i, d = divmod(o, 1)  # i = row(beat number) , d = column (beat subdivision)
		d_ = (abs(subdiv_aux - d)).argmin()
		if i < noBeats_bass:
			rhythm[int(i), d_] = 1
	return rhythm


def translate_rhythm(rhythm):
	"""
	Translate binary rhythm to markov variables dictionary

	:param rhythm: array of binary onsets.(output of quantize_pattern())
	:return: array of beat pattern ids
	"""
	id = []

	for beat in rhythm:
		id.append((beat[0] * 8) + (beat[1] * 4) + (beat[2] * 2) + beat[3])
	return id


def corpus_analysis(bass_path, drum_path):
	"""
	Compute rhtyhmic model (temporal + interlocking)  and pitch model (intervals)

	Input files must match their names : i.e. bass_[trackname].mid , drums_[trackname].mid

	:param bass_path: folder with bass midi files
	:param drum_path: folder with drums midi files
	:return: rhythmic and pitch Markov Models , Kick patterns
	"""

	bass_files = search_files(bass_path, '.mid')
	drum_files = search_files(drum_path, '.mid')

	bass_names = []
	drum_names = []

	print "Bass Files"
	for bf in bass_files:
		bass_names.append(bf[len(bass_path) + 1:-len('.mid')])
	print "\nNumber of files: ", len(bass_files)

	print "\nDrums Files"
	for df in drum_files:
		drum_names.append(df[len(drum_path) + 1:-len('.mid')])
	print "\nNumber of files: ", len(drum_files)


	# File counter
	file_it = 0

	# Markov analysis object
	rhythm_model = markov.MarkovModel(16)
	kick_patterns = []

	# Pitch Model
	#pitch_model = markov.MarkovModel(25);
	#pitch_contours = []
	# LOOP THROUGH THE DIFFERENT MIDI INSTANCES
	for f in range(len(drum_files)):

		match = str(match_files('drums' + bass_names[f][4:], drum_names))
		match_file = drum_path + '/' + match[2:-2] + '.mid'

		print ('Bass file: '), bass_files[f]
		print ('Drum file: '), match_file
		print bass_names[f][5:-3]
		"""
		BASSLINE
		"""
		# Read Bassline files

		bass_pattern = GSIO.fromMidi(bass_files[f], "pitchNames", TagsFromTrackNameEvents=False)
		onset_bass = [x.startTime for x in bass_pattern.events]

		bass_rhythm = binaryBeatPattern(onset_bass, bass_pattern.duration)
		#print(bass_rhythm)
		bass_id = translate_rhythm(bass_rhythm)
		rhythm_model.add_temporal(bass_id)

		# Read Drum files
		# Filter kick notes
		kick_pattern = GSIO.fromMidi(match_file, {"Kick": 36}, TagsFromTrackNameEvents=False)
		onset_kick = [x.startTime for x in kick_pattern.events]
		# Quantize
		kick_rhythm = binaryBeatPattern(onset_kick, kick_pattern.duration)
		# print kick_rhythm
		# Translate
		kick_id = translate_rhythm(kick_rhythm)
		kick_patterns.append(kick_id)
		# Update interlocking model
		rhythm_model.add_interlocking(kick_id, bass_id)

		# Update file counter
		file_it += 1

	return rhythm_model, kick_patterns #, pitch_model

