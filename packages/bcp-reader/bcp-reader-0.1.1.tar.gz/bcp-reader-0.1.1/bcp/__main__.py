import sys
import argparse
import csv
import io
import bcp


def main():
    parser = argparse.ArgumentParser(
        description='Convert a BCP file into a CSV'
    )
    parser.add_argument('infile', help="file to convert")
    parser.add_argument(
        '--encoding',
        '-e',
        default='latin1',
        help='Encoding of the file to convert'
    )
    parser.add_argument(
        '--blocksize',
        '-b',
        default=bcp.BLOCKSIZE,
        type=int,
        help='Blocksize for parsing'
    )
    args = parser.parse_args()
    writer = csv.writer(sys.stdout)
    with open(args.infile, 'rb') as a:
        writer.writerows(
            bcp.reader(
                io.TextIOWrapper(a, encoding=args.encoding),
                blocksize=256
            )
        )


if __name__ == '__main__':
    main()
