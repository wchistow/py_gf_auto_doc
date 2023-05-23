import argparse
import sys

from .doc_gen import generate_doc

parser = argparse.ArgumentParser()
parser.add_argument('--dir', '-d', type=str)
parser.add_argument('--out_dir', '-o', type=str)
args = parser.parse_args(sys.argv[1:])
generate_doc(vars(args)['dir'], vars(args)['out_dir'])
