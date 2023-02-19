# Global frames serves as a container for all global variables
class GFrame:
    def __init__(self):
        self.variables = {}


# Local frame is set to zero at the beginning and is used as a reference
# to the top of the stack of frames (the current frame) and ised to store
# local variables
class LFrame:
    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent


# Temporary frame is used to store temporary variables
class TFrame:
    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent


# Memory is resposible for handling all the frames
class Memory:
    def __init__(self):
        self.gframe = GFrame()
        self.lframe = LFrame()
        self.tframe = TFrame()

