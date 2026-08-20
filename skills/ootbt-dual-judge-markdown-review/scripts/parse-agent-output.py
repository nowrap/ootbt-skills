#!/usr/bin/env python
"""Extract final Markdown and normalized telemetry from Codex or Claude output."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
from typing import Any


def num(v: Any) -> int | float:
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else 0


def jsonl(path: Path) -> list[dict[str, Any]]:
    rows=[]
    for n,line in enumerate(path.read_text(encoding="utf-8", errors="strict").splitlines(),1):
        if not line.strip(): continue
        try: value=json.loads(line)
        except json.JSONDecodeError as e: raise ValueError(f"invalid JSONL line {n}: {e}") from e
        if isinstance(value,dict): rows.append(value)
    return rows


def codex(path: Path):
    rows=jsonl(path); texts=[]; thread=None; inp=cache=out=0; completed=False
    for row in rows:
        if row.get("type")=="thread.started": thread=row.get("thread_id")
        item=row.get("item") if isinstance(row.get("item"),dict) else {}
        if row.get("type")=="item.completed" and item.get("type")=="agent_message" and isinstance(item.get("text"),str): texts.append(item["text"])
        if row.get("type")=="turn.completed":
            completed=True; u=row.get("usage") if isinstance(row.get("usage"),dict) else {}
            inp+=int(num(u.get("input_tokens"))); cache+=int(num(u.get("cached_input_tokens"))); out+=int(num(u.get("output_tokens")))
    if not texts: raise ValueError("Codex has no final agent message")
    if not completed: raise ValueError("Codex has no turn.completed event")
    return texts[-1], {"provider":"openai-codex","model":None,"thread_id":thread,"input_tokens":max(inp-cache,0),"cached_input_tokens":cache,"output_tokens":out,"total_tokens":max(inp-cache,0)+cache+out,"cost_usd":None,"terminal_completion":True}


def claude(path: Path):
    try: data=json.loads(path.read_text(encoding="utf-8",errors="strict"))
    except json.JSONDecodeError as e: raise ValueError(f"invalid Claude JSON: {e}") from e
    if not isinstance(data,dict) or not isinstance(data.get("result"),str): raise ValueError("Claude has no textual result")
    if data.get("is_error") is True: raise ValueError("Claude marked run as error")
    usage=data.get("modelUsage") if isinstance(data.get("modelUsage"),dict) else {}
    inp=cache=out=0; cost=0.0; models=[]
    for model,v in usage.items():
        if not isinstance(v,dict): continue
        models.append(str(model)); inp+=int(num(v.get("inputTokens")))+int(num(v.get("cacheCreationInputTokens"))); cache+=int(num(v.get("cacheReadInputTokens"))); out+=int(num(v.get("outputTokens"))); cost+=float(num(v.get("costUSD")))
    return data["result"], {"provider":"anthropic","model":",".join(models) if models else None,"models":models,"input_tokens":inp if usage else None,"cached_input_tokens":cache if usage else None,"output_tokens":out if usage else None,"total_tokens":inp+cache+out if usage else None,"cost_usd":data.get("total_cost_usd",cost if usage else None),"duration_ms":data.get("duration_ms"),"terminal_completion":True,"permission_denials":data.get("permission_denials")}


def main():
    if len(sys.argv)!=5 or sys.argv[1] not in {"codex","claude"}:
        print("Usage: parse-agent-output.py <codex|claude> <raw> <report> <metrics>",file=sys.stderr); return 2
    kind,raw,report,metrics=sys.argv[1:]
    try:
        text,meta=(codex if kind=="codex" else claude)(Path(raw))
        requested_model = os.environ.get("DUAL_JUDGE_MODEL")
        if requested_model:
            meta["requested_model"] = requested_model
        requested_reasoning_effort = os.environ.get("DUAL_JUDGE_REASONING_EFFORT")
        if requested_reasoning_effort:
            meta["requested_reasoning_effort"] = requested_reasoning_effort
        telemetry_fields = {
            "execution_environment": "DUAL_JUDGE_EXECUTION_ENVIRONMENT",
            "host_os": "DUAL_JUDGE_HOST_OS",
            "wsl_capability_status": "DUAL_JUDGE_WSL_CAPABILITY_STATUS",
            "wsl_distribution": "DUAL_JUDGE_WSL_DISTRO",
            "wsl_kernel": "DUAL_JUDGE_WSL_KERNEL",
            "node_version": "DUAL_JUDGE_NODE_VERSION",
            "codex_cli_version": "DUAL_JUDGE_CODEX_VERSION",
            "wsl_repo_path": "DUAL_JUDGE_WSL_REPO_PATH",
        }
        for field, environment_variable in telemetry_fields.items():
            value = os.environ.get(environment_variable)
            if value:
                meta[field] = value
        if not text.strip(): raise ValueError("empty final report")
        Path(report).parent.mkdir(parents=True,exist_ok=True)
        Path(report).write_text(text.rstrip()+"\n",encoding="utf-8",newline="\n")
        Path(metrics).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    except (OSError,ValueError) as e:
        print(f"ERROR: {e}",file=sys.stderr); return 64
    return 0
if __name__=="__main__": raise SystemExit(main())
