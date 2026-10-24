"""KISIV AI MVP: event triage with safe, dry-run-only response."""
from __future__ import annotations
import hmac, json, logging, os, sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

APP_NAME = "KISIV AI"
logger = logging.getLogger("kisiv.security")
# Prefer the current name while preserving compatibility with existing deployments.
DB_PATH = Path(os.getenv("KISIV_DB_PATH") or os.getenv("AEGIS_DB_PATH") or "./data/kisiv.db")
def utc_now() -> str: return datetime.now(timezone.utc).isoformat()
def connect_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10); conn.row_factory = sqlite3.Row; return conn
def init_db() -> None:
    with closing(connect_db()) as conn:
        conn.executescript("""CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, source TEXT NOT NULL, event_type TEXT NOT NULL, severity TEXT NOT NULL, description TEXT NOT NULL, asset TEXT, metadata_json TEXT NOT NULL, created_at TEXT NOT NULL); CREATE TABLE IF NOT EXISTS audit_log (id TEXT PRIMARY KEY, event_id TEXT, action TEXT NOT NULL, outcome TEXT NOT NULL, details_json TEXT NOT NULL, created_at TEXT NOT NULL);"""); conn.commit()
app = FastAPI(title=APP_NAME, description="Defensive security event triage with safe, dry-run-only response.", version="0.1.0")

@app.middleware("http")
async def api_key_guard(request: Request, call_next):
    """Enforce an API key when configured; keep health checks public."""
    expected_key = os.getenv("KISIV_API_KEY", "").strip()
    if expected_key and request.url.path.startswith("/api/v1/"):
        supplied_key = request.headers.get("x-api-key", "")
        authorization = request.headers.get("authorization", "")
        if not supplied_key and authorization.lower().startswith("bearer "):
            supplied_key = authorization[7:].strip()
        if not supplied_key or not hmac.compare_digest(supplied_key, expected_key):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid API key"},
                headers={"WWW-Authenticate": "Bearer"},
            )
    return await call_next(request)

@app.on_event("startup")
def startup() -> None:
    init_db()
    if not os.getenv("KISIV_API_KEY", "").strip():
        logger.warning("KISIV_API_KEY is not configured; API routes are unauthenticated. Keep this service bound to localhost.")
class EventIn(BaseModel):
    source: str = Field(min_length=1, max_length=100)
    event_type: str = Field(min_length=1, max_length=100)
    severity: Literal["info","low","medium","high","critical"] = "info"
    description: str = Field(min_length=1, max_length=4000)
    asset: str | None = Field(default=None, max_length=500)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, value: dict[str, Any]) -> dict[str, Any]:
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        if len(encoded) > 16_384:
            raise ValueError("metadata must be 16 KiB or smaller")

        def check_depth(item: Any, depth: int = 0) -> None:
            if depth > 8:
                raise ValueError("metadata nesting must not exceed 8 levels")
            if isinstance(item, dict):
                for child in item.values():
                    check_depth(child, depth + 1)
            elif isinstance(item, list):
                for child in item:
                    check_depth(child, depth + 1)

        check_depth(value)
        return value
class ResponseRequest(BaseModel):
    event_id: str
    action: Literal["alert","isolate_asset","block_source","disable_account"] = "alert"
    reason: str = Field(default="MVP dry-run", max_length=1000)
