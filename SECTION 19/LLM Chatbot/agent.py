"""
agent.py — ReAct-style tool-calling agent powered by Ollama.

Flow:
  User message
    → Agent.run()
      → LLM thinks (stream)
      → detects <tool>…</tool> calls
      → executes tool
      → feeds result back as observation
      → repeats until <final>…</final> or max_steps
    → yields AgentEvent objects consumed by the Streamlit UI
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generator, Optional
from enum import Enum

import requests


# Event types

class EventKind(str, Enum):
    THOUGHT    = "thought"      # streaming LLM reasoning token
    TOOL_CALL  = "tool_call"    # agent decided to call a tool
    TOOL_RESULT= "tool_result"  # tool returned a result
    FINAL      = "final"        # streaming final answer token
    ERROR      = "error"        # something went wrong
    DONE       = "done"         # agent finished


@dataclass
class AgentEvent:
    kind:    EventKind
    content: str = ""
    meta:    dict = field(default_factory=dict)


# Built-in tools

def tool_calculator(expression: str) -> str:
    """Safely evaluate a math expression."""
    try:
        # Normalize: strip whitespace, convert ^ to **, remove thousands commas
        expr = expression.strip().replace("^", "**").replace(",", "")
        # Allow digits, operators, parens, dot, space, * (covers **)
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expr):
            return f"Error: unsupported characters in expression: {expr!r}"
        result = eval(expr, {"__builtins__": {}})   # nosec
        # Format nicely: int if whole number
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return str(result)
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception as e:
        return f"Error: {e}"


def tool_datetime(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Return the current date/time."""
    return datetime.now().strftime(fmt)


def tool_search_wikipedia(query: str) -> str:
    """Fetch a short Wikipedia summary."""
    try:
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(query)
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            data = r.json()
            return data.get("extract", "No summary found.")[:600]
        return f"Wikipedia returned status {r.status_code}"
    except Exception as e:
        return f"Error fetching Wikipedia: {e}"


def tool_web_fetch(url: str) -> str:
    """Return the first 800 chars of a web page's text content."""
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "OllamaAgent/1.0"})
        # crude text extraction
        text = re.sub(r"<[^>]+>", " ", r.text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:800]
    except Exception as e:
        return f"Error fetching URL: {e}"


TOOLS: dict[str, dict] = {
    "calculator": {
        "fn":          tool_calculator,
        "description": "Evaluate a math expression. Input: arithmetic string e.g. '(3+5)*2'.",
        "param":       "expression",
    },
    "datetime": {
        "fn":          tool_datetime,
        "description": "Get current date and time. Input: optional strftime format string.",
        "param":       "fmt",
    },
    "wikipedia": {
        "fn":          tool_search_wikipedia,
        "description": "Get a Wikipedia summary for a topic. Input: topic name.",
        "param":       "query",
    },
    "web_fetch": {
        "fn":          tool_web_fetch,
        "description": "Fetch text content from a URL. Input: full URL.",
        "param":       "url",
    },
}


def build_tool_docs() -> str:
    lines = []
    for name, info in TOOLS.items():
        lines.append(f"- {name}({info['param']}): {info['description']}")
    return "\n".join(lines)


# System prompt

SYSTEM_PROMPT = f"""You are a tool-calling agent. You MUST use the exact XML format shown below. No explanations, no plans — just tags.

TOOLS:
{build_tool_docs()}

RULES:
- To use a tool output EXACTLY: <tool>TOOLNAME|ARGUMENT</tool>
- After receiving <observation>RESULT</observation> continue to next step.
- To give the final answer output EXACTLY: <final>ANSWER</final>
- Never describe what you will do. Output the tag immediately.
- Do not output any text before or after the tag on that line.

EXAMPLES:
Q: What is 6 * 7?
A: <tool>calculator|6 * 7</tool>
<observation>42</observation>
<final>6 * 7 = 42</final>

Q: What day is it?
A: <tool>datetime|%A %d %B %Y</tool>
<observation>Thursday 19 March 2026</observation>
<final>Today is Thursday 19 March 2026.</final>
"""


