import logging
import os
import glob

gsiolog = logging.getLogger("gsapi.GSIO")
gsiolog.setLevel(level=logging.INFO)

from gsapi import *
from midi_map import *

def from_midi(midi_path,
              note_to_tags_map,
              tracks_to_get = [],
              tags_from_trackname_events=False,
              filter_out_not_mapped=True,
              check_for_overlapped=False):
    """
    Load a midi file as a GSpattern.

    :param midi_path: midi file path
    :param note_to_tags_map: dictionary converting pitches to tags. If only interested in pitch, you can set it to "pitch_names", and optionally set the value to the list of strings for pitches from C. noteMapping maps classes to a list of possible Mappings, a mapping can be:
            - a tuple of (note, channel). If one of those doesnt matter it can be replaced by '*' character
            - an integer if only pitch matters.
            For simplicity one can pass only one integer (i.e not a list) for one-to-one mappings.
            If the midi track contains the name of one element of mapping, it'll be choosed without anyother consideration
    :param tracks_to_get: if not empty, specifies tracks wanted either by name or index.
    :param tags_from_trackname_events: Use only track names to resolve mapping, useful for midi containing named tracks.
    :param filter_out_not_mapped: if set to true, don't add event not represented by note_to_tags_map
    :param check_for_overlapped: if true, it will check that two consecutive events with exactly same midi note are not overlapping.
    :return:
    """
    _note_to_tags_map = __format_note_to_tags(note_to_tags_map)
    return __from_midi_formatted(midi_path=midi_path,
                                 note_to_tags_map=_note_to_tags_map,
                                 tracks_to_get = tracks_to_get,
                                 tags_from_trackname_events=tags_from_trackname_events,
                                 filter_out_not_mapped=filter_out_not_mapped,
                                 check_for_overlapped=check_for_overlapped)



def from_midi_collection(midi_glob_path,
                         note_to_tags_map,
                         tracks_to_get = [],
                         tags_from_trackname_events=False,
                         filter_out_not_mapped = True,
                         desired_length = 0):
    """
    Loads a midi file collection

    Args:
        midi_glob_path: midi file path in glob naming convention (e.g '/folder/to/crawl/*.mid').
        desired_length: optionally cut patterns in equal length.
        otherArguments: as defined in :py:func:`from_midi`
    Returns:
        a list of GSPattern built from the midi folder
    """

    res = []
    __note_to_tags_map = __format_note_to_tags(note_to_tags_map)
    for f in glob.glob(midi_glob_path):
        name =  os.path.splitext(os.path.basename(f))[0]
        gsiolog.info("getting " + name)
        p = from_midi(f,
                      __note_to_tags_map,
                      tags_from_trackname_events=tags_from_trackname_events,
                      filter_out_not_mapped=filter_out_not_mapped)

        if desired_length > 0:
            res += p.split_in_equal_length_patterns(desired_length,
                                                    copy=False)
        else:
            res+=[p]

    return res


def PatternFromJSONFile(filePath):
    """ load a pattern to internal JSON Format

    Args:
        filePath:filePath where to load it
    """
    with open(filePath,'r') as f:
        return GSPattern().fromJSONDict(json.load(f))

def PatternToJSONFile(pattern,filePath):
    """ save a pattern to internal JSON Format

    Args:
        filePath:filePath where to save it
    """
    with open(filePath,'w') as f:
        return json.dump(pattern.toJSONDict(),f)




def __format_note_to_tags(_NoteToTags):
    """ internal conversion for consistent NoteTagMap Structure

    """
    import copy
    NoteToTags = copy.copy(_NoteToTags)
    if(NoteToTags == "pitchNames"):
        NoteToTags = {"pitchNames":""}
    for n in NoteToTags:
        if n=="pitchNames":
            if not NoteToTags["pitchNames"]:
                NoteToTags["pitchNames"] = defaultPitchNames
        else:
            if not isinstance(NoteToTags[n],list): NoteToTags[n] = [NoteToTags[n]]
            for i in range(len(NoteToTags[n])):
                if isinstance(NoteToTags[n][i],int):NoteToTags[n][i] = (NoteToTags[n][i],'*')
    return NoteToTags


