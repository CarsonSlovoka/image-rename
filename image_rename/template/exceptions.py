class InvalidTemplateLibrary(Exception):
    def __init__(self, why=None):
        Exception.__init__(self, why)
        self.why = why


class HotkeyConflictWarning(Warning):
    ...