# Ollama streaming helper

OLLAMA_URL = "http://localhost:11434/api/chat"


def stream_ollama(
    messages: list[dict],
    model: str,
    temperature: float = 0.6,
    stop: Optional[list[str]] = None,
) -> Generator[str, None, None]:
    """Yields text tokens from Ollama streaming API."""
    payload = {
        "model":    model,
        "messages": messages,
        "stream":   True,
        "options":  {
            "temperature": temperature,
            "num_ctx":     4096,
            "stop":        stop or [],
        },
    }
    with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as resp:
        if not resp.ok:
            body = resp.text[:300]
            raise RuntimeError(
                f"Ollama returned {resp.status_code}.\n{body}\n\n"
                f"Fix: run  ollama pull {model}  or pick a different model in the sidebar."
            )
        for line in resp.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            token = chunk.get("message", {}).get("content", "")
            if token:
                yield token
            if chunk.get("done"):
                break


# Helpers

def _clean_answer(text: str) -> str:
    """Remove markdown artifacts, leading >, XML tags, extra blank lines."""
    # strip any remaining XML tags
    text = re.sub(r"<[^>]+>", "", text)
    # strip leading > (markdown blockquote bleed)
    lines = [l.lstrip("> ").rstrip() for l in text.splitlines()]
    # drop empty leading/trailing lines
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


# Agent

