Example using JUCE library
=====
This VST Plugin is for testing purpose only .

This VST loads a python file (python/VSTPlugin.py) and implement a basic API to:
* display and play a GSPattern
* call python functions from VST UI

###Interface
A basic interface allowing to show python file being processed, reloading it and autowatching the file (reload each time the file is modified). The file is in the VST bundle, under Resources/python. You need to install the python gsapi first (see GS_API Readme.md)

### Dependencies

Cython, numpy, python-midi

### Known Bugs

work in pretty much all DAWs (Bitwig,JUCEAudiopluginHostDemo ...) but does not work in Ableton Live yet.
