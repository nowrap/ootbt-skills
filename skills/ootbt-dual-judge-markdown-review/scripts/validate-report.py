#!/usr/bin/env python
"""Mechanically validate a staged dual-judge Markdown report."""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

HEADINGS=[
"## Gesamturteil","## Tragende Befunde","## Claim-Matrix",
"## Detailprüfung der Behauptungen","## Abhängigkeiten, Gates und offene Entscheidungen",
"## Scope-Abdeckung und nicht zugeordnete Flächen","## Risiken, Lücken und Widersprüche",
"## Konkrete Korrekturen vor Freigabe","## Belege und durchgeführte Prüfungen",
"## Grenzen der Methode","## Offene Punkte / UNBEKANNT"]
VERDICTS=["TRÄGT","TRÄGT MIT ÄNDERUNGEN","NICHT BELASTBAR","WIDERLEGT","UNBEKANNT"]
SECRET_PATTERNS=[
re.compile(r"(?i)(?:api[_-]?key|token|secret|password)\s*[:=]\s*[`\"']?[A-Za-z0-9_./+=-]{24,}"),
re.compile(r"\b(?:sk-|ghp_|glpat-)[A-Za-z0-9_-]{16,}"),
re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")]

def sha(path:Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def fail(msg:str,errors:list[str]): errors.append(msg)

def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--report",required=True); p.add_argument("--title",required=True); p.add_argument("--source",required=True); p.add_argument("--metrics",required=True)
    p.add_argument("--expected-provider"); p.add_argument("--expected-requested-model")
    p.add_argument("--expected-observed-model"); p.add_argument("--require-thread-id",action="store_true")
    p.add_argument("--require-metric",action="append",default=[]); a=p.parse_args()
    report=Path(a.report); source=Path(a.source); metrics=Path(a.metrics); errors=[]
    for f,label in [(report,"report"),(source,"source"),(metrics,"metrics")]:
        if not f.is_file(): fail(f"missing {label}: {f}",errors)
    if errors:
        print("\n".join("ERROR: "+e for e in errors),file=sys.stderr); return 64
    text=report.read_text(encoding="utf-8",errors="strict"); lines=text.splitlines()
    if not lines or lines[0]!=a.title: fail(f"first line must equal {a.title!r}",errors)
    h1=[x for x in lines if x.startswith("# ")]
    if len(h1)!=1: fail(f"expected exactly one H1, found {len(h1)}",errors)
    pos=[]
    for h in HEADINGS:
        if lines.count(h)!=1: fail(f"heading must occur once: {h}",errors)
        else: pos.append(lines.index(h))
    if len(pos)==len(HEADINGS) and pos!=sorted(pos): fail("required headings are out of order",errors)
    if len(text)<1200: fail("report is too short to be substantive",errors)
    verdict_block=text[text.find("## Gesamturteil"):text.find("## Tragende Befunde")]
    if not any(v in verdict_block for v in VERDICTS): fail("no allowed verdict in Gesamturteil",errors)
    claim_block=text[text.find("## Claim-Matrix"):text.find("## Detailprüfung der Behauptungen")]
    required_columns=["ID","Tragende Aussage","Belegstatus","Stand/Ref","Gegenprüfung","Auswirkung"]
    if not all(column in claim_block for column in required_columns): fail("claim matrix lacks required columns",errors)
    if not any(status in claim_block for status in ["BELEGT","PLAUSIBEL","UNBEKANNT","WIDERSPRUCH"]): fail("claim matrix has no allowed evidence status",errors)
    method_block=text[text.find("## Grenzen der Methode"):text.find("## Offene Punkte / UNBEKANNT")]
    if len(method_block.strip()) < 80: fail("Grenzen der Methode is not substantive",errors)
    if re.search(r"(?i)<(?:tool|function)|recipient_name|tool_call|analysis channel",text): fail("report appears to contain tool/protocol markup",errors)
    if ".handoff" in text.casefold(): fail("report leaks internal .handoff provenance",errors)
    for pat in SECRET_PATTERNS:
        if pat.search(text): fail(f"possible secret matched: {pat.pattern}",errors)
    try: meta=json.loads(metrics.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e: fail(f"invalid metrics JSON: {e}",errors); meta={}
    if meta.get("terminal_completion") is not True: fail("metrics do not confirm terminal completion",errors)
    if not meta.get("provider"): fail("metrics have no provider",errors)
    if meta.get("permission_denials") not in (None, [], {}): fail("metrics contain permission denials",errors)
    if a.expected_provider and meta.get("provider") != a.expected_provider: fail("provider does not match contract",errors)
    if a.expected_requested_model and meta.get("requested_model") != a.expected_requested_model: fail("requested model does not match contract",errors)
    if a.expected_observed_model and meta.get("model") != a.expected_observed_model: fail("observed model does not match contract",errors)
    if a.require_thread_id and not meta.get("thread_id"): fail("metrics have no required thread ID",errors)
    for field in a.require_metric:
        if meta.get(field) in (None, "", [], {}): fail(f"required metric is missing: {field}",errors)
    if errors:
        print("\n".join("ERROR: "+e for e in errors),file=sys.stderr); return 64
    print(json.dumps({"valid":True,"report":str(report),"report_sha256":sha(report),"source_sha256":sha(source),"provider":meta.get("provider"),"requested_model":meta.get("requested_model"),"observed_model":meta.get("model"),"thread_id":meta.get("thread_id")},ensure_ascii=False,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
