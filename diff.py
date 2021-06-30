#patience diff by bram cohen

from __future__ import absolute_import

from bisect import bisect
import difflib


class MaxRecursionDepth(Exception):

    def __init__(self):
        super(MaxRecursionDepth, self).__init__('max recursion depth reached')


def unique_lcs_py(a, b):
    """Find the longest common subset for unique lines.

    :param a: An indexable object (such as string or list of strings)
    :param b: Another indexable object (such as string or list of strings)
    :return: A list of tuples, one for each line which is matched.
            [(line_in_a, line_in_b), ...]

    This only matches lines which are unique on both sides.
    This helps prevent common lines from over influencing match
    results.
    The longest common subset uses the Patience Sorting algorithm:
    http://en.wikipedia.org/wiki/Patience_sorting
    """
    # set index[line in a] = position of line in a unless
    # a is a duplicate, in which case it's set to None
    index = {}
    for i, line in enumerate(a):
        if line in index:
            index[line] = None
        else:
            index[line] = i
    # make btoa[i] = position of line i in a, unless
    # that line doesn't occur exactly once in both,
    # in which case it's set to None
    btoa = [None] * len(b)
    index2 = {}
    for pos, line in enumerate(b):
        next = index.get(line)
        if next is not None:
            if line in index2:
                # unset the previous mapping, which we now know to
                # be invalid because the line isn't unique
                btoa[index2[line]] = None
                del index[line]
            else:
                index2[line] = pos
                btoa[pos] = next
    # this is the Patience sorting algorithm
    # see http://en.wikipedia.org/wiki/Patience_sorting
    backpointers = [None] * len(b)
    stacks = []
    lasts = []
    k = 0
    for bpos, apos in enumerate(btoa):
        if apos is None:
            continue
        # as an optimization, check if the next line comes at the end,
        # because it usually does
        if stacks and stacks[-1] < apos:
            k = len(stacks)
        # as an optimization, check if the next line comes right after
        # the previous line, because usually it does
        elif stacks and stacks[k] < apos and (k == len(stacks) - 1 or
                                              stacks[k+1] > apos):
            k += 1
        else:
            k = bisect(stacks, apos)
        if k > 0:
            backpointers[bpos] = lasts[k-1]
        if k < len(stacks):
            stacks[k] = apos
            lasts[k] = bpos
        else:
            stacks.append(apos)
            lasts.append(bpos)
    if len(lasts) == 0:
        return []
    result = []
    k = lasts[-1]
    while k is not None:
        result.append((btoa[k], k))
        k = backpointers[k]
    result.reverse()
    return result


def recurse_matches_py(a, b, alo, blo, ahi, bhi, answer, maxrecursion):
    """Find all of the matching text in the lines of a and b.

    :param a: A sequence
    :param b: Another sequence
    :param alo: The start location of a to check, typically 0
    :param ahi: The start location of b to check, typically 0
    :param ahi: The maximum length of a to check, typically len(a)
    :param bhi: The maximum length of b to check, typically len(b)
    :param answer: The return array. Will be filled with tuples
                   indicating [(line_in_a, line_in_b)]
    :param maxrecursion: The maximum depth to recurse.
                         Must be a positive integer.
    :return: None, the return value is in the parameter answer, which
             should be a list

    """
    if maxrecursion < 0:
        # this will never happen normally, this check is to prevent DOS attacks
        raise MaxRecursionDepth()
    oldlength = len(answer)
    if alo == ahi or blo == bhi:
        return
    last_a_pos = alo-1
    last_b_pos = blo-1
    for apos, bpos in unique_lcs_py(a[alo:ahi], b[blo:bhi]):
        # recurse between lines which are unique in each file and match
        apos += alo
        bpos += blo
        # Most of the time, you will have a sequence of similar entries
        if last_a_pos+1 != apos or last_b_pos+1 != bpos:
            recurse_matches_py(
                a, b, last_a_pos+1, last_b_pos+1,
                apos, bpos, answer, maxrecursion - 1)
        last_a_pos = apos
        last_b_pos = bpos
        answer.append((apos, bpos))
    if len(answer) > oldlength:
        # find matches between the last match and the end
        recurse_matches_py(a, b, last_a_pos+1, last_b_pos+1,
                           ahi, bhi, answer, maxrecursion - 1)
    elif a[alo] == b[blo]:
        # find matching lines at the very beginning
        while alo < ahi and blo < bhi and a[alo] == b[blo]:
            answer.append((alo, blo))
            alo += 1
            blo += 1
        recurse_matches_py(a, b, alo, blo,
                           ahi, bhi, answer, maxrecursion - 1)
    elif a[ahi - 1] == b[bhi - 1]:
        # find matching lines at the very end
        nahi = ahi - 1
        nbhi = bhi - 1
        while nahi > alo and nbhi > blo and a[nahi - 1] == b[nbhi - 1]:
            nahi -= 1
            nbhi -= 1
        recurse_matches_py(a, b, last_a_pos+1, last_b_pos+1,
                           nahi, nbhi, answer, maxrecursion - 1)
        for i in range(ahi - nahi):
            answer.append((nahi + i, nbhi + i))


def _collapse_sequences(matches):
    """Find sequences of lines.

    Given a sequence of [(line_in_a, line_in_b),]
    find regions where they both increment at the same time
    """
    answer = []
    start_a = start_b = None
    length = 0
    for i_a, i_b in matches:
        if (start_a is not None
                and (i_a == start_a + length)
                and (i_b == start_b + length)):
            length += 1
        else:
            if start_a is not None:
                answer.append((start_a, start_b, length))
            start_a = i_a
            start_b = i_b
            length = 1

    if length != 0:
        answer.append((start_a, start_b, length))

    return answer


