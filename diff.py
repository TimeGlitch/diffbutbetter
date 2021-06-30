

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

file1 = ""
with open(str(input("Starting file name: ")), 'r') as source1 :
  file1 = source1.read()
  print(file1)
file2 = ""
with open(str(input("Ending file name: ")), 'r') as source1 :
  file2 = source1.read()
  print(file2)

