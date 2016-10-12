import os
import sys


if __name__=='__main__':

    sys.path.insert(1, os.path.abspath(os.path.join(__file__,
                                                    os.pardir,
                                                    os.pardir,
                                                    os.pardir)))


from gsapi import GSDescriptor


class GSDNumberOfTags(GSDescriptor):

    def __init__(self, ignored_tags=["silence"], included_tags=[]):

        GSDescriptor.__init__(self)
        self.ignored_tags = ignored_tags
        self.included_tags = included_tags


    def getDescriptorForPattern(self, pattern):

        _checked_pattern = pattern.get_pattern_without_tags(self.ignored_tags)

        if self.included_tags:
            _checked_pattern = _checked_pattern.get_pattern_with_tags(self.included_tags,
                                                                      copy=False)

        return len(_checked_pattern.get_all_tags())
