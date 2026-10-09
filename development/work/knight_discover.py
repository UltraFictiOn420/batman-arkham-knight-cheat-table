"""Read-only x64 UE3 registry discovery, using the live module base."""
import sys,struct
from ue3_inspect import ProcessMemory
pm=ProcessMemory(int(sys.argv[1]))
base=int(sys.argv[2],0);size=int(sys.argv[3],0)
raw=bytearray(size)
for off in range(0,size,0x10000):
    data=pm.read(base+off,min(0x10000,size-off))
    raw[off:off+len(data)]=data
print('MODULE',hex(base),hex(size),flush=True)
for off in range(0,size-16,4):
    data,count,maximum=struct.unpack_from('<Qii',raw,off)
    if not (100<count<=maximum<2000000 and 0x10000<data<0x7fffffffffff):continue
    sample=pm.read(data,64)
    if len(sample)!=64:continue
    ptrs=struct.unpack('<8Q',sample)
    if not all(0x10000<p<0x7fffffffffff for p in ptrs[:2]):continue
    print('CANDIDATE',hex(off),count,maximum,[hex(p) for p in ptrs[:4]],flush=True)
    for stringoff in (8,12,16,24):
        first=pm.read(ptrs[0]+stringoff,10)
        if first.startswith(b'None\0') or first==b'N\0o\0n\0e\0\0\0':
            print('NAMES',hex(base+off),'RVA',hex(off),'DATA',hex(data),'COUNT',count,'STR',stringoff,'FIRST',[(hex(p),pm.read(p,48).hex()) for p in ptrs[:4]],flush=True)
    headers=[pm.read(p,80) for p in ptrs[:6]]
    if all(len(h)==80 and base<=struct.unpack_from('<Q',h)[0]<base+size for h in headers):
        print('OBJECTS',hex(base+off),'RVA',hex(off),'DATA',hex(data),'COUNT',count,'FIRST',[(hex(p),h.hex()) for p,h in zip(ptrs,headers)][:3],flush=True)
pm.close()
