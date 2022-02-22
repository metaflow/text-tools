import argparse
from itertools import zip_longest 
import re
import difflib
import sys
# import pprint
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

with open(args.left, encoding='utf8') as f:
    left = [x.strip() for x in f]

with open(args.right, encoding='utf8') as f:
    right = [x for x in f]
    right = [remove_punctuation(x) for x in right]
    right = [normalize_spacing(x) for x in right]
    right = [x.strip() for x in right]

if len(left) != len(right):
    print(f'left {len(left)} lines, right {len(right)} lines')
    exit(1)

for i in range(len(left)):
    while True:
        print(left[i])
        user = input()
        # user = left[i]
        t = normalize_spacing(remove_punctuation(user)).strip()
        a = t.split(' ')
        # differ = difflib.Differ()
        # print(right[i])
        # print(t)
        diff = [x for x in difflib.Differ().compare(right[i].split(' '), t.split(' '))]
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
        out_hightlight = []
        difference = False
        for (x, y) in z:
            # print(x, y)
            n = max(len(x), len(y))
            out_from.append(x.ljust(n))
            out_to.append(y.ljust(n))
            if x == y:
                out_hightlight.append(' ' * n)
            else:
                out_hightlight.append('^' * n)
                difference = True
        if not difference:
            break
        print(' '.join(out_from))
        print(' '.join(out_to))
        print(' '.join(out_hightlight))
        c = readchar.readchar().decode('utf8')
        # print(f'readchar "{c}"')
        if c == 'n' or c == 'c':
            break
        delete = 5
        sys.stdout.write(f'\x1B[{delete}F')
        for i in range(delete):
            sys.stdout.write('\x1b[2K')
            sys.stdout.write('\n')
    # for d in diff: 
    #     print(d)
    # print(right[i])