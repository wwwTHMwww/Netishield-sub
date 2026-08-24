import os, base64, binascii, requests
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit
from dotenv import load_dotenv

load_dotenv()
TOKEN=os.environ["BOT_TOKEN"]
GH_TOKEN=os.environ["GITHUB_TOKEN"]
OWNER=os.environ["GITHUB_OWNER"]
REPO=os.environ["GITHUB_REPO"]
BRANCH=os.getenv("GITHUB_BRANCH","main")
CONFIG_FILE=os.getenv("CONFIG_FILE","data/configs.txt")
OFFSET_FILE=os.getenv("OFFSET_FILE","data/telegram_offset.txt")
REMARKS="NetiShield"

API=f"https://api.telegram.org/bot{TOKEN}"
GH=f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
HEAD={"Authorization":f"Bearer {GH_TOKEN}","Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}

def gh_get(path):
    r=requests.get(f"{GH}/{path}",headers=HEAD,params={"ref":BRANCH},timeout=20)
    if r.status_code==404:return "",None
    r.raise_for_status()
    j=r.json()
    return base64.b64decode(j["content"]).decode("utf-8"),j["sha"]

def gh_put(path,content,message,sha=None):
    body={"message":message,"content":base64.b64encode(content.encode()).decode(),"branch":BRANCH}
    if sha: body["sha"]=sha
    r=requests.put(f"{GH}/{path}",headers=HEAD,json=body,timeout=20)
    r.raise_for_status()

def decode_configs(text):
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    direct=[x for x in lines if x.lower().startswith(("vless://","vmess://","trojan://","ss://"))]
    if direct:return direct
    compact="".join(lines)
    try:
        decoded=base64.b64decode(compact+"="*(-len(compact)%4)).decode("utf-8","ignore")
        return [x.strip() for x in decoded.splitlines() if x.strip().lower().startswith(("vless://","vmess://","trojan://","ss://"))]
    except (binascii.Error,ValueError):
        return []

def rename(cfg):
    try:
        p=urlsplit(cfg)
        return urlunsplit((p.scheme,p.netloc,p.path,p.query,REMARKS))
    except Exception:return cfg

def send(chat,text):
    requests.post(f"{API}/sendMessage",json={"chat_id":chat,"text":text},timeout=20)

def main():
    configs,sha=gh_get(CONFIG_FILE)
    offset,_=gh_get(OFFSET_FILE)
    offset=int(offset.strip()) if offset.strip().isdigit() else 0

    r=requests.get(f"{API}/getUpdates",params={"offset":offset,"timeout":0,"allowed_updates":"message"},timeout=20)
    r.raise_for_status()
    updates=r.json().get("result",[])
    changed=False

    allowed={x.strip() for x in os.getenv("ALLOWED_USER_IDS","").split(",") if x.strip()}

    for u in updates:
        new_offset=u["update_id"]+1
        offset=max(offset,new_offset)
        msg=u.get("message",{})
        chat=msg.get("chat",{})
        uid=str(msg.get("from",{}).get("id",""))
        text=msg.get("text","").strip()

        if allowed and uid not in allowed:
            continue

        if text=="/start":
            send(chat.get("id"),"سلام 👋\\nکانفیگ V2Ray را بفرست. ربات آن را در مخزن NetiShield ذخیره می‌کند.")
            continue
        if text=="/status":
            count=len([x for x in configs.splitlines() if x.strip()])
            send(chat.get("id"),f"📊 تعداد کانفیگ‌های ذخیره‌شده: {count}")
            continue

        found=decode_configs(text)
        if found:
            existing={x.strip() for x in configs.splitlines() if x.strip()}
            added=0
            for c in found:
                c=rename(c)
                if c not in existing:
                    existing.add(c);added+=1
            configs="\n".join(existing)+"\n"
            changed=True
            send(chat.get("id"),f"✅ {added} کانفیگ جدید ذخیره شد.")
        elif text:
            send(chat.get("id"),"❌ کانفیگ VLESS/VMess/Trojan/SS یا Base64 معتبر پیدا نشد.")

    if changed:
        gh_put(CONFIG_FILE,configs,"Bot: add new V2Ray configs",sha)

    gh_put(OFFSET_FILE,str(offset)+"\n","Bot: update Telegram offset",gh_get(OFFSET_FILE)[1])

if __name__=="__main__":
    main()
