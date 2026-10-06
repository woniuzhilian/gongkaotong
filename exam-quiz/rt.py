# -*- coding: utf-8 -*-
import sys, os, json, shutil
sys.stdout.reconfigure(encoding='utf-8')
D=r"E:\应用程序开发\刷题\exam-quiz\src\data"
P=os.path.join(D,"questions.json")
BAK=os.path.join(D,"questions_BACKUP_20260913_104530.json")
raw=open(BAK,'rb').read()
print("BAK bytes",len(raw))
# detect indent
txt=raw.decode('utf-8')
print("starts:",repr(txt[:40]))
print("BOM:", raw[:3]==b'\xef\xbb\xbf')
# round-trip test
Q=json.loads(txt)
s2=json.dumps(Q,ensure_ascii=False,indent=2)
b2=s2.encode('utf-8')
print("roundtrip bytes",len(b2),"identical:",b2==raw)
if b2!=raw:
    # find first difference
    for i,(a,b) in enumerate(zip(txt,s2)):
        if a!=b:
            print("first diff at",i,repr(txt[max(0,i-40):i+40]),"|",repr(s2[max(0,i-40):i+40])); break
