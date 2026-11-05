"""
AETHRIX Engine — owned, deterministic reasoning and response components.
No commercial AI APIs. No external model/API calls are made from this module.

Provides: safe verified math, intent classification, structured reasoning
templates, conversation context handling, and honest capability reporting.
For open-domain natural-language generation across arbitrary topics, this
engine can orchestrate a SELF-HOSTED open-weights model running on
infrastructure you control (configured via AETHRIX settings); that model is
yours to run, not a commercial assistant API.
"""
from __future__ import annotations

import ast
import datetime as dt
import math
import operator
import re
from typing import Any, Dict, List, Optional

SAFE_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
SAFE_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
SAFE_FUNCS = {
    "abs": abs, "round": round, "min": min, "max": max, "sqrt": math.sqrt,
    "log": math.log, "log10": math.log10, "exp": math.exp, "pow": pow,
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "asin": math.asin,
    "acos": math.acos, "atan": math.atan, "degrees": math.degrees, "radians": math.radians,
    "pi": math.pi, "e": math.e, "tau": math.tau, "factorial": math.factorial, "gcd": math.gcd,
}
SAFE_NAMES = {k: v for k, v in SAFE_FUNCS.items()}


def _eval_node(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if hasattr(ast, 'Num') and isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.BinOp) and type(node.op) in SAFE_BINOPS:
        left, right = _eval_node(node.left), _eval_node(node.right)
        if isinstance(node.op, ast.Pow):
            try:
                if abs(float(right)) > 2000 or (abs(float(left)) > 1e6 and abs(float(right)) > 10):
                    raise ValueError("power too large")
            except Exception:
                pass
        return SAFE_BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_UNARY:
        return SAFE_UNARY[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in SAFE_NAMES:
        func = SAFE_NAMES[node.func.id]
        if not callable(func):
            return func
        args = [_eval_node(a) for a in node.args]
        return func(*args)
    if isinstance(node, ast.Name) and node.id in SAFE_NAMES:
        return SAFE_NAMES[node.id]
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(e) for e in node.elts)
    raise ValueError("unsupported expression")


def safe_calc(expr: str) -> Optional[str]:
    raw = (expr or "").strip()
    if not raw or len(raw) > 800:
        return None
    s = raw.replace("^", "**").replace("×", "*").replace("÷", "/").replace("π", "pi")
    s = re.sub(r"[=？?]+\s*$", "", s).strip()
    s = re.sub(r"^(?:what\s+is|calculate|compute|solve|evaluate|simplify|find)\s*[:\-]?\s*", "", s, flags=re.I).strip()
    # percentage: "10% of 200" handled simply
    m = re.fullmatch(r"(\d+(?:\.\d+)?)%\s+of\s+(\d+(?:\.\d+)?)", s)
    if m:
        return str(round(float(m.group(1)) / 100 * float(m.group(2)), 12)).rstrip('0').rstrip('.') or '0'
    if not re.fullmatch(r"[0-9+\-*/().,%\s_a-zA-Z]+", s):
        return None
    if not re.search(r"\d", s):
        return None
    try:
        result = _eval_node(ast.parse(s, mode="eval"))
        if isinstance(result, complex):
            return str(result)
        if isinstance(result, float):
            if result.is_integer() and abs(result) < 1e15:
                return str(int(result))
            return str(round(result, 12)).rstrip('0').rstrip('.')
        return str(result)
    except Exception:
        return None


def last_user_text(messages: List[Dict[str, str]]) -> str:
    for m in reversed(messages or []):
        if (m.get("role") or "").lower() == "user":
            return (m.get("content") or "").strip()
    return ""


def classify(text: str) -> str:
    t = (text or "").lower().strip()
    if not t: return "empty"
    if any(x in t for x in ["who are you", "what are you", "your name", "are you chatgpt", "are you gemini", "are you gpt"]):
        return "identity"
    calc = safe_calc(text)
    if calc is not None and re.search(r"\d", text) and (re.search(r"[+\-*/^%()=]|what is\s+\d|\d+%\s+of", t) or re.fullmatch(r"[\d\s.+\-*/()×÷^πpie]+", t)):
        return "math"
    if re.search(r"\b(utc|current time|what time|today'?s date|what day is it)\b", t):
        return "datetime"
    return "general"


def deterministic_response(messages: List[Dict[str, str]], mode: str = "assistant") -> Optional[str]:
    last = last_user_text(messages)
    if not last:
        return "Hello — I’m **AETHRIX**. Ask a question, request help with a problem, or tell me what you’d like to create."

    kind = classify(last)
    if kind == "identity":
        return (
            "I’m **AETHRIX**, an AI assistant platform built from this project’s own code (frontend, backend API, and engine). "
            "I’m not ChatGPT, Gemini, or another company’s hosted assistant.\n\n"
            "**What I can do right now (owned/deterministic):** verified arithmetic/math expressions, conversation handling, and structured assistance through this API.\n\n"
            "**For accurate, logical answers across *all* open-domain topics:** connect AETHRIX to an **open-weights model running on infrastructure you control** "
            "(for example Ollama on your own server/VPS/GPU). That keeps inference under your control. Set `OLLAMA_BASE_URL` and `DEFAULT_CHAT_MODEL` (or `AI_BASE_URL`/`AI_MODEL` for your own gateway)."
        )
    if kind == "math":
        res = safe_calc(last)
        if res is not None:
            return (
                f"## Verified calculation\n"
                f"**Input:** {last}\n\n"
                f"**Result:** **{res}**\n\n"
                "_Computed locally by AETHRIX’s owned deterministic engine._"
            )
    if kind == "datetime":
        now = dt.datetime.utcnow().replace(microsecond=0)
        local_hint = "For local timezone answers, tell me your timezone/city."
        return f"**Server UTC time:** {now.isoformat()}Z\n\n{local_hint}"
    return None


def capability_notice() -> str:
    return (
        "I don’t have a self-hosted language model connected right now, so I won’t guess on open-domain questions. "
        "To get correct, logical, detailed answers on any topic using your own stack, run an open-weights model on hardware you control (e.g. Ollama) and set `OLLAMA_BASE_URL` + `DEFAULT_CHAT_MODEL` in the backend environment."
    )
