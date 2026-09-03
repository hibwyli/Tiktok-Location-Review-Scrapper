#!/usr/bin/env python3
import requests, json, time, pathlib, argparse
BASE="https://api22-normal-c-alisg.tiktokv.com/tiktok/poi/review/get/v1"
H={"User-Agent":"Mozilla/5.0"}
def scrape(poi_id):
    cursor=0
    seen=set()
    out=[]
    while True:
        r=requests.get(BASE, params={"poi_id":poi_id,"scene":"7","count":"20","cursor":str(cursor),"sort_type":"2","review_tab":"0"}, headers=H, timeout=15)
        j=r.json()
        batch=j.get("reviews",[])
        if not batch and not j.get("has_more"): break
        for rev in batch:
            if not rev.get("content",{}).get("text","").strip(): continue
            rid=rev.get("review_id")
            if rid not in seen:
                seen.add(rid)
                out.append(rev)
        if not j.get("has_more"): break
        cursor=int(j.get("cursor", cursor+20))
        time.sleep(0.3)
        if cursor>20000: break
    out.sort(key=lambda x: int(x.get("basic_info",{}).get("create_time",0)), reverse=True)
    # Minimal
    minimal=[]
    from datetime import datetime
    for r in out:
        ct=r.get("basic_info",{}).get("create_time")
        try:
            c=int(ct)
            if c>2000000000: c//=1000
            d=datetime.fromtimestamp(c).isoformat()
        except: d=None
        imgs=[(img.get("origin_image",{}).get("url_list") or img.get("crop_image",{}).get("url_list") or [None])[0] for img in r.get("content",{}).get("image_data",[]) or []]
        imgs=[u for u in imgs if u]
        minimal.append({"name":r.get("author",{}).get("nickname"),"stars":r.get("content",{}).get("rating"),"comment":r.get("content",{}).get("text","").strip(),"images":imgs,"create_time":str(ct) if ct else None,"create_date":d})
    pathlib.Path("data").mkdir(exist_ok=True)
    json.dump(minimal, open(f"data/{poi_id}.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Done {poi_id}: {len(minimal)} -> data/{poi_id}.json")
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("poi_id", help="POI ID, e.g. 23661696389879272")
    args=ap.parse_args()
    scrape(args.poi_id)
