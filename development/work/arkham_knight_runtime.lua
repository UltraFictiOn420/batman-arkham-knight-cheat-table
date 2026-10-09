-- Original Knight v1: x64 reflected objects, no console or executable patches.
if AK and AK.shutdown then AK.shutdown() end
AK=nil
openProcess('BatmanAK.exe')
local base=getAddressSafe('BatmanAK.exe')
if not base then error('Start Batman Arkham Knight and load into single-player gameplay.') end
local C={pid=getOpenedProcessID(),names={},flags={},originals={},tick=0,enemies={},gadgets={}}
local function read(fn,a) if a and a>0x10000 then local ok,v=pcall(fn,a);if ok then return v end end end
local function ri(a) return read(readInteger,a) end
local function rq(a) return read(readQword,a) end
local function rf(a) return read(readFloat,a) end
local function finite(v) return v and v==v and math.abs(v)<10000000 end
local function ptr(v) return v and v>0x10000 and v<0x7FFFFFFFFFFF end
C.gnames=base+0x3A208B8
function C.name(i)
  if not i or i<0 then return end
  if C.names[i] then return C.names[i] end
  local n,d=ri(C.gnames+8),rq(C.gnames)
  if not n or n<10000 or n>500000 or i>=n or not ptr(d) then return end
  local e=rq(d+i*8);if not ptr(e) then return end
  local f=ri(e);if not f then return end
  local s=f%4>=2 and rq(e+12) or e+12;if not ptr(s) then return end
  local ok,v=pcall(readString,s,192,f%2==1)
  if ok and v and v~='' then C.names[i]=v;return v end
end
function C.oname(o) return ptr(o) and C.name(ri(o+0x3C)) or nil end
function C.class(o) return ptr(o) and rq(o+0x44) or nil end
function C.isA(o,n)
  local c=C.class(o);local seen={}
  for _=1,60 do
    if not ptr(c) or seen[c] then return false end
    seen[c]=true;if C.oname(c)==n then return true end;c=rq(c+0x5C)
  end
  return false
end
function C.live(o,n)
  if getOpenedProcessID()~=C.pid or not C.isA(o,n) then return false end
  local name=C.oname(o)
  return name and name:sub(1,9)~='Default__'
end
local function identity(o)
  return {class=C.class(o),name=ri(o+0x3C),number=ri(o+0x40),outer=rq(o+0x34)}
end
local function same(o,x)
  return x and getOpenedProcessID()==C.pid and C.class(o)==x.class and ri(o+0x3C)==x.name and ri(o+0x40)==x.number and rq(o+0x34)==x.outer
end
function C.field(o,n)
  local c=C.class(o);local visited={}
  for _=1,60 do
    if not ptr(c) or visited[c] then return end;visited[c]=true
    local f=rq(c+0x64);local seen={}
    for _=1,3000 do
      if not ptr(f) or seen[f] then break end;seen[f]=true
      if C.oname(f)==n then
        local cn=C.oname(C.class(f));local v=ri(f+0x68)
        if cn and cn:sub(-8)=='Property' and v then return math.floor(v/65536),v%65536 end
      end
      f=rq(f+0x54)
    end
    c=rq(c+0x5C)
  end
end
function C.bind()
  if getOpenedProcessID()~=C.pid then C.player=nil;return false end
  local e
  for _,off in ipairs({0x3728ED4,0x317D3A0,0x311F508}) do
    local x=rq(base+off);if C.live(x,'GameEngine') then e=x;break end
  end
  if not e then C.player=nil;return false end
  local a,n=rq(e+0x84C),ri(e+0x854)
  if not ptr(a) or not n or n<1 or n>4 then C.player=nil;return false end
  local lp=rq(a);local pc=ptr(lp) and rq(lp+0x5C);local p=ptr(pc) and rq(pc+0x29C)
  if not C.live(pc,'PlayerController') or not C.live(p,'RPawnPlayer') then C.player=nil;return false end
  local w=rq(p+0x9C)
  if not C.live(w,'WorldInfo') then C.player=nil;return false end
  local h,m=ri(p+0x478),ri(p+0x47C)
  if not h or not m or h<0 or m<1 or m>100000 then C.player=nil;return false end
  C.player=p;C.controller=pc;C.world=w;return true
