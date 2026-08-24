import os,base64,random,requests
from urllib.parse import urlsplit,urlunsplit
from dotenv import load_dotenv
load_dotenv()

TOKEN=os.environ["GITHUB_TOKEN"]; OWNER=os.environ["GITHUB_OWNER"]; REPO=os.environ["GITHUB_REPO"]
BRANCH=os.getenv("GITHUB_BRANCH","main")
SOURCE=os.getenv("CONFIG_FILE","data/configs.txt")
OUTPUT=os.getenv("OUTPUT_FILE","subscriptions/netishield.txt")
COUNT=int(os.getenv("PUBLISH_COUNT","20"))
POOL=int(os.getenv("NEWEST_POOL_SIZE","100"))
REMARKS="NetiShield"
GH=f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
H={"Authorization":f"Bearer {TOKEN}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}

def get(path):
 r=requests.get(f"{GH}/{path}",headers=H,params={"ref":BRANCH},timeout=30)
 if r.status_code==404:return "",None
 r.raise_for_status();j=r.json()
 return base64.b64decode(j["content"]).decode(),j["sha"]

def put(path,data,msg,sha=None):
 b={"message":msg,"content":base64.b64encode(data.encode()).decode(),"branch":BRANCH}
 if sha:b["sha"]=sha
 r=requests.put(f"{GH}/{path}",headers=H,json=b,timeout=30);r.raise_for_status()

src,_=get(SOURCE)
rows=[x.strip() for x in src.splitlines() if x.strip()]
pool=rows[-POOL:]
chosen=random.sample(pool,min(COUNT,len(pool))) if pool else []
out=[]
for c in chosen:
 p=urlsplit(c)
 out.append(urlunsplit((p.scheme,p.netloc,p.path,p.query,REMARKS)))
content="\n".join(out)+("\n" if out else "")
_,sha=get(OUTPUT)
put(OUTPUT,content,"Daily NetiShield subscription update",sha)
print(f"Published {len(out)} configs.")
