"""Read-only reflected data inspection for this Steam Arkham Knight build."""
import sys,struct,re
from functools import lru_cache
from ue3_inspect import ProcessMemory
pm=ProcessMemory(int(sys.argv[1]));base=int(sys.argv[2],0)
def q(a):
    d=pm.read(a,8);return struct.unpack('<Q',d)[0] if len(d)==8 else 0
nd=q(base+0x3a208b8);nc=pm.u32(base+0x3a208c0)
np=struct.unpack('<%dQ'%nc,pm.read(nd,nc*8))
od=q(base+0x316c510);oc=pm.u32(base+0x316c518)
ob=pm.read(od,oc*16);op=[struct.unpack_from('<Q',ob,i*16)[0] for i in range(oc)]
@lru_cache(None)
def name(i):
    if i is None or i>=nc:return '?'
    e=np[i];flags=pm.u32(e) or 0;s=q(e+12) if flags&2 else e+12;raw=pm.read(s,192)
    return raw.decode('utf-16le',errors='ignore').split('\0')[0] if flags&1 else raw.split(b'\0')[0].decode('latin1')
@lru_cache(None)
def oname(o):return name(pm.u32(o+0x3c)) if o else '?'
@lru_cache(None)
def cn(o):return oname(q(o+0x44))
def path(o):
    parts=[]
    for _ in range(10):
        if not o:break
        parts.append(oname(o));o=q(o+0x34)
    return '.'.join(reversed(parts))
mode=sys.argv[3];pat=re.compile(sys.argv[4],re.I);owner=re.compile(sys.argv[5] if len(sys.argv)>5 else '.*',re.I)
if mode in ('dynamic','stats'):
    od=q(base+0x3119d90);oc=pm.u32(base+0x3119d98);ob=pm.read(od,oc*36);op=[struct.unpack_from('<Q',ob,i*36)[0] for i in range(oc)]
print('REGISTRY',nc,oc,'FIRST',[(hex(o),oname(o),cn(o)) for o in op[:4]])
if mode=='stats':
    from collections import Counter
    print(Counter(cn(o) for o in op if o).most_common(30))
if mode=='fields':
    seen=set()
    for obj in op:
        cls=q(obj+0x44) if obj else 0
        if not cls or cls in seen or not owner.search(oname(cls)):continue
        seen.add(cls);print('CLASS',hex(cls),oname(cls),pm.read(cls+0x54,96).hex())
        f=q(cls+0x64);walk=set()
        while f and f not in walk:
            walk.add(f)
            if pat.search(oname(f)) and cn(f).endswith('Property'):
                packed=pm.u32(f+0x68) or 0
                print('FIELD',hex(f),cn(f),path(f),'OFFSET',hex(packed>>16),'SIZE',packed&65535,'MASK',hex(pm.u32(f+0xac) or 0))
            f=q(f+0x54)
if mode=='discover':
    raw=bytearray(0x4398000)
    for j in range(0,len(raw),0x10000):
        d=pm.read(base+j,min(0x10000,len(raw)-j));raw[j:j+len(d)]=d
    for off in range(0,len(raw)-16,4):
        ptr,count,maximum=struct.unpack_from('<Qii',raw,off)
        if not (1000<count<=maximum<2000000 and 0x10000<ptr<0x7fffffffffff):continue
        for stride in (8,16,24,36):
            dat=pm.read(ptr,stride*4)
            if len(dat)!=stride*4:continue
            ps=[struct.unpack_from('<Q',dat,k*stride)[0] for k in range(4)]
            valid=[(hex(p),oname(p),cn(p)) for p in ps if 0x10000<p<0x7fffffffffff]
            if len(valid)>=3 and all(n not in ('?','') and c not in ('?','') for p,n,c in valid):print('ARRAY',hex(off),count,'stride',stride,valid)
for o in op:
    if not o:continue
    n,c=oname(o),cn(o)
    if mode in ('instances','dynamic') and pat.search(c):print(hex(o),c,path(o),'header',pm.read(o,0x80).hex())
    if mode=='properties' and c.endswith('Property') and pat.search(n) and owner.search(oname(q(o+0x34))):print(hex(o),c,path(o),'raw',pm.read(o+0x54,0x70).hex())
    if mode=='classes' and c=='Class' and pat.search(n):print(hex(o),n,'raw',pm.read(o+0x50,0x50).hex())
pm.close()
