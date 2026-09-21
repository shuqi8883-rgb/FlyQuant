import json,re
from datetime import datetime,timezone
from pathlib import Path
import requests,pandas as pd

HEADERS={"User-Agent":"Mozilla/5.0 FlyQuant data sync"}
def fetch(url):
    r=requests.get(url,headers=HEADERS,timeout=20)
    r.raise_for_status()
    r.encoding=r.apparent_encoding or "utf-8"
    return r.text

def parse_tables(url,sport):
    try:
        tables=pd.read_html(fetch(url))
    except Exception as e:
        return {"sport":sport,"source":url,"items":[],"error":str(e)}
    items=[]
    for t in tables:
        rows=t.fillna("").astype(str).to_dict("records")
        for row in rows:
            text=" ".join(row.values())
            if any(x in text for x in ["VS","主队","客队","开赛时间"]) and len(text)>8:
                items.append(row)
    return {"sport":sport,"source":url,"items":items[:100],"error":None}

today=datetime.now(timezone.utc).strftime("%Y-%m-%d")
sources=[
 {"sport":"football","url":f"https://trade.500.com/jczq/index.php?date={today}&g=2"},
 {"sport":"basketball","url":f"https://trade.500.com/jclq/?date={today}"}
]
out={"updated_at":datetime.now(timezone.utc).isoformat(),"date":today,"provider":"500.com public sports data","note":"赛事数据用于展示与分析；中国体育彩票实际可售场次、玩法和停售时间以官方渠道为准。","sports":[parse_tables(x["url"],x["sport"]) for x in sources]}
Path("data").mkdir(exist_ok=True)
Path("data/live.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
