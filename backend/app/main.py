from dotenv import load_dotenv\nload_dotenv()\nimport os,json,re,uuid
from datetime import datetime,timezone
from contextlib import asynccontextmanager
from typing import Optional
import httpx
from fastapi import FastAPI,HTTPException,UploadFile,File,Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field
from .db import connect,init_db

def now(): return datetime.now(timezone.utc).isoformat()
def rowdict(r):
 x=dict(r); x["evidence"]=json.loads(x.pop("evidence_json")); x["claims"]=json.loads(x.pop("claims_json")); return x
class AnalyzeBody(BaseModel):
 claim:str=Field(min_length=8,max_length=5000)
 max_results:int=Field(default=5,ge=1,le=10)
class MonitorBody(BaseModel):
 query:str=Field(min_length=4,max_length=500)

@asynccontextmanager
async def lifespan(app):
 init_db(); yield
app=FastAPI(title="Verityx API",version="0.2.0",lifespan=lifespan)
origins=os.getenv("CORS_ORIGINS","http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in origins],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

async def search(query,limit):
 key=os.getenv("TAVILY_API_KEY")
 if not key: raise HTTPException(503,"Tavily is not configured. Add TAVILY_API_KEY to backend/.env.")
 try:
  async with httpx.AsyncClient(timeout=40) as c:
   r=await c.post("https://api.tavily.com/search",json={"api_key":key,"query":query,"search_depth":"advanced","max_results":limit,"include_answer":True,"include_raw_content":False})
   r.raise_for_status(); data=r.json()
 except httpx.HTTPError as e: raise HTTPException(502,f"Tavily request failed: {e}")
 ev=[]
 for x in data.get("results",[]):
  ev.append({"title":x.get("title") or "Untitled source","url":x.get("url",""),"content":x.get("content",""),"score":x.get("score"),"published_date":x.get("published_date"),"source":x.get("url","").split("/")[2] if x.get("url") else "Unknown"})
 return ev,data.get("answer")

async def assess(claim,evidence,answer):
 base=os.getenv("BIFROST_BASE_URL","").rstrip("/"); model=os.getenv("BIFROST_MODEL",""); key=os.getenv("BIFROST_API_KEY","")
 if base and model:
  prompt={"claim":claim,"search_answer":answer,"evidence":evidence}
  system='You are Verityx, an evidence-first freshness verifier. Use only supplied evidence. Distinguish current, potentially_stale, contradicted, insufficient_evidence. Stale does not mean false. Contradicted requires credible direct conflict. Return JSON: status, summary, freshness_score (integer 0-100 or null), rationale. Score measures evidence freshness/coverage, never probability of truth. If unsure use insufficient_evidence.'
  try:
   async with httpx.AsyncClient(timeout=70) as c:
    h={"Content-Type":"application/json"}
    if key:h["Authorization"]="Bearer "+key
    r=await c.post(base+"/chat/completions",headers=h,json={"model":model,"temperature":0.1,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":system},{"role":"user","content":json.dumps(prompt)}]})
    r.raise_for_status(); obj=json.loads(r.json()["choices"][0]["message"]["content"])
   if obj.get("status") not in ["current","potentially_stale","contradicted","insufficient_evidence"]: raise ValueError("Invalid status")
   score=obj.get("freshness_score")
   if score is not None: score=max(0,min(100,int(score)))
   return {"status":obj["status"],"summary":str(obj.get("summary","Assessment completed")),"freshness_score":score,"rationale":str(obj.get("rationale","")),"method":"bifrost"}
  except Exception as e:
   return {"status":"insufficient_evidence","summary":"Evidence was retrieved, but the configured Bifrost assessment failed. Review sources manually.","freshness_score":None,"rationale":str(e),"method":"retrieval_only"}
 if not evidence:return {"status":"insufficient_evidence","summary":"No evidence was retrieved. The claim remains unresolved.","freshness_score":None,"rationale":"No sources returned.","method":"retrieval_only"}
 return {"status":"insufficient_evidence","summary":"Evidence retrieved. Connect Bifrost to perform semantic comparison; keyword matching is deliberately not used as a truth test.","freshness_score":None,"rationale":"Tavily retrieval completed; semantic assessment is not configured.","method":"retrieval_only"}

@app.get("/api/health")
async def health():
 return {"status":"ok","service":"verityx-api","version":"0.2.0","integrations":{"tavily":bool(os.getenv("TAVILY_API_KEY")),"bifrost":bool(os.getenv("BIFROST_BASE_URL") and os.getenv("BIFROST_MODEL"))},"database":"sqlite"}
@app.post("/api/analyze")
async def analyze(body:AnalyzeBody):
 ev,answer=await search(body.claim,body.max_results)
 result=await assess(body.claim,ev,answer)
 claims=[s.strip() for s in re.split(r"(?<=[.!?])\\s+",body.claim) if len(s.strip())>12][:8] or [body.claim]
 ident=str(uuid.uuid4()); created=now()
 with connect() as d:
  d.execute("INSERT INTO analyses VALUES(?,?,?,?,?,?,?,?,?,?)",(ident,body.claim,result["status"],result["summary"],result["freshness_score"],created,json.dumps(ev),json.dumps(claims),result["method"],result["rationale"]))
 return {"id":ident,"claim":body.claim,"claims":claims,"created_at":created,"evidence":ev,**result}
@app.get("/api/analyses")
async def analyses(limit:int=Query(default=50,ge=1,le=200)):
 with connect() as d: rows=d.execute("SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
 return [rowdict(r) for r in rows]
@app.get("/api/analyses/{analysis_id}")
async def get_analysis(analysis_id:str):
 with connect() as d:r=d.execute("SELECT * FROM analyses WHERE id=?",(analysis_id,)).fetchone()
 if not r:raise HTTPException(404,"Analysis not found")
 return rowdict(r)
@app.delete("/api/analyses/{analysis_id}")
async def delete_analysis(analysis_id:str):
 with connect() as d:r=d.execute("DELETE FROM analyses WHERE id=?",(analysis_id,))
 if not r.rowcount:raise HTTPException(404,"Analysis not found")
 return {"deleted":True}
@app.post("/api/monitors")
async def create_monitor(body:MonitorBody):
 ident=str(uuid.uuid4()); created=now()
 with connect() as d:d.execute("INSERT INTO monitors(id,query,created_at) VALUES(?,?,?)",(ident,body.query,created))
 return {"id":ident,"query":body.query,"active":True,"created_at":created}
@app.get("/api/monitors")
async def list_monitors():
 with connect() as d:rows=d.execute("SELECT * FROM monitors ORDER BY created_at DESC").fetchall()
 return [dict(r) for r in rows]
@app.patch("/api/monitors/{monitor_id}")
async def toggle_monitor(monitor_id:str):
 with connect() as d:
  r=d.execute("SELECT active FROM monitors WHERE id=?",(monitor_id,)).fetchone()
  if not r:raise HTTPException(404,"Monitor not found")
  active=0 if r["active"] else 1; d.execute("UPDATE monitors SET active=? WHERE id=?",(active,monitor_id))
 return {"id":monitor_id,"active":bool(active)}
@app.delete("/api/monitors/{monitor_id}")
async def delete_monitor(monitor_id:str):
 with connect() as d:r=d.execute("DELETE FROM monitors WHERE id=?",(monitor_id,))
 if not r.rowcount:raise HTTPException(404,"Monitor not found")
 return {"deleted":True}
@app.post("/api/documents/inspect")
async def inspect_document(file:UploadFile=File(...)):
 if file.content_type not in ["text/plain","text/markdown","text/csv","application/json"]:raise HTTPException(415,"For this preview, upload a TXT, MD, CSV or JSON text file.")
 raw=await file.read(1_000_001)
 if len(raw)>1_000_000:raise HTTPException(413,"File exceeds 1 MB.")
 try:text=raw.decode("utf-8")
 except UnicodeDecodeError:raise HTTPException(400,"File must be UTF-8 text.")
 if len(text.strip())<8:raise HTTPException(400,"Document has too little readable text.")
 return {"filename":file.filename,"characters":len(text),"preview":text[:5000],"message":"Document text extracted. Select a claim from the preview and send it to Analyze for live verification."}
