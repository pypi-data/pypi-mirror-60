import csv


RECORD_SEP = "\u241E"
BLOCKSIZE = 65536


class bcp_dialect(csv.Dialect):
    """Describe the usual properties of BCP files."""
    delimiter = '@**@'
    lineterminator = '*@@*'
    quoting = csv.QUOTE_NONE

    def _validate(self):
        pass


class reader:

    def __init__(self, fp, dialect='bcp', blocksize=BLOCKSIZE, **fmtparams):
        self.reader = faststream(
            fp,
            dialect=dialect,
            blocksize=blocksize,
            **fmtparams
        )
        self.line_num = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.line_num += 1
        return next(self.reader)


def faststream(fp, dialect='bcp', blocksize=BLOCKSIZE, **fmtparams):
    """Read a BCP file and yield the rows

    fp is a file pointer to a BCP file opened in 'r' mode.

    It is assumed the file is opened with the correct encoding, so thatß
    fp.read() gives strings. A trailing newline may need to be added
    after this method to get exact results.

    Author: Gertjan van den Burg
    License: MIT
    Copyright: 2020, The Alan Turing Institute

    """
    if dialect != 'bcp':
        return csv.reader(fp, dialect=dialect, **fmtparams)

    d = bcp_dialect()
    delimiter = fmtparams.get("delimiter", d.delimiter)
    lineterminator = fmtparams.get("delimiter", d.lineterminator)
    chars = set(delimiter + lineterminator)

    block = fp.read(blocksize)
    trail = None
    while len(block) > 0:
        lines = []
        if trail is not None:
            block = trail + block

        # if we see a char from either of the terminators
        # then add a bit more onto the block
        if block[-1] in chars:
            new = fp.read(4)
            if new:
                trail = ''
                block = block + new
                continue

        lines = block.replace(delimiter, RECORD_SEP).split(lineterminator)

        if block[-4:] == lineterminator:
            trail = ""
        else:
            trail = lines[-1]
            lines.pop()

        for line in lines:
            if len(line):
                yield line.split(RECORD_SEP)

        block = fp.read(blocksize)
    return


class DictReader(csv.DictReader):
    def __init__(self, f, fieldnames=None, restkey=None, restval=None,
                 dialect="bcp", *args, **kwds):
        self._fieldnames = fieldnames   # list of keys for the dict
        self.restkey = restkey          # key to catch long rows
        self.restval = restval          # default value for short rows
        self.reader = reader(f, dialect, *args, **kwds)
        self.dialect = dialect
        self.line_num = 0
