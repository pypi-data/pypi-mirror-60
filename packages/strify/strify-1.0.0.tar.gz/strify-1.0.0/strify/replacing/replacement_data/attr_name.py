from strify.replacing.replacement_data.replacement_data import ReplacementData


class AttrNameReplacementData(ReplacementData):
    def __init__(self, marker_name, attr_name):
        self._marker_name = marker_name
        self._attr_name = attr_name

    @property
    def marker_name(self) -> str:
        return self._marker_name

    @property
    def attr_name(self) -> str:
        return self._attr_name