def __from_midi_formatted(midi_path,
                          note_to_tags_map,
                          tracks_to_get = [],
                          tags_from_trackname_events=False,
                          filter_out_not_mapped=True,
                          check_for_overlapped=False):
    """
    Internal function that accepts only a consistent note_tag_map structure as created by __format_note_to_tags
    """
    import os
    import midi

    global_midi = midi.read_midifile(midi_path)
    global_midi.make_ticks_abs()
    pattern = GSPattern()
    pattern.name = os.path.basename(midi_path)

    # get signature first:
    gsiolog.info("start processing %s" % pattern.name)
    __find_time_info_from_midi(pattern, global_midi)

    tick_to_quarter_note = 1.0 / global_midi.resolution

    pattern.events = []
    last_note_off = 0
    not_found_tags = []
    track_idx = 0

    for tracks in global_midi:
        should_skip_track = False
        last_pitch = -1
        last_tick = -1
        for e in tracks:
            if should_skip_track:
                continue
            if not tags_from_trackname_events:
                note_tags = []
            if midi.MetaEvent.is_event(e.statusmsg):
                if e.metacommand == midi.TrackNameEvent.metacommand:
                    if tracks_to_get != [] and not((e.text in tracks_to_get) or (track_idx in tracks_to_get)):
                        gsiolog.info('skipping track: %i %s' % (track_idx, e.text))
                        should_skip_track = True
                        continue
                    else:
                        gsiolog.info(pattern.name + ': getting track: %i %s' % (track_idx, e.text))

                    if tags_from_trackname_events:
                        note_tags = __find_tags_from_name(e.text, note_to_tags_map)

            is_note_on = midi.NoteOnEvent.is_event(e.statusmsg)
            is_note_off =midi.NoteOffEvent.is_event(e.statusmsg)
            if is_note_on or is_note_off:
                pitch = e.pitch  # optimize pitch property access
                tick = e.tick
                current_beat = tick * 1.0 * tick_to_quarter_note
                if note_tags == []:
                    if tags_from_trackname_events:
                        continue
                    note_tags = __find_tags_from_pitch_and_channel(pitch, e.channel, note_to_tags_map)

                if note_tags == []:
                    if [e.channel,pitch] not in not_found_tags:
                        gsiolog.info(pattern.name + ": no tags found for pitch %d on channel %d" % (pitch,e.channel))
                        not_found_tags += [[e.channel,pitch]]
                    if filter_out_not_mapped:
                        continue

                if is_note_on:
                    # ignore duplicated events (can't have 2 simultaneous note_on for the same pitch)
                    if  pitch == last_pitch and tick == last_tick:
                        gsiolog.info(pattern.name + ': skip duplicated event: %i %f' % (pitch,current_beat))
                        continue
                    last_pitch = pitch
                    last_tick = tick
                    # print "on" + str(pitch) + ":" + str(tick * 1.0 * tick_to_quarter_note)
                    pattern.events += [GSPatternEvent(startTime=current_beat,
                                                      duration=-1,
                                                      pitch=pitch,
                                                      velocity=127,
                                                      tags=note_tags)]

                if is_note_on or is_note_off:
                    # print "off" + str(pitch) + ":" + str(tick * 1.0 * tick_to_quarter_note)
                    found_note_on = False
                    for i in reversed(pattern.events):
                        if (i.pitch == pitch) and (i.tags==note_tags) and current_beat >= i.startTime and i.duration<=0.0001:
                            found_note_on = True
                            i.duration = max(0.0001, current_beat - i.startTime)
                            last_note_off = max(current_beat, last_note_off)
                            # print "set duration" + str(i.duration) + "at start" + str(i.start_time)
                            break
                    if not found_note_on and midi.NoteOffEvent.is_event(e.statusmsg):
                        gsiolog.warning(pattern.name + ": not found note on " + str(e) + str(pattern.events[-1]))
        track_idx+=1

    element_size = 4.0 / pattern.time_signature[1]
    bar_size = pattern.time_signature[0] * element_size
    last_bar_pos = math.ceil(last_note_off * 1.0 / bar_size) * bar_size
    pattern.duration = last_bar_pos

    if check_for_overlapped:
        pattern.remove_overlapped(use_pitch_values=True)

    return pattern


def __find_time_info_from_midi(pattern, midi_file):

    import midi

    found_time_signature_event = False
    found_tempo = False
    pattern.time_signature = [4, 4]
    pattern.bpm = 60
    for tracks in midi_file:
        for e in tracks:
            if midi.MetaEvent.is_event(e.statusmsg):
                if e.metacommand == midi.TimeSignatureEvent.metacommand:
                    if found_time_signature_event and (pattern.time_signature != [e.numerator, e.denominator]):
                        gsiolog.error(pattern.name + ": multiple time_signature found; unsupported, result can be altered.")
                    found_time_signature_event = True
                    pattern.time_signature = [e.numerator, e.denominator]
                    #  e.metronome = e.thirtyseconds ::  do we need that ???
                elif e.metacommand == midi.SetTempoEvent.metacommand:
                    if found_tempo:
                        gsiolog.error(pattern.name + ": multiple bpm found; unsupported.")
                    found_tempo = True
                    pattern.bpm = e.bpm

        if found_time_signature_event:
            break
    if not found_time_signature_event:
        gsiolog.warning(pattern.name + ": no time_signature event found.")


def __find_tags_from_name(name, note_mapping):

    res =[]
    for l in note_mapping:
        if l in name:
            res+=[l]
        return res


def __find_tags_from_pitch_and_channel(pitch, channel, note_mapping):

    def pitch_to_name(pitch, pitch_names):
        octave_length = len(pitch_names)
        octave  = (pitch / octave_length) - 2 # 0 is C-2
        note = pitch % octave_length
        return pitch_names[note] + "_" + str(octave)

    if "pitch_names" in note_mapping.keys():
        return [pitch_to_name(pitch, note_mapping["pitch_names"])]
    res = []
    for l in note_mapping:
        for le in note_mapping[l]:
            if (le[0] in {'*',pitch}) and (le[1] in {'*',channel}):
                res += [l]

    return res
