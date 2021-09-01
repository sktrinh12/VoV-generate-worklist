import argparse
from os import remove, listdir, path

parser = argparse.ArgumentParser(description = 'Delete worklist (*.csv)')
parser.add_argument('-w', '--wl', metavar = 'WORKLIST', nargs = 1, type = str,
                    help = 'file path to worklist file', required = True)
parser.add_argument('-a', '--all', metavar = 'ALL_FILES', nargs = 1, type = int,
                    choices = [0], help = 'remove all files in directory passed to -w; pass a 0')
args = parser.parse_args()

if __name__ == "__main__":
    if args.all:
        if args.all[0] == 0:
            for fi in listdir(args.wl[0]):
                remove(path.join(args.wl[0], fi))
    else:
        remove(args.wl[0])

