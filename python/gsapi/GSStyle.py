from GSPattern import GSPattern


class GSStyle(object):
    """
    Base class for defining a style.

	Such class needs to provide the following functions:
		- generate_style(self, pattern_classes)
		- generate_pattern(self, seed=None)
		- get_distance_from_style(self, pattern)
		- get_closest_pattern(self, pattern, seed=None)
		- get_interpolated(self, patternA, patternB, distance_from_A, seed=None)
		- get_internal_state(self)
		- load_internal_state(self, internal_state_dict)
		- is_built(self)
    """


    def __init__(self):
        self.type = "None"


    def generate_style(self, pattern_classes):
        """Computes the inner state of a style based on a list of patterns."""
        raise NotImplementedError("Martin should have implemented this ;-)")


    def generate_pattern(self, seed=None):
        """Generates a new random pattern using a seed if not "None".
		Ideally, the same seed should lead to the same pattern."""
        raise NotImplementedError("Martin should have implemented this ;-)")


    def get_distance_from_style(self, pattern):
        """Returns a normalized value representing the "styleness" of a
        pattern, 0 being the closest to style and 1 the farthest."""
        raise NotImplementedError("Martin should have implemented this ;-)")


    def get_closest_pattern(self, pattern, seed=None):
        """Returns the closest pattern in the current style."""
        raise NotImplementedError("Martin should have implemented this ;-)")


    def get_interpolated(self, patternA, patternB, distance_from_A, seed=0):
        """ Interpolates between 2 patterns given this style constraints."""
        raise NotImplementedError("Martin should have implemented this ;-)")


    def get_internal_state(self):
        """Returns a dictionary representing the current internal state"""
        raise NotImplementedError("Martin should have implemented this ;-)")


    def set_internal_state(self, internal_state_dict):
        """Loads internal state from a given dictionary."""
        raise NotImplementedError("Martin should have implemented this ;-)")


    def is_built(self):
        """Returns True if style has been correctly built."""
        raise NotImplementedError("Martin should have implemented this ;-)")


    def save_to_json(self, file_path):

        import json
        state = self.get_internal_state()
        with open(file_path, 'w') as f:
            json.dump(state, f)


    def load_from_json(self, file_path):

        import json
        with open(file_path, 'r') as f:
            state = json.load(f)
        if state:
            self.set_internal_state(state)


    def save_to_pickle(self, file_path):

        import cPickle
        cPickle.dump(self, file_path)


    def load_from_pickle(self, file_path):

        import cPickle
        GSStyle.self = cPickle.load(file_path)  # Likely angel's mess!
