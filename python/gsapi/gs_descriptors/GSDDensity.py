import os
import sys


if __name__=='__main__':

    sys.path.insert(1, os.path.abspath(os.path.join(__file__,
                                                    os.pardir,
                                                    os.pardir,
                                                    os.pardir)))


from gsapi import GSDescriptor

class GSDDensity(GSDescriptor):

    def __init__(self, ignored_tags = ["silence"], included_tags = []):

        GSDescriptor.__init__(self)
        self.ignored_tags = ignored_tags
        self.included_tags = included_tags


    def get_descriptor_for_pattern(self, pattern):

        density = 0
        _checked_pattern = pattern.get_pattern_withouth_tags(self.ignored_tags)

        if self.included_tags:
            _checked_pattern = _checked_pattern.getPatternWithTags(self.included_tags,
                                                                   copy=False)
        for e in _checked_pattern.events:
                density += e.duration
        return density
