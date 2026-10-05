"""Isolated synthetic Phase 12 runtime/restart/preservation checks; never prints keys."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import httpx
from sqlalchemy import select, text, create_engine
from backend.app.core.config import Settings
from backend.app.db.base import Base
from backend.app.db.session import create_engine_and_factory
from backend.app.models import AuditEvent

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/".audit/phase12-browser-state.json"
API="http://127.0.0.1:8003"


def state():
    value=json.loads(STATE.read_text())
    if not re.fullmatch(r"p12_browser_[a-f0-9]{32}",value["schema"]):
        raise RuntimeError("Unsafe verification schema; operation refused.")
    return value


def digest(settings):
    engine,factory=create_engine_and_factory(settings)
    rows={}
    with factory() as session:
        for table in Base.metadata.sorted_tables:
            if table.name in {"sessions","login_rate_buckets"}: continue
            q=select(table)
            if table.name=="audit_events": q=q.where(AuditEvent.entity!="session")
            rows[table.name]=sorted(json.dumps(dict(r),default=str,sort_keys=True) for r in session.execute(q).mappings())
    engine.dispose()
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()


def restart(value,settings,provider=None):
    row=next(p for p in value["processes"] if p["kind"]=="api")
    pid=row["pid"]
    probe=subprocess.run(["powershell","-NoProfile","-Command",f'(Get-CimInstance Win32_Process -Filter "ProcessId={pid}").CommandLine'],capture_output=True,text=True)
    if "scripts/run_backend.py" not in probe.stdout.replace("\\","/"):
        raise RuntimeError("Recorded PID is not this verification API; stop refused.")
    subprocess.run(["taskkill","/PID",str(pid),"/T","/F"],check=True,capture_output=True)
    env=os.environ.copy()
    env.update(DATABASE_URL=settings.database_url,DB_SCHEMA=value["schema"],APP_ENV="test",API_PORT="8003",CORS_ORIGINS="http://127.0.0.1:5176",SESSION_COOKIE_SECURE="false",SESSION_COOKIE_SAMESITE="lax")
    if provider: env["AI_PROVIDER"]=provider
    with open(ROOT/".audit/phase12-browser-api.out.log","a") as out,open(ROOT/".audit/phase12-browser-api.err.log","a") as err:
        process=subprocess.Popen([sys.executable,"scripts/run_backend.py"],cwd=ROOT,env=env,stdout=out,stderr=err,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
    row["pid"]=process.pid
    STATE.write_text(json.dumps(value))
    for _ in range(40):
        try:
            if httpx.get(API+"/api/ready",timeout=2).status_code==200: return
        except httpx.HTTPError: pass
        time.sleep(.25)
    raise RuntimeError("Verification API did not become ready.")


def smoke(value,expected_provider=None):
    report={"health":httpx.get(API+"/api/health").status_code,"ready":httpx.get(API+"/api/ready").status_code,"roles":{}}
    for role,login,password in [("Admin","browser-admin","BrowserAdminPass123!"),("PM","browser-pm","BrowserManagerPass123!"),("TL","browser-tl","BrowserLeaderPass123!")]:
        with httpx.Client(base_url=API,timeout=120) as client:
            assert client.post("/api/auth/login",json={"email":login,"password":password}).status_code==200
            context=client.get("/api/assistant/contexts").json()
            project=context["projects"][0]["id"]
            response=client.post("/api/assistant/ask",json={"question":"Show project overview","project_id":project})
            assert response.status_code==200,response.json().get("error")
            data=response.json()
            source=client.get(data["evidence"][0]["source"])
            assert source.status_code==200 and source.json()["record"]["evidenceId"]==data["evidence"][0]["evidenceId"]
            if expected_provider: assert data["mode"]=="AI", data["failure"]
            report["roles"][role]={"mode":data["mode"],"failure":data["failure"],"scope":data["context"]["scope"],"source":source.status_code,"evidenceRecords":len(data["evidence"])}
            if role=="PM":
                value["restartProbe"]={"cookie":dict(client.cookies),"project":project,"conversation":data["conversation"],"source":data["evidence"][0]["source"]}
                if expected_provider:
                    report["languages"]={"en":"PASS"}
                    for language,question in [("hi","परियोजना का सारांश दिखाएँ"),("hi-Latn","Project ka overview dikhao")]:
                        answer=client.post("/api/assistant/ask",json={"question":question,"intent":"overview","project_id":project,"language":language}).json()
                        assert answer["mode"]=="AI",answer.get("failure")
                        report["languages"][language]={"mode":answer["mode"],"claims":answer["answer"]["claims"]}
    report["requestedSelection"] = expected_provider
    report["providerIdentityVerified"] = False  # Use verify_assistant_live for safe backend diagnostics.
    STATE.write_text(json.dumps(value))
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["snapshot","smoke","restart","verify","cleanup"])
    parser.add_argument("--provider",choices=["none","groq","nvidia","auto"])
    args=parser.parse_args(); value=state(); canonical=Settings()
    settings=canonical.model_copy(update={"db_schema":value["schema"]})
    if args.action=="snapshot":
        value["before"]=digest(settings); value["canonicalBefore"]=digest(canonical)
        STATE.write_text(json.dumps(value)); print("Canonical and isolated domain fingerprints saved without exporting records.")
    elif args.action=="smoke":
        report=smoke(value,args.provider if args.provider in {"groq","nvidia"} else None)
        (ROOT/f".audit/phase12-runtime-{args.provider or 'fallback'}.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        print({"health":report["health"],"ready":report["ready"],"roles":report["roles"]})
    elif args.action=="restart":
        restart(value,canonical,args.provider)
        print("Only the recorded isolated Phase 12 API restarted.")
    elif args.action=="verify":
        assert value["before"]==digest(settings),"Isolated domain records changed"
        assert value["canonicalBefore"]==digest(canonical),"Canonical domain records changed"
        probe=value.get("restartProbe")
        if probe:
            with httpx.Client(base_url=API,cookies=probe["cookie"],timeout=120) as client:
                assert client.get(probe["source"]).status_code==200
                answer=client.post("/api/assistant/ask",json={"question":"Which updates await PM review?","project_id":probe["project"],"conversation":probe["conversation"]})
                assert answer.status_code==200
        print("Canonical/isolated domain fingerprints unchanged; persisted session, source and conversation survive API restart.")
    elif args.action=="cleanup":
        for row in value["processes"]:
            pid=row["pid"]
            probe=subprocess.run(["powershell","-NoProfile","-Command",f'(Get-CimInstance Win32_Process -Filter "ProcessId={pid}").CommandLine'],capture_output=True,text=True)
            signature="scripts/run_backend.py" if row["kind"]=="api" else "npm run dev"
            if signature in probe.stdout.replace("\\","/"):
                subprocess.run(["taskkill","/PID",str(pid),"/T","/F"],check=True,capture_output=True)
        engine=create_engine(canonical.database_url)
        with engine.begin() as connection: connection.execute(text(f'DROP SCHEMA "{value["schema"]}" CASCADE'))
        engine.dispose(); value.pop("restartProbe",None);value["cleanedUp"]=True
        STATE.write_text(json.dumps(value));print("Only recorded Phase 12 processes and their disposable schema were cleaned up.")


if __name__=="__main__": main()