class Agent:
    def __init__(
        self,
        model:       str   = "llama3.2",
        temperature: float = 0.6,
        max_steps:   int   = 8,
    ):
        self.model       = model
        self.temperature = temperature
        self.max_steps   = max_steps

    def run(
        self,
        user_message: str,
        history: list[dict] | None = None,
    ) -> Generator[AgentEvent, None, None]:
        """
        Main entry point. Yields AgentEvent objects.
        history: list of {"role": "user"|"assistant", "content": "..."}
        """
        messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        # Cap temperature — small models follow format better at low temp
        effective_temp = min(self.temperature, 0.2)

        # Track collected tool results so we can synthesize answer directly
        collected: list[str] = []   # "tool(arg) => result"
        seen_calls: set[str] = set()  # detect infinite loops

        for step in range(self.max_steps):
            # ── Stream LLM response ──────────────────────────────────
            buffer = ""
            try:
                for token in stream_ollama(messages, self.model, effective_temp):
                    buffer += token
                    # stream thought tokens
                    if "<tool>" not in buffer and "<final>" not in buffer:
                        yield AgentEvent(kind=EventKind.THOUGHT, content=token)
                    # stream final tokens
                    if "<final>" in buffer and "</final>" not in buffer:
                        if token and "<final>" not in token:
                            yield AgentEvent(kind=EventKind.FINAL, content=token)
                    # stop once tag closes
                    if "</tool>" in buffer or "</final>" in buffer:
                        break

            except requests.exceptions.ConnectionError:
                yield AgentEvent(kind=EventKind.ERROR,
                    content="Cannot connect to Ollama. Is it running? (`ollama serve`)")
                yield AgentEvent(kind=EventKind.DONE)
                return
            except Exception as e:
                yield AgentEvent(kind=EventKind.ERROR, content=str(e))
                yield AgentEvent(kind=EventKind.DONE)
                return

            # ── Check for <final> ────────────────────────────────────
            final_match = re.search(r"<final>(.*?)</final>", buffer, re.DOTALL)
            if final_match:
                answer = _clean_answer(final_match.group(1))
                yield AgentEvent(kind=EventKind.FINAL, content=answer)
                yield AgentEvent(kind=EventKind.DONE, meta={"steps": step + 1})
                return

            # ── Check for <tool> ─────────────────────────────────────
            tool_match = re.search(r"<tool>(.*?)</tool>", buffer, re.DOTALL)

            # Prose fallback: model wrote tool name without tags
            if not tool_match:
                for tname in TOOLS:
                    m = re.search(r"\b" + tname + r"\(([^)]+)\)", buffer, re.IGNORECASE)
                    if m:
                        buffer = f"<tool>{tname}|{m.group(1)}</tool>"
                        tool_match = re.search(r"<tool>(.*?)</tool>", buffer)
                        break
                    pat = r"\b" + tname + r"\b" + r".*?[`\'\"](.*?)[`\'\"]"
                    m2 = re.search(pat, buffer, re.IGNORECASE)
                    if m2:
                        buffer = f"<tool>{tname}|{m2.group(1)}</tool>"
                        tool_match = re.search(r"<tool>(.*?)</tool>", buffer)
                        break

            if tool_match:
                raw = tool_match.group(1).strip()
                tool_name, arg = (raw.split("|", 1) + [""])[:2]
                tool_name = tool_name.strip()
                arg       = arg.strip()

                call_key = f"{tool_name}|{arg}"

                # ── Loop detection: same call seen before → synthesize now ──
                if call_key in seen_calls:
                    if collected:
                        answer = self._synthesize(user_message, collected)
                        yield AgentEvent(kind=EventKind.FINAL, content=answer)
                        yield AgentEvent(kind=EventKind.DONE, meta={"steps": step + 1})
                    else:
                        yield AgentEvent(kind=EventKind.ERROR,
                            content="Agent looped without results. Try a simpler query.")
                        yield AgentEvent(kind=EventKind.DONE)
                    return

                seen_calls.add(call_key)

                yield AgentEvent(kind=EventKind.TOOL_CALL,
                    content=f"{tool_name}({arg})",
                    meta={"tool": tool_name, "arg": arg})

                # Execute tool
                t0 = time.time()
                if tool_name in TOOLS:
                    try:
                        result = TOOLS[tool_name]["fn"](arg)
                    except Exception as e:
                        result = f"Tool error: {e}"
                else:
                    result = f"Unknown tool '{tool_name}'"
                elapsed = time.time() - t0

                yield AgentEvent(kind=EventKind.TOOL_RESULT,
                    content=result,
                    meta={"tool": tool_name, "elapsed": round(elapsed, 3)})

                collected.append(f"{tool_name}({arg}) => {result}")

                # Feed result back — instruct to continue or finalize
                messages.append({"role": "assistant", "content": buffer})
                messages.append({
                    "role": "user",
                    "content": (
                        f"<observation>{result}</observation>\n"
                        "If you still need another tool call it now with <tool>NAME|ARG</tool>.\n"
                        "If you have everything, reply with ONLY: <final>complete answer here</final>"
                    ),
                })
                continue

            # ── Free text with no tags → treat as final ──────────────
            if buffer.strip():
                yield AgentEvent(kind=EventKind.FINAL, content=_clean_answer(buffer))
                yield AgentEvent(kind=EventKind.DONE, meta={"steps": step + 1})
                return

        # ── Max steps hit → synthesize from collected results ────────
        if collected:
            answer = self._synthesize(user_message, collected)
            yield AgentEvent(kind=EventKind.FINAL, content=answer)
            yield AgentEvent(kind=EventKind.DONE, meta={"steps": self.max_steps})
        else:
            yield AgentEvent(kind=EventKind.ERROR,
                content="Agent could not produce an answer. Try rephrasing.")
            yield AgentEvent(kind=EventKind.DONE)

    def _synthesize(self, question: str, collected: list[str]) -> str:
        """Directly build a final answer from tool results without asking LLM again."""
        facts = "\n".join(f"- {c}" for c in collected)
        # Ask LLM one last time with ONLY the facts — no tool loop possible
        prompt = (
            f"Question: {question}\n\n"
            f"Facts gathered:\n{facts}\n\n"
            "Answer the question in one clear sentence using only the facts above."
        )
        messages = [
            {"role": "system", "content": "You are a concise assistant. Answer directly."},
            {"role": "user",   "content": prompt},
        ]
        answer = ""
        try:
            for token in stream_ollama(messages, self.model, 0.1):
                answer += token
                # strip any tags the model might add
                answer = re.sub(r"<[^>]+>", "", answer)
        except Exception:
            pass
        return _clean_answer(answer) or "\n".join(c.split("=>")[-1].strip() for c in collected)
