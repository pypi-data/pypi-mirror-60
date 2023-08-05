from strify.replacing.replacement_data.replacement_data import ReplacementData


class FuncReplacementData(ReplacementData):
    def __init__(self, func):
        self.func = func

    @property
    def marker_name(self) -> str:
        return self.func.__name__

    @property
    def attr_name(self) -> str:
        return self.func.__name__
