import os,urllib.request,json
N=(-19,-8,-21,-12,19,8,21,12)
G=(-11,-10,-9,-1,1,9,10,11)
D=(-11,-9,9,11)
R=(-10,-1,1,10)
V={'P':100,'N':320,'B':330,'R':500,'Q':900,'K':0}
I=' '*20+' rnbqkbnr '+' pppppppp '+' ........ '*4+' PPPPPPPP '+' RNBQKBNR '+' '*20
def F(b):return ''.join(b[i:i+10] for i in range(110,-1,-10))
def fi(i):return 112-i+2*((i-21)%10)
def pst(p,i):
 f=(i-21)%10;k=7-(i-21)//10;c=7-abs(2*f-7)-abs(2*k-7)
 return 10*k if p=='P' else 4*c if p=='N' else 3*c if p=='B' else 2*c if p=='Q' else 10*(k==6) if p=='R' else 8*(k<2)-2*c
def atk(b,s,w):
 o=1 if w else -1;q='P' if w else 'p'
 if b[s+9*o]==q or b[s+11*o]==q:return 1
 for ds,q in((N,'N'),(G,'K')):
  for d in ds:
   if b[s+d]==(q if w else q.lower()):return 1
 for d in D+R:
  j=s+d
  while b[j]=='.':j+=d
  c=b[j]
  if c==('Q' if w else 'q') or d in D and c==('B' if w else 'b') or d in R and c==('R' if w else 'r'):return 1
 return 0
def gen(b,e,cr):
 m=[]
 for i,p in enumerate(b):
  if p<'A' or p>'Z':continue
  if p=='P':
   j=i-10
   if b[j]=='.':
    m.append((i,j))
    if 80<i<89 and b[i-20]=='.':m.append((i,i-20))
   for j in(i-9,i-11):
    if b[j] in 'pnbrq' or j==e and b[j]=='.':m.append((i,j))
  elif p in 'NK':
   for d in N if p=='N' else G:
    j=i+d
    if b[j]=='.' or b[j] in 'pnbrq':m.append((i,j))
  else:
   for d in D if p=='B' else R if p=='R' else D+R:
    j=i+d
    while b[j]=='.':
     m.append((i,j));j+=d
    if b[j] in 'pnbrq':m.append((i,j))
 if cr&1 and b[96:98]=='..' and b[98]=='R' and not any(atk(b,x,0)for x in(95,96,97)):m.append((95,97))
 if cr&2 and b[92:95]=='...' and b[91]=='R' and not any(atk(b,x,0)for x in(95,94,93)):m.append((95,93))
 return m
def mk(b,s,e,cr,m,q='Q'):
 i,j=m;p=b[i];n=b[:i]+'.'+b[i+1:];c=n[j];d=-pst(p,i)
 if p=='P' and j==e:n=n[:j+10]+'.'+n[j+11:];d+=100+pst('P',fi(j+10));c='p'
 elif c in 'pnbrq':d+=V[c.upper()]+pst(c.upper(),fi(j))
 q=q if p=='P' and j<29 else p;d+=pst(q,j);n=n[:j]+q+n[j+1:]
 if p=='K' and abs(j-i)==2:
  rf=j+1 if j>i else j-2;rt=j-1 if j>i else j+1
  n=n[:rf]+'.'+n[rf+1:];n=n[:rt]+'R'+n[rt+1:];d+=-pst('R',rf)+pst('R',rt)
 a=cr&3;o=cr>>2
 if p=='K':a=0
 elif p=='R':
  if i==98:a&=2
  elif i==91:a&=1
 if j==28 and c=='r':o&=2
 elif j==21 and c=='r':o&=1
 ne=i-10 if p=='P' and j==i-20 else 0
 return F(n).swapcase(),-(s+d),fi(ne) if ne else 0,o|(a<<2)
ND=0
BU=200000
class A(Exception):pass
def neg(b,s,e,cr,d,y):
 global ND
 ND+=1
 if ND>BU:raise A
 if d==0:return s
 bs=-999999
 for m in gen(b,e,cr):
  r,t,f,w=mk(b,s,e,cr,m)
  if atk(r,r.index('k'),1):continue
  v=-neg(r,t,f,w,d-1,y+1)
  if v>bs:bs=v
 if bs==-999999:return -100000+y if atk(b,b.index('K'),0) else 0
 return bs
def sqn(i):return 'abcdefgh'[(i-21)%10]+str(8-(i-21)//10)
def uci(b,m,blk):
 i,j=m
 if blk:i,j=fi(i),fi(j)
 return sqn(i)+sqn(j)+('q' if b[m[0]]=='P' and m[1]<29 else '')
def idx(u):return 91+'abcdefgh'.index(u[0])-10*(int(u[1])-1)
def replay(ms):
 b=I;s=0;e=0;cr=15;h={I+'|0|15'}
 for k,u in enumerate(ms):
  i=idx(u[:2]);j=idx(u[2:4]);q=u[4].upper() if len(u)>4 else 'Q'
  if k%2:i,j=fi(i),fi(j)
  b,s,e,cr=mk(b,s,e,cr,(i,j),q)
  h.add(b+'|'+str(e)+'|'+str(cr))
 return b,s,e,cr,h
def post(u,o):
 q=urllib.request.Request(u,data=json.dumps(o).encode(),headers={'Content-Type':'application/json'})
 return json.loads(urllib.request.urlopen(q).read())
def ranked(g):
 global ND
 b,s,e,cr,h=replay(g['moves']);blk=g['colour']=='black';lg=set(g['legal_moves']);cs=[];ND=0
 try:
  for m in gen(b,e,cr):
   r,t,f,w=mk(b,s,e,cr,m)
   if atk(r,r.index('k'),1):continue
   u=uci(b,m,blk)
   if u not in lg:continue
   cs.append((neg(r,t,f,w,2,1),u))
 except A:pass
 cs.sort()
 return [u for v,u in cs] or sorted(lg)
def main():
 U=os.environ['MAKEFUN_ENV_URL']
 g=post(U+'/game',{})
 while g.get('status')!='done':
  if g.get('status')=='your_move':
   try:cs=ranked(g)
   except Exception:cs=sorted(g['legal_moves'])
   ok=0
   for c in cs:
    try:g=post(U+'/move',{'game':g['game'],'move':c});ok=1;break
    except Exception:continue
   if not ok:g=post(U+'/game',{})
  else:g=post(U+'/game',{})
if __name__=='__main__':main()