SEVERITY_SCORE = {"info":0,"low":10,"medium":25,"high":45,"critical":65}
def assess_event(event: dict[str, Any]) -> dict[str, Any]:
    score = SEVERITY_SCORE.get(event["severity"], 0); reasons = [f"来源上报严重程度：{event['severity']}"]
    text = f"{event['event_type']} {event['description']}".lower()
    indicators = [(( "repeated_login_failure","brute force","暴力破解","多次登录失败"),25,"疑似重复登录失败或暴力尝试"),(("malware","ransomware","恶意软件","勒索软件"),35,"事件文本包含恶意软件相关信号"),(("prompt injection","提示注入","tool abuse","工具滥用"),25,"疑似 AI Agent 提示注入或工具滥用"),(("data exfiltration","数据外传","credential theft","凭据窃取"),35,"疑似数据外传或凭据窃取")]
    for terms, points, reason in indicators:
        if any(term in text for term in terms): score += points; reasons.append(reason)
    score=min(score,100)
    if score>=80: level,recommendation="critical","立即通知管理员并人工核验；不要自动执行破坏性操作。"
    elif score>=55: level,recommendation="high","优先调查相关资产与时间线，建议人工审批后采取遏制措施。"
    elif score>=25: level,recommendation="medium","补充上下文并检查相邻事件，必要时升级调查。"
    else: level,recommendation="low","记录并持续观察；当前规则未发现强风险信号。"
    return {"score":score,"risk_level":level,"reasons":reasons,"recommendation":recommendation,"engine":"starter-rules-v1","limitations":"启发式演示规则，可能误报或漏报；不能作为唯一安全决策依据。"}
def add_audit(event_id: str | None, action: str, outcome: str, details: dict[str, Any]) -> None:
    with closing(connect_db()) as conn:
        conn.execute("INSERT INTO audit_log (id,event_id,action,outcome,details_json,created_at) VALUES (?,?,?,?,?,?)",(str(uuid4()),event_id,action,outcome,json.dumps(details,ensure_ascii=False),utc_now())); conn.commit()
@app.get("/health")
def health() -> dict[str,str]: return {"status":"ok","service":APP_NAME,"version":"0.1.0"}
@app.post("/api/v1/events",status_code=201)
def create_event(payload: EventIn) -> dict[str,Any]:
    event_id=str(uuid4()); created_at=utc_now(); item=payload.model_dump()
    with closing(connect_db()) as conn:
        conn.execute("INSERT INTO events (id,source,event_type,severity,description,asset,metadata_json,created_at) VALUES (?,?,?,?,?,?,?,?)",(event_id,item["source"],item["event_type"],item["severity"],item["description"],item["asset"],json.dumps(item["metadata"],ensure_ascii=False),created_at)); conn.commit()
    add_audit(event_id,"event.created","recorded",{"source":item["source"],"event_type":item["event_type"]})
    return {"id":event_id,**item,"created_at":created_at}
@app.get("/api/v1/events")
def list_events(limit: int = Query(default=50,ge=1,le=200)) -> dict[str,Any]:
    with closing(connect_db()) as conn: rows=conn.execute("SELECT * FROM events ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
    items=[]
    for row in rows:
        item=dict(row); item["metadata"]=json.loads(item.pop("metadata_json")); items.append(item)
    return {"items":items,"count":len(items)}
@app.post("/api/v1/events/{event_id}/assess")
def assess(event_id: str) -> dict[str,Any]:
    with closing(connect_db()) as conn: row=conn.execute("SELECT * FROM events WHERE id=?",(event_id,)).fetchone()
    if row is None: raise HTTPException(status_code=404,detail="Event not found")
    result=assess_event(dict(row)); add_audit(event_id,"event.assessed","completed",result); return {"event_id":event_id,**result}
@app.post("/api/v1/responses")
def request_response(payload: ResponseRequest) -> dict[str,Any]:
    with closing(connect_db()) as conn: row=conn.execute("SELECT id FROM events WHERE id=?",(payload.event_id,)).fetchone()
    if row is None: raise HTTPException(status_code=404,detail="Event not found")
    result={"response_id":str(uuid4()),"event_id":payload.event_id,"requested_action":payload.action,"status":"simulated","dry_run":True,"reason":payload.reason,"message":"已记录模拟响应；当前版本不会更改系统、网络或账号状态。","created_at":utc_now()}
    add_audit(payload.event_id,"response.requested","simulated",result); return result
@app.get("/api/v1/audit")
def list_audit(limit: int = Query(default=50,ge=1,le=200)) -> dict[str,Any]:
    with closing(connect_db()) as conn: rows=conn.execute("SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?",(limit,)).fetchall()
    items=[]
    for row in rows:
        item=dict(row); item["details"]=json.loads(item.pop("details_json")); items.append(item)
    return {"items":items,"count":len(items)}
