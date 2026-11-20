import sys
S="/tmp/claude-0/-home-user-Admin/d39b7636-1eba-5c6d-b314-8084f5795d40/scratchpad/no2"
k,c,src,voice,extra=sys.argv[1:6]
no=[l.strip() for l in open(f"{S}/no/{k}.txt",encoding="utf-8") if l.strip()]
sv=[l.rstrip("\n").split("\t")[3] for l in open(f"{S}/sv/{k}.txt",encoding="utf-8") if l.strip()]
out=[f"Norrtvätt NO batch 2 - {c}: norsk manus (Nordvask Maskinren), 1:1 med svenska meningar",f"Svensk källa: {src}",
     f"Röst: ElevenLabs eleven_v3, language_code no, {voice}, en tagning"]+([extra] if extra else [])+[""]
for i,(a,b) in enumerate(zip(no,sv),1): out += [f"{i:02d} NO: {a}", f"   SV: {b}"]
open(f"/home/user/Admin/leverans/norge_batch2/manus/manus_NO_batch2_{c}.txt","w",encoding="utf-8").write("\n".join(out)+"\n")
