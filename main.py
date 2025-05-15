#!/usr/bin/env python3
"""
LLM Query-Recommender
"""
import os
import re, ast, pickle, httpx, spacy
from pathlib import Path
from typing import List, Dict, Any, Optional
from ollama import Client
import spacy
# ── initialise ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
spacy.cli.download("en_core_web_sm")
nlp = spacy.load("en_core_web_sm")

# lemma mappings → intent-symbol map
LEMMA_MAPPING = {
    # ── aggregations
    "average":"AGGREGATE","mean":"AGGREGATE","median":"AGGREGATE","mode":"AGGREGATE",
    "sum":"AGGREGATE","total":"AGGREGATE","count":"AGGREGATE",
    "min":"AGGREGATE","minimum":"AGGREGATE","max":"AGGREGATE","maximum":"AGGREGATE",
    "percent":"AGGREGATE","percentage":"AGGREGATE",
    # ── difference / change
    "difference":"DIFFERENCE","delta":"DIFFERENCE","change":"DIFFERENCE",
    "increase":"DIFFERENCE","decrease":"DIFFERENCE",
    # ── trend / forecast
    "trend":"TREND","growth":"TREND","decline":"TREND",
    "forecast":"TREND","projection":"TREND",
    # ── sorting / ranking
    "sort":"SORT","order":"SORT","rank":"SORT",
    "top":"SORT","bottom":"SORT","highest":"SORT","lowest":"SORT",
    # ── selection / display
    "list":"SELECT","show":"SELECT","display":"SELECT","get":"SELECT",
    "return":"SELECT","provide":"SELECT","fetch":"SELECT",
    # ── filtering
    "filter":"FILTER","where":"FILTER","with":"FILTER","having":"FILTER",
    # ── grouping
    "group":"GROUP_BY","bucket":"GROUP_BY","cluster":"GROUP_BY",
    "segment":"GROUP_BY","by":"GROUP_BY",
    # ── arithmetic
    "add":"ARITHMETIC","plus":"ARITHMETIC","subtract":"ARITHMETIC","minus":"ARITHMETIC",
    "multiply":"ARITHMETIC","times":"ARITHMETIC","divide":"ARITHMETIC","ratio":"ARITHMETIC",
    # ── attribute facts
    "height":"ATTRIBUTE","weight":"ATTRIBUTE","length":"ATTRIBUTE","width":"ATTRIBUTE",
    "depth":"ATTRIBUTE","distance":"ATTRIBUTE","area":"ATTRIBUTE","volume":"ATTRIBUTE",
    "size":"ATTRIBUTE","population":"ATTRIBUTE","density":"ATTRIBUTE",
    "temperature":"ATTRIBUTE","speed":"ATTRIBUTE","duration":"ATTRIBUTE","time":"ATTRIBUTE",
    "cost":"ATTRIBUTE","price":"ATTRIBUTE","salary":"ATTRIBUTE",
    "revenue":"ATTRIBUTE","profit":"ATTRIBUTE","age":"ATTRIBUTE","capital": "ATTRIBUTE",
    # ── titles / roles
    "president":"TITLE","prime":"TITLE","minister":"TITLE","king":"TITLE",
    "queen":"TITLE","ceo":"TITLE","founder":"TITLE","author":"TITLE"
}

with open(BASE_DIR / "models" / "ambiguity_clf.pkl", "rb") as f:
    ambiguity_clf = pickle.load(f)


ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
oai = Client(base_url=ollama_host)
LLM_MODEL = "llama3.1:latest"

CLARIFY_PROMPT = [
    {"role":"system","content":"You ask concise clarifying questions for ambiguous queries."},
    {"role":"user","content":"Show me data."},
    {"role":"assistant","content":"Which data specifically do you want to see?"}
]


