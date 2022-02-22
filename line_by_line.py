import argparse
from itertools import zip_longest 
import os
import re
import difflib
import pprint
import readchar

def remove_punctuation(s: str):
    return re.sub('[,!?".„():;]', ' ', s)

def normalize_spacing(s: str):
    return re.sub('[ \t\n]+', ' ', s)

parser = argparse.ArgumentParser(description='')
parser.add_argument('--left', type=str)
parser.add_argument('--right', type=str)
args = parser.parse_args()
print(f'left {args.left}')
print(f'right {args.right}')

with open(args.left) as f:
    left = [x.strip() for x in f]

with open(args.right) as f:
    right = [x for x in f]
    right = [remove_punctuation(x) for x in right]
    right = [normalize_spacing(x) for x in right]
    right = [x.strip() for x in right]

if len(left) != len(right):
    print(f'left {len(left)} lines, right {len(right)} lines')
    os.exit(1)

for i in range(len(left)):
    while True:
        print(left[i])
        user = input()
        # user = left[i]
        t = normalize_spacing(remove_punctuation(user)).strip()
        a = t.split(' ')
        d = difflib.Differ()
        # print(right[i])
        # print(t)
        diff = [x for x in d.compare(right[i].split(' '), t.split(' '))]
        # pprint.pprint(diff)
        match_from = []
        match_to = []
        for d in diff:
            x = d[2:]
            if d.startswith('- '):
                match_from.append(x)
            if d.startswith('+ '):
                match_to.append(x)
            if d.startswith('  '):
                while len(match_from) < len(match_to):
                    match_from.append('')
                while len(match_from) > len(match_to):
                    match_to.append('')
                match_from.append(x)
                match_to.append(x)
        n = max(len(match_to), len(match_from))
        z = zip_longest(match_from, match_to, fillvalue='')
        out_from = []
        out_to = []
        difference = False
        for (x, y) in z:  
            difference = difference or (x != y)
            # print(x, y)
            n = max(len(x), len(y))
            out_from.append(x.ljust(n))
            out_to.append(y.ljust(n))
        if not difference:
            break
        print(' '.join(out_from))
        print(' '.join(out_to))
        c = readchar.readchar()
        if c == 'n':
            break
    # for d in diff: 
    #     print(d)
    # print(right[i])