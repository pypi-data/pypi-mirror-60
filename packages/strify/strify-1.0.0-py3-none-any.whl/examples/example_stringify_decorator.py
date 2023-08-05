from strify import stringifyable, stringify


def format_proper_name(string):
    return ' '.join((word[0].upper() + word[1:].lower() for word in string.split(' ')))


if __name__ == '__main__':
    @stringifyable()
    class Song:
        def __init__(self, artist, title, year):
            self._artist = artist
            self._title = title
            self._year = year

        @property
        @stringify(format_proper_name)
        def artist(self):
            return self._artist

        @property
        @stringify(format_proper_name)
        def title(self):
            return self._title

        @property
        @stringify()
        def year(self):
            return self._year

        def __hash__(self):
            return hash(str(self._artist) + self._title)


    people = [
        Song('we butter the bread with butter', 'alptraum song', 2010),
        Song('falling in reverse', 'loosing my mind', 2018)
    ]

    patterns = [
        '[artist] -- [title] ([year])',
        '[title]: [artist], [year]'
    ]

    for person in people:
        for pattern in patterns:
            print(person.stringify(pattern))
