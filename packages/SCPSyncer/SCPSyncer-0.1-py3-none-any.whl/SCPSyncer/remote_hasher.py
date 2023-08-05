#!/usr/bin/env python3
import argparse
import os
import pickle
import hashlib

hashers = {'sha1':   hashlib.sha1,
           'sha256': hashlib.sha256,
           'sha512': hashlib.sha512,
           'md5':    hashlib.md5}

try:
    with open(os.path.join(os.path.splitext(__file__)[0], '.pkl')) as f:
        filters = pickle.load(f)
except FileNotFoundError:
    filters = {}

parser = argparse.ArgumentParser(description='Calculate hashes of files recursively')
parser.add_argument('path', default='./', nargs='?', help='The path to search in')
parser.add_argument('output', default='hashes.pkl', nargs='?', help='Output file (pickle)')
parser.add_argument('--hash', choices=hashers.keys(), default='sha1')
args = parser.parse_args()

hasher_class = hashers[args.hash]
hashes = {}
for root, dirs, files in os.walk(args.path):
    # print(root)
    for file in files:
        fn = os.path.join(root, file)
        rel_fn = os.path.relpath(fn, args.path)
        hasher = hasher_class()
        with open(fn, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        hashes[rel_fn] = hasher.hexdigest()

with open(args.output, 'wb') as f:
    pickle.dump(hashes, f)