end
local function remember(flag,o,off)
  local a=o+off;C.originals[flag]=C.originals[flag] or {};local map=C.originals[flag]
  if map[a] and same(o,map[a].id) then return map[a].v end
  local v=rf(a);if not finite(v) then return end
  map[a]={owner=o,id=identity(o),v=v};return v
end
function C.restore(flag)
  for a,x in pairs(C.originals[flag] or {}) do
    if same(x.owner,x.id) and C.live(x.owner,'RInventoryGadget') then writeFloat(a,x.v) end
  end
  C.originals[flag]=nil
end
function C.scan()
  C.enemies={};C.gadgets={};if not C.bind() then return end
  local p=rq(C.world+0x5C4);local seen={}
  for _=1,2048 do
    if not ptr(p) or seen[p] then break end;seen[p]=true
    if C.live(p,'Pawn') and p~=C.player and not C.isA(p,'RPawnPlayer') then
      local name=C.oname(C.class(p)) or ''
      if (C.isA(p,'RBMPawnAI') or C.isA(p,'RPawnVillain')) and not name:lower():find('boss') then
        C.enemies[#C.enemies+1]={o=p,id=identity(p)}
      end
    end
    p=rq(p+0x2C4)
  end
  local im=rq(C.player+0x33C)
  if not C.live(im,'InventoryManager') then return end
  local g=rq(im+0x29C);seen={}
  for _=1,128 do
    if not ptr(g) or seen[g] then break end;seen[g]=true
    if C.live(g,'RInventoryGadget') then C.gadgets[#C.gadgets+1]={o=g,id=identity(g)} end
    g=rq(g+0x29C)
  end
end
function C.apply()
  if not C.bind() then return end
  if C.flags.health then
    local h,m=ri(C.player+0x478),ri(C.player+0x47C)
    if h and m and h>0 and h<m then writeInteger(C.player+0x478,m) end
  end
  if C.flags.superDamage or C.flags.oneHit then
    for _,x in ipairs(C.enemies) do
      local o=x.o
      if same(o,x.id) and C.live(o,'Pawn') and rq(o+0x9C)==C.world and not C.isA(o,'RPawnPlayer') then
        local h,m=ri(o+0x478),ri(o+0x47C)
        if h and m and h>0 and m>0 and m<100000 then
          local target=C.flags.oneHit and 1 or math.max(1,math.floor(m/10))
          if h>target then writeInteger(o+0x478,target) end
        end
      end
    end
  end
  for _,x in ipairs(C.gadgets) do
    if same(x.o,x.id) and C.live(x.o,'RInventoryGadget') then
      local o=x.o
      if C.flags.grappleRange and C.isA(o,'RGrappleGun') then
        for _,off in ipairs({0x81C,0x824,0x9FC,0xA18,0xCB4,0xE00}) do
          local v=remember('grappleRange',o,off);if v and v>0 then writeFloat(o+off,math.max(v,50000)) end
        end
      end
      if C.flags.batarangRange and C.isA(o,'RBatarang') then
        for _,off in ipairs({0x8CC,0x8D0}) do
          local v=remember('batarangRange',o,off);if v and v>0 then writeFloat(o+off,math.max(v,50000)) end
        end
      end
    end
  end
end
function C.setFlag(n,v)
  if v and not C.bind() then error('No active on-foot player. Load gameplay and enable again.') end
  if v and n=='superDamage' then C.flags.oneHit=false end
  if v and n=='oneHit' then C.flags.superDamage=false end
  C.flags[n]=v
  if v then C.scan();C.apply() else C.restore(n) end
end
local function position()
  if not C.bind() then return end
  local h=ri(C.player+0x478);if not h or h<=0 then return end
  local v={x=rf(C.player+0xC4),y=rf(C.player+0xC8),z=rf(C.player+0xCC),owner=C.player,world=C.world,id=identity(C.player)}
  if finite(v.x) and finite(v.y) and finite(v.z) then return v end
end
local function move(v)
  if not v or not C.bind() or C.player~=v.owner or C.world~=v.world or not same(v.owner,v.id) then return false end
  if not finite(v.x) or not finite(v.y) or not finite(v.z) then return false end
  -- Restrict to on-foot walking/falling; no cutscenes, vehicles, ledge or grapple transitions.
  local ph=read(readBytes,C.player+0x11B)
  if ph~=1 and ph~=2 then return false end
  writeFloat(C.player+0xC4,v.x);writeFloat(C.player+0xC8,v.y);writeFloat(C.player+0xCC,v.z)
  for _,off in ipairs({0x1BC,0x1C0,0x1C4}) do writeFloat(C.player+off,0) end
  return true
end
function C.save() local p=position();if p then C.saved=p;return true end;return false end
function C.teleport() local p=position();if p and move(C.saved) then C.undo=p;return true end;return false end
function C.undoTeleport() local p=position();if p and move(C.undo) then C.undo=p;return true end;return false end
function C.up(n)
  local p=position();if not p then return false end
  local cyl=rq(C.player+0x384);local half=ptr(cyl) and rf(cyl+0x21C)
  if not half or half<10 or half>300 then return false end
  local target={};for k,v in pairs(p) do target[k]=v end;target.z=target.z+half*2*n
  if move(target) then C.undo=p;return true end;return false
end
function C.action(memrec,fn)
  local ok,result=pcall(fn);C.result=ok and result and 'Action completed' or 'Action unavailable (on-foot / saved position required)'
  if not ok or not result then pcall(playSound,'SystemHand') end
  local t=createTimer(nil,false);t.Interval=100;t.OnTimer=function(sender) sender.destroy();if memrec then memrec.Active=false end end;t.Enabled=true
end
local status=allocateMemory(1024);if not status then error('Could not allocate runtime status.') end
registerSymbol('AK_RuntimeStatus',status,true)
function C.status()
  local s=C.player and string.format('On foot | HP %s/%s | eligible enemies %d | gadgets %d',tostring(ri(C.player+0x478)),tostring(ri(C.player+0x47C)),#C.enemies,#C.gadgets) or 'Waiting for on-foot gameplay'
  if C.result then s=s..' | '..C.result end;writeString(status,s..string.char(0))
end
function C.shutdown()
  if C.timer then C.timer.destroy();C.timer=nil end
  for _,n in ipairs({'grappleRange','batarangRange'}) do C.restore(n) end
  unregisterSymbol('AK_RuntimeStatus');deAlloc(status)
end
if C.name(0)~='None' then C.shutdown();error('Unsupported Knight build: name registry validation failed.') end
if not C.bind() then C.shutdown();error('No active on-foot Batman found. Load single-player gameplay first.') end
-- Validate reflected offsets before any writes are enabled.
for n,off in pairs({Health=0x478,HealthMax=0x47C,Location=0xC4,WorldInfo=0x9C,InvManager=0x33C,CylinderComponent=0x384}) do
  if C.field(C.player,n)~=off then C.shutdown();error('Unsupported Knight layout: '..n) end
end
C.scan();C.status()
C.timer=createTimer(nil,false);C.timer.Interval=50
C.timer.OnTimer=function()
  local ok,err=pcall(function() C.tick=C.tick+1;if C.tick%20==0 then C.scan() end;C.apply();if C.tick%10==0 then C.status() end end)
  if not ok then C.flags={};C.result='Stopped after runtime error: '..tostring(err);C.status();C.timer.Enabled=false end
end
AK=C;C.timer.Enabled=true
