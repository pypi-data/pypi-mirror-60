from strify import stringifyable, StringifyInfo


def format_proper_name(string):
    return ' '.join((word[0].upper() + word[1:].lower() for word in string.split(' ')))


if __name__ == '__main__':
    @stringifyable([
        StringifyInfo('artist', 'artist', format_proper_name),
        StringifyInfo('title', 'title', format_proper_name),
        StringifyInfo('year', 'year'),
        StringifyInfo('hash', '__hash__'),
    ])
    class Song:
        def __init__(self, artist, title, year):
            self.artist = artist
            self.title = title
            self.year = year

        def __hash__(self):
            return hash(str(self.artist) + self.title)


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