def _check_consistency(answer):
    # For consistency sake, make sure all matches are only increasing
    next_a = -1
    next_b = -1
    for (a, b, match_len) in answer:
        if a < next_a:
            raise ValueError('Non increasing matches for a')
        if b < next_b:
            raise ValueError('Non increasing matches for b')
        next_a = a + match_len
        next_b = b + match_len


class PatienceSequenceMatcher_py(difflib.SequenceMatcher):
    """Compare a pair of sequences using longest common subset."""

    _do_check_consistency = True

    def __init__(self, isjunk=None, a='', b=''):
        if isjunk is not None:
            raise NotImplementedError('Currently we do not support'
                                      ' isjunk for sequence matching')
        difflib.SequenceMatcher.__init__(self, isjunk, a, b)

    def get_matching_blocks(self):
        """Return list of triples describing matching subsequences.

        Each triple is of the form (i, j, n), and means that
        a[i:i+n] == b[j:j+n].  The triples are monotonically increasing in
        i and in j.

        The last triple is a dummy, (len(a), len(b), 0), and is the only
        triple with n==0.

        >>> s = PatienceSequenceMatcher(None, "abxcd", "abcd")
        >>> s.get_matching_blocks()
        [(0, 0, 2), (3, 2, 2), (5, 4, 0)]
        """
        # jam 20060525 This is the python 2.4.1 difflib get_matching_blocks
        # implementation which uses __helper. 2.4.3 got rid of helper for
        # doing it inline with a queue.
        # We should consider doing the same for recurse_matches

        if self.matching_blocks is not None:
            return self.matching_blocks

        matches = []
        recurse_matches_py(self.a, self.b, 0, 0,
                           len(self.a), len(self.b), matches, 10)
        # Matches now has individual line pairs of
        # line A matches line B, at the given offsets
        self.matching_blocks = _collapse_sequences(matches)
        self.matching_blocks.append((len(self.a), len(self.b), 0))
        if PatienceSequenceMatcher_py._do_check_consistency:
            if __debug__:
                _check_consistency(self.matching_blocks)

        return self.matching_blocks


def lcssimple(text1,  text2):
    if text1 == "" or text2 == "":
        return ""
    elif text1[-1] == text2[-1]:
        return lcssimple(text1[0: -1], text2[0: -1]) + text1[-1]
    else:
        bit1 = lcssimple(text1[0: -1], text2)
        bit2 = lcssimple(text1, text2[0: -1])
        if len(bit1) < len (bit2) :
            return bit2
        else:
            return bit1

#  from https://blog.robertelder.org/diff-algorithm/
#  Returns a minimal list of differences between 2 lists e and f
#  requring O(min(len(e),len(f))) space and O(min(len(e),len(f)) * D)
#  worst-case execution time where D is the number of differences.
def minimaldiff(e, f, i=0, j=0):
  #  Documented at http://blog.robertelder.org/diff-algorithm/
  N,M,L,Z = len(e),len(f),len(e)+len(f),2*min(len(e),len(f))+2
  if N > 0 and M > 0:
    w,g,p = N-M,[0]*Z,[0]*Z
    for h in range(0, (L//2+(L%2!=0))+1):
      for r in range(0, 2):
        c,d,o,m = (g,p,1,1) if r==0 else (p,g,0,-1)
        for k in range(-(h-2*max(0,h-M)), h-2*max(0,h-N)+1, 2):
          a = c[(k+1)%Z] if (k==-h or k!=h and c[(k-1)%Z]<c[(k+1)%Z]) else c[(k-1)%Z]+1
          b = a-k
          s,t = a,b
          while a<N and b<M and e[(1-o)*N+m*a+(o-1)]==f[(1-o)*M+m*b+(o-1)]:
            a,b = a+1,b+1
          c[k%Z],z=a,-(k-w)
          if L%2==o and z>=-(h-o) and z<=h-o and c[k%Z]+d[z%Z] >= N:
            D,x,y,u,v = (2*h-1,s,t,a,b) if o==1 else (2*h,N-a,M-b,N-s,M-t)
            if D > 1 or (x != u and y != v):
              return diff(e[0:x],f[0:y],i,j)+diff(e[u:N],f[v:M],i+u,j+v)
            elif M > N:
              return diff([],f[N:M],i+N,j+N)
            elif M < N:
              return diff(e[M:N],[],i+M,j+M)
            else:
              return []
  elif N > 0: #  Modify the return statements below if you want a different edit script format
    return [{"operation": "delete", "position_old": i+n} for n in range(0,N)]
  else:
    return [{"operation": "insert", "position_old": i,"position_new":j+n} for n in range(0,M)]

def patiencediff(text1, text2):
  print("WIP")

def testing():
    print("yep")

def equals(c1, c2):

    return c1 == c2
#print(lcssimple("yeehaw", "yeea"))
file1name = str(input("Starting file name: "))
file2name =str(input("Ending file name: "))


file1 = ""
file2 = ""
print("---file1---")
with open(file1name, 'r') as source :
  file1 = source.read()
  print(file1)
print("---file2---")
with open(file2name, 'r') as source :
  file2 = source.read()
  print(file2)

output = "testing testing"
with open(file1name + " and " + file2name + " diff", 'x') as outfile :
  outfile.write(output)
