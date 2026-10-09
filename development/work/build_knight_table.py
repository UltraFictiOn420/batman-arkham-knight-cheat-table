"""Build the original Knight table from its reviewed Lua source."""
from pathlib import Path
import xml.etree.ElementTree as ET
from luaparser import ast
ROOT=Path(__file__).resolve().parents[1]
runtime=(ROOT/'work/arkham_knight_runtime.lua').read_text(encoding='utf-8');ast.parse(runtime)
t=ET.Element('CheatTable',CheatEngineTableVersion='45');entries=ET.SubElement(t,'CheatEntries')
def node(parent,i,title,script=None,key=None,group=False):
    e=ET.SubElement(parent,'CheatEntry');ET.SubElement(e,'ID').text=str(i);ET.SubElement(e,'Description').text='"'+title+'"'
    if script:ET.SubElement(e,'VariableType').text='Auto Assembler Script';ET.SubElement(e,'AssemblerScript').text=script
    if group:ET.SubElement(e,'GroupHeader').text='1';ET.SubElement(e,'Options',moHideChildren='1')
    if key:
        h=ET.SubElement(ET.SubElement(e,'Hotkeys'),'Hotkey');ET.SubElement(h,'Action').text='Toggle Activation';ET.SubElement(ET.SubElement(h,'Keys'),'Key').text=str(key);ET.SubElement(h,'ID').text='0'
    return e
r=node(entries,1,'[Required] Initialize Arkham Knight - Original v1',f'[ENABLE]\n{{$lua}}\nif syntaxcheck then return end\n{runtime}\n{{$asm}}\n[DISABLE]\n{{$lua}}\nif syntaxcheck then return end\nif AK and AK.shutdown then AK.shutdown() end\nAK=nil\n{{$asm}}')
ET.SubElement(r,'Options',moHideChildren='1',moDeactivateChildrenAsWell='1');children=ET.SubElement(r,'CheatEntries')
s=node(children,2,'Runtime Status (read-only; no popup)');ET.SubElement(s,'VariableType').text='String';ET.SubElement(s,'Length').text='500';ET.SubElement(s,'Unicode').text='0';ET.SubElement(s,'Address').text='AK_RuntimeStatus'
def group(i,title):return ET.SubElement(node(children,i,title,group=True),'CheatEntries')
def flag(parent,i,title,n,key=None,other=None):
    extra=f'local x=getAddressList().getMemoryRecordByID({other});if x and x.Active then x.Active=false end\n' if other else ''
    return node(parent,i,title,f"[ENABLE]\n{{$lua}}\nif syntaxcheck then return end\nif not AK then error('Enable Initialize Arkham Knight first.') end\n{extra}AK.setFlag('{n}',true)\n{{$asm}}\n[DISABLE]\n{{$lua}}\nif syntaxcheck then return end\nif AK then AK.setFlag('{n}',false) end\n{{$asm}}",key)
def action(parent,i,title,fn,key):
    return node(parent,i,title,f"[ENABLE]\n{{$lua}}\nif syntaxcheck then return end\nif not AK then error('Enable Initialize Arkham Knight first.') end\nAK.action(memrec,function() return AK.{fn} end)\n{{$asm}}\n[DISABLE]",key)
g=group(10,'Player / Survival');flag(g,11,'Infinite Health [Test]','health')
g=group(20,'Enemies / Melee Combat');flag(g,22,'Super Damage (enemy HP / 10) [-] [Test]','superDamage',189,23);flag(g,23,'One-Hit Knockout (enemy HP = 1) [=] [Test]','oneHit',187,22)
g=group(30,'Gadgets / Reach');flag(g,31,'Extra-Long Grapple Distance [Test]','grappleRange');flag(g,32,'Extra-Long Batarang Distance [Test]','batarangRange')
g=group(60,'Positions / Teleport (on-foot, same character session)');action(g,61,'Save Position [J] [Test]','save()',74);action(g,62,'Teleport to Saved Position [K] [Test]','teleport()',75);action(g,63,'Undo / Redo Last Teleport [L] [Test]','undoTeleport()',76)
for i,n in enumerate([1,2,5,10]):action(g,64+i,f'Teleport Up {n} Body Height(s) [F{i+1}] [Test]',f'up({n})',112+i)
ET.SubElement(t,'UserdefinedSymbols');ET.SubElement(t,'Comments').text='Original Knight v1, Steam BatmanAK.exe x64, single-player only. No console, executable hooks, armor, XP/points, puzzle bypass or global time changes. All features require user gameplay testing. Infinite Health replenishes living on-foot player HP; not immunity to instant death or scripts. Damage caps nearby loaded eligible enemy pawn HP; disable around tutorials, scripted encounters and bosses. Off stops damage edits but does not restore lost enemy HP. Batarang/gadget damage is NOT yet claimed supported. Reach changes current player inventory items only and restores their floats on disable if identity still matches. Long range cannot create grapple targets or bypass line of sight/streaming. Teleports require walking/falling and same pawn/world; no collision/streaming safety. J/K/L save/teleport/undo; F1-F4 up 1/2/5/10 body heights; main -/= damage toggles. No Batmobile support yet. Initial reflected offsets and live HP 100/100 independently inspected; simulated write tests do not establish gameplay success. Back up saves and use one table version at a time.'
ET.indent(t,space='  ');out=ROOT/'outputs/Batman Arkham Knight - Original v1.CT';ET.ElementTree(t).write(out,encoding='utf-8',xml_declaration=True)
for e in ET.parse(out).findall('.//AssemblerScript'):
    for b in e.text.split('{$lua}')[1:]:ast.parse(b.split('{$asm}')[0])
ids=[e.text for e in ET.parse(out).findall('.//CheatEntry/ID')];assert len(ids)==len(set(ids));print(out);print('XML, embedded Lua syntax and unique IDs verified.')
