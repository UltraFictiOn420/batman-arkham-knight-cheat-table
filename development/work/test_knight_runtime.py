"""Live-read validation with CE Lua APIs mocked; all writes are overlay-only."""
import sys,struct,time
from pathlib import Path
from lupa import LuaRuntime
from ue3_inspect import ProcessMemory
pid=int(sys.argv[1]);base=int(sys.argv[2],0);pm=ProcessMemory(pid)
lua=LuaRuntime(unpack_returned_tuples=True);g=lua.globals();overlay={};writes=[];current=[pid]
def raw(a,n):
    a=int(a);d=pm.read(a,n)
    if len(d)!=n:d=bytes(n)
    return bytes(overlay.get(a+k,d[k]) for k in range(n))
def ri(a):return struct.unpack('<I',raw(a,4))[0]
def rq(a):return struct.unpack('<Q',raw(a,8))[0]
def rf(a):return struct.unpack('<f',raw(a,4))[0]
def write(a,v,kind):
    a=int(a);b=struct.pack('<I' if kind=='int' else '<f',v)
    overlay.update({a+k:c for k,c in enumerate(b)});writes.append((a,v,kind));return True
def string(a,n,wide=False):
    b=raw(a,n*2 if wide else n)
    return b.decode('utf-16le',errors='ignore').split('\0')[0] if wide else b.split(b'\0')[0].decode('latin1')
def ws(a,s):
    if isinstance(s,str):s=s.encode('latin1')
    overlay.update({int(a)+k:c for k,c in enumerate(s)});writes.append((int(a),len(s),'string'));return True
g.openProcess=lambda _:None;g.getAddressSafe=lambda _:base;g.getOpenedProcessID=lambda:current[0]
g.readInteger=ri;g.readQword=rq;g.readFloat=rf;g.readString=string;g.readBytes=lambda a:raw(a,1)[0]
g.writeInteger=lambda a,v:write(a,v,'int');g.writeFloat=lambda a,v:write(a,v,'float');g.writeString=ws
g.allocateMemory=lambda _:0x7FFE00000000;g.deAlloc=lambda _:None;g.registerSymbol=lambda *a:None;g.unregisterSymbol=lambda _:None
g.playSound=lambda _:None;g.createTimer=lambda *a:lua.table_from({'destroy':lambda *a:None})
start=time.monotonic();lua.execute((Path(__file__).parent/'arkham_knight_runtime.lua').read_text(encoding='utf-8'));c=g.AK;p=c.player
assert p and c.bind();assert all(a>=0x7FFE00000000 for a,_,_ in writes)
print('INIT',round(time.monotonic()-start,3),'PLAYER',hex(p),'HP',ri(p+0x478),ri(p+0x47c),'ENEMIES',len(c.enemies),'GADGETS',len(c.gadgets),flush=True)
write(p+0x478,5,'int');c.setFlag('health',True);assert ri(p+0x478)==ri(p+0x47c)
c.setFlag('health',False);write(p+0x478,5,'int');c.apply();assert ri(p+0x478)==5
c.flags.health=True;write(p+0x478,0,'int');c.apply();assert ri(p+0x478)==0;c.flags.health=False;write(p+0x478,100,'int')
print('HEALTH refill / off / no resurrection verified',flush=True)
for _,x in c.enemies.items():assert not c.isA(x.o,'RPawnPlayer')
if len(c.enemies):
    e=c.enemies[1].o;m=ri(e+0x47c);assert m>0
    write(e+0x478,m,'int');c.setFlag('superDamage',True);assert ri(e+0x478)==max(1,m//10)
    c.setFlag('superDamage',False);write(e+0x478,m,'int');c.apply();assert ri(e+0x478)==m
    c.setFlag('oneHit',True);assert ri(e+0x478)==1;c.setFlag('oneHit',False)
    print('ENEMY health cap / off / one hit verified',flush=True)
gr=[x.o for _,x in c.gadgets.items() if c.isA(x.o,'RGrappleGun')];ba=[x.o for _,x in c.gadgets.items() if c.isA(x.o,'RBatarang')]
print('GRAPPLE',list(map(hex,gr)),'BATARANG',list(map(hex,ba)),flush=True);assert gr and ba
initial={o:{off:rf(o+off) for off in ([0x81c,0x824,0x9fc,0xa18,0xcb4,0xe00] if o in gr else [0x8cc,0x8d0])} for o in gr+ba}
for o,ofs in initial.items():
    for off in ofs:assert c.field(o,{0x81c:'MaxGrappleHorizontalDistance',0x824:'MaxHorizontalDistanceForAimedGrapple',0x9fc:'MaxOWSwingRange',0xa18:'MaxHorizontalRange',0xcb4:'AerialGrappleRange',0xe00:'ChainGrappleRange',0x8cc:'BatarangRange',0x8d0:'AutoTargetRange'}[off])[0]==off
c.setFlag('grappleRange',True);c.setFlag('batarangRange',True)
for o,ofs in initial.items():
    for off,v in ofs.items():assert rf(o+off)==(max(v,50000) if v>0 else v)
c.setFlag('grappleRange',False);c.setFlag('batarangRange',False)
for o,ofs in initial.items():
    for off,v in ofs.items():assert rf(o+off)==v
print('RANGE metadata / changes / restoration verified',flush=True)
assert c.save();v=c.saved;ph=raw(p+0x11b,1)[0];print('PHYSICS',ph,flush=True)
for n in [1,2,5,10]:
    assert c.up(n);assert rf(p+0xcc)>v.z;assert c.undoTeleport();assert abs(rf(p+0xcc)-v.z)<0.05
assert c.teleport();print('SAVE / TELEPORT / UNDO / UP overlay tests verified',flush=True)
before=len(writes);current[0]=pid+1;c.apply();assert len(writes)==before;current[0]=pid
c.shutdown();pm.close();print('All game writes simulated; live game unchanged.',flush=True)