# ── central router ------------------------------------------------------------
def handle(q_raw: str) -> Dict[str, Any]:
    q = q_raw.strip()

    # literal sort / group first
    for fn in (sort, group_by):
        res = fn(q)
        if res is not None:
            return {"status":"answered","answer":res}

    # WH-question → direct LLM
    if re.match(r"^(who|what|where|when|why|how)\\b", q, re.I):
        return {"status":"answered",
                "answer": ask_llm([
                    {"role":"system","content":"You answer questions directly."},
                    {"role":"user","content":q}
                ])}

    parsed = parse_query(q)

    # single ATTRIBUTE fact
    if parsed["symbols"] == ["ATTRIBUTE"]:
        return {"status":"answered",
                "answer": ask_llm([
                    {"role":"system","content":"You answer factual questions."},
                    {"role":"user","content":q}
                ])}

    # unknown words
    jargon = unknown_terms(q, parsed)
    if jargon:
        asks = ask_llm([
            {"role":"system","content":"Ask one concise clarifier per unknown word."},
            {"role":"user","content":f"Unknown words: {', '.join(jargon)}"}
        ]).splitlines()
        return {"status":"ambiguous","questions":[x.strip() for x in asks if x.strip()]}

    # ambiguity classifier
    if ambiguous(parsed):
        lines = ask_llm(CLARIFY_PROMPT + [{"role":"user","content":q}]).splitlines()
        return {"status":"ambiguous","questions":[l.strip() for l in lines if l.strip()]}

    # direct answer
    return {"status":"answered",
            "answer": ask_llm([
                {"role":"system","content":"You answer questions directly."},
                {"role":"user","content":q}
            ])}

# ── spaCy parse & helpers -----------------------------------------------------
def parse_query(q: str) -> Dict[str, Any]:
    doc = nlp(q)
    symbols = [LEMMA_MAPPING[t.lemma_.lower()] for t in doc if t.lemma_.lower() in LEMMA_MAPPING]
    entities = [e.text for e in doc.ents]
    return {"symbols": symbols, "entities": entities}

def unknown_terms(q: str, parsed: Dict[str, Any]) -> List[str]:
    ents = set(parsed["entities"])
    return [
        t.text for t in nlp(q)
        if (t.is_alpha and not t.is_stop and t.pos_ in {"NOUN","PROPN"}
            and t.lemma_.lower() not in LEMMA_MAPPING and t.text not in ents)
    ]

def ambiguous(parsed: Dict[str, Any]) -> bool:
    sy, n = parsed["symbols"], len(parsed["symbols"])
    vec = [n, sum(sy.count(x) > 1 for x in sy)/n if n else 0.0,
           float(bool(parsed["entities"]))]
    return bool(ambiguity_clf.predict([vec])[0])

# ── helper to chat with llama-3 ───────────────────────────────────────────────
def ask_llm(msgs: List[dict]) -> str:
    raw = oai.chat(model=LLM_MODEL, messages=msgs)
    return raw["message"]["content"].strip() if isinstance(raw, dict) else raw.message.content.strip()

# ── literal “sort …” handler --------------------------------------------------
def sort(q: str) -> Optional[Any]:
    m = re.search(r"sort.*\[(.*)]\s+in\s+(ascending|descending)", q, re.I)
    if not m:
        if re.search(r"\b(sort|order)\b", q, re.I):
            return "Syntax tip → Sort the list [1,3,2] in ascending order."
        return None
    nums, direction = m.group(1), m.group(2).lower()
    try:
        arr = ast.literal_eval(f"[{nums}]")
        return sorted(arr, reverse=(direction == "descending"))
    except Exception:
        return "Couldn't parse the list; please use JSON-style numbers."

# ── literal “group by …” handler ---------------------------------------------
def group_by(q: str) -> Optional[Any]:
    m = re.search(r"group\s+by\s+(\w+)\s*:\s*(\[[^\]]+\])", q, re.I)
    if not m:
        if re.search(r"\bgroup\s+by\b", q, re.I):
            return "Syntax tip → Group by dept: [{'name':'A','dept':'HR'}, …]"
        return None
    field, literal = m.group(1), m.group(2)
    try:
        items = ast.literal_eval(literal)
        if not (isinstance(items, list) and all(isinstance(r, dict) for r in items)):
            raise ValueError
        out: Dict[Any, List[Any]] = {}
        for rec in items:
            out.setdefault(rec.get(field), []).append(rec)
        return out
    except Exception:
        return "Couldn't parse the list — check the JSON syntax."

# ── simple REPL ---------------------------------------------------------------
if __name__ == "__main__":
    print("Query-Recommender  (type 'exit' to quit)\n")
    while True:
        query = input("Query: ").strip()
        if query.lower() == "exit":
            break
        result = handle(query)
        if result["status"] == "answered":
            print("\nAnswer:\n", result["answer"], "\n")
        else:
            print("\nNeed clarification:")
            for i, line in enumerate(result["questions"], 1):
                print(f" {i}. {line}")
            print()