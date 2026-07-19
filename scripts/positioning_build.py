#!/usr/bin/env python3
"""Build data/positioning.json — insider + politician (smart money) channels.

Reads raw FMP MCP dumps committed under data/positioning_src/ (saved verbatim by
the Routine in scripts/positioning_refresh.md):

  fmp_insider_<TKR>.json  — mcp__FMP__insiderTrades output per name
  fmp_senate.json         — mcp__FMP__senate senate-trades feed
  fmp_house.json          — mcp__FMP__senate house-disclosure feed
  config.json             — {"trackedPoliticians": [...], "windowDays": 90}

and normalizes them into positioning.json, preserving the existing insider[]
contract the Risk tab renders ({ticker, direction, netInsiderShares, window})
while adding the classification layer the process requires:

  Insider rule (codified from the research notes): an open-market BUY is always
  discretionary — "there are many reasons to sell, but only one reason to buy".
  A SELL is TECHNICAL (not signal) when it is tax-withholding / an option
  exercise (codes F/M, or an S filed the same day as an M by the same insider),
  an award/gift/conversion (A/G/C/X/D-to-issuer), or a small trim (<10% of
  post-transaction holdings). Everything else is a DISCRETIONARY sell.

Every build also appends one row per (ticker, channel) per UTC day to
data/positioning_history.jsonl — the accumulation feed channel_accuracy.py
scores the insider/politician channels from.

Resilient by design: missing/empty positioning_src leaves the existing
positioning.json untouched; a malformed dump is skipped, not fatal. Stdlib only.
"""
import datetime
import glob
import json
import os
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
SRC = pathlib.Path(os.environ.get("POSITIONING_SRC", str(DATA / "positioning_src")))

TECHNICAL_CODES = {"F", "M", "A", "G", "C", "X", "D"}   # non-open-market Form 4 codes
SMALL_TRIM_PCT = 10.0                                    # sells below this % of holdings = technical
MAX_LATEST = 5                                           # transactions kept per insider card
MAX_POLITICIANS = 120                                    # rows kept in politicians[]


def _load(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text())
    except Exception as e:
        print(f"  ! skip {pathlib.Path(path).name}: {e}")
        return default


def _rows(doc):
    """FMP dumps arrive as a bare list or wrapped ({data|results|items: [...]})."""
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict):
        for k in ("data", "results", "items", "trades"):
            if isinstance(doc.get(k), list):
                return doc[k]
    return []


def _first(row, *keys):
    for k in keys:
        v = row.get(k)
        if v not in (None, ""):
            return v
    return None


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _code(row):
    """Form 4 transaction code from FMP's 'S-Sale' / 'P-Purchase' style field."""
    t = _first(row, "transactionType", "transactionCode", "type")
    return str(t).strip().upper()[:1] if t else None


# ── insider classification ────────────────────────────────────────────────────
def classify(row, same_day_m):
    """→ (classification, is_buy). The buy/sell asymmetry rule lives here."""
    code = _code(row)
    acq = str(_first(row, "acquistionOrDisposition", "acquisitionOrDisposition") or "").upper()
    if code == "P":
        return "discretionary_buy", True
    if code in TECHNICAL_CODES:
        return "technical", False
    if code == "S":
        key = (_first(row, "reportingName", "insiderName", "name"),
               _first(row, "transactionDate", "date"))
        if key in same_day_m:
            return "technical", False   # sell-to-cover on an option exercise
        transacted = _num(_first(row, "securitiesTransacted", "shares"))
        owned = _num(_first(row, "securitiesOwned", "sharesOwned"))
        if transacted and owned is not None:
            pct = transacted / (owned + transacted) * 100 if (owned + transacted) else None
            if pct is not None and pct < SMALL_TRIM_PCT:
                return "technical", False
        return "discretionary_sell", False
    # unknown/odd codes: signal only if it's an explicit open-market acquisition
    return ("discretionary_buy", True) if acq == "A" and code is None else ("technical", False)


def build_insiders(window_days):
    cards = []
    cutoff = (datetime.date.today() - datetime.timedelta(days=window_days)).isoformat()
    for path in sorted(glob.glob(str(SRC / "fmp_insider_*.json"))):
        ticker = pathlib.Path(path).stem.replace("fmp_insider_", "").upper()
        rows = [r for r in _rows(_load(path, [])) if isinstance(r, dict)]
        rows = [r for r in rows
                if (_first(r, "transactionDate", "date") or "9999") >= cutoff]
        if not rows:
            continue
        same_day_m = {(_first(r, "reportingName", "insiderName", "name"),
                       _first(r, "transactionDate", "date"))
                      for r in rows if _code(r) == "M"}
        buys = sells = disc_sells = tech_sells = 0
        net = 0.0
        latest = []
        for r in sorted(rows, key=lambda r: _first(r, "transactionDate", "date") or "",
                        reverse=True):
            cls, is_buy = classify(r, same_day_m)
            shares = _num(_first(r, "securitiesTransacted", "shares")) or 0.0
            price = _num(_first(r, "price", "transactionPrice"))
            owned = _num(_first(r, "securitiesOwned", "sharesOwned"))
            acq = str(_first(r, "acquistionOrDisposition", "acquisitionOrDisposition") or "").upper()
            if is_buy:
                buys += 1
                net += shares
            elif cls == "discretionary_sell":
                sells += 1
                disc_sells += 1
                net -= shares
            elif acq != "A":
                sells += 1
                tech_sells += 1          # technical flow excluded from the net signal
            # technical acquisitions (M exercises, A awards) are neither buys nor sells
            if len(latest) < MAX_LATEST:
                pct = (shares / (owned + shares) * 100
                       if shares and owned is not None and (owned + shares) else None)
                latest.append({
                    "date": _first(r, "transactionDate", "date"),
                    "insider": _first(r, "reportingName", "insiderName", "name"),
                    "role": _first(r, "typeOfOwner", "position", "officerTitle"),
                    "code": _code(r),
                    "shares": shares,
                    "value": round(shares * price, 0) if price else None,
                    "pctOfHoldings": round(pct, 1) if pct is not None else None,
                    "classification": cls,
                })
        signal = ("bullish" if buys else
                  "bearish" if disc_sells and net < 0 else "neutral")
        direction = "buying" if net > 0 else "selling" if net < 0 else "mixed"
        note_bits = []
        if buys:
            note_bits.append(f"{buys} open-market buy{'s' if buys != 1 else ''}")
        if sells:
            note_bits.append(f"{tech_sells} of {sells} sells classified technical "
                             f"(10b5-1 / RSU / option exercise / small trim)")
        cards.append({
            "ticker": ticker,
            "direction": direction,
            "netInsiderShares": round(net),
            "window": f"{window_days}d",
            "buys": buys, "sells": sells,
            "discretionarySells": disc_sells, "technicalSells": tech_sells,
            "signal": signal,
            "note": "; ".join(note_bits) or "no transactions in window",
            "latest": latest,
        })
    cards.sort(key=lambda c: ({"bullish": 0, "bearish": 1}.get(c["signal"], 2), c["ticker"]))
    return cards


# ── politicians ───────────────────────────────────────────────────────────────
def _universe_tickers():
    tickers = set()
    uni = _load(DATA / "universe.json", {})
    for r in uni.get("tickers", []):
        if r.get("ticker"):
            tickers.add(r["ticker"].split(" @")[0].upper())
    pos = _load(DATA / "positions.json", {"positions": []})
    for p in pos.get("positions", []):
        if p.get("ticker"):
            tickers.add(p["ticker"].split(" @")[0].upper())
    watch = _load(DATA / "altdata_src" / "watchlist.json", {})
    for w in watch.get("watchlist", []):
        if w.get("ticker"):
            tickers.add(w["ticker"].upper())
    return tickers


def _lag_days(tx, filed):
    try:
        return (datetime.date.fromisoformat(str(filed)[:10])
                - datetime.date.fromisoformat(str(tx)[:10])).days
    except Exception:
        return None


def build_politicians(tracked, window_days):
    universe = _universe_tickers()
    cutoff = (datetime.date.today() - datetime.timedelta(days=window_days)).isoformat()
    tracked_lc = [t.lower() for t in tracked]
    out = []
    for fname, chamber in (("fmp_senate.json", "Senate"), ("fmp_house.json", "House")):
        for r in _rows(_load(SRC / fname, [])):
            if not isinstance(r, dict):
                continue
            ticker = (_first(r, "symbol", "ticker") or "").split(" @")[0].upper()
            name = (_first(r, "representative", "senator", "name")
                    or " ".join(x for x in (r.get("firstName"), r.get("lastName")) if x))
            if not ticker or not name:
                continue
            tx_date = _first(r, "transactionDate", "txDate")
            if (tx_date or "9999") < cutoff:
                continue
            watched = ticker in universe or any(t in name.lower() for t in tracked_lc)
            if not watched:
                continue
            ttype = str(_first(r, "type", "transaction") or "").lower()
            transaction = ("buy" if "purchase" in ttype or ttype == "buy"
                           else "sell" if "sale" in ttype or "sell" in ttype else ttype or "?")
            filed = _first(r, "disclosureDate", "dateRecieved", "dateReceived", "filedDate")
            out.append({
                "name": name,
                "party": _first(r, "party"),
                "chamber": chamber,
                "ticker": ticker,
                "transaction": transaction,
                "amountRange": _first(r, "amount", "amountRange"),
                "txDate": str(tx_date)[:10] if tx_date else None,
                "filedDate": str(filed)[:10] if filed else None,
                "disclosureLagDays": _lag_days(tx_date, filed),
                "note": _first(r, "assetDescription", "comment", "owner"),
            })
    out.sort(key=lambda p: p["txDate"] or "", reverse=True)
    return out[:MAX_POLITICIANS]


# ── history feed for channel_accuracy ─────────────────────────────────────────
def append_history(insiders, politicians):
    path = DATA / "positioning_history.jsonl"
    today = datetime.date.today().isoformat()
    if path.exists():
        for line in path.read_text().splitlines():
            if line.strip() and json.loads(line).get("date") == today:
                return 0   # once per day; the Routine may rerun
    rows = []
    for c in insiders:
        rows.append({"date": today, "ticker": c["ticker"], "channel": "insider",
                     "signal": c["signal"], "net": c["netInsiderShares"]})
    by_ticker = {}
    for p in politicians:
        d = by_ticker.setdefault(p["ticker"], 0)
        by_ticker[p["ticker"]] = d + (1 if p["transaction"] == "buy"
                                      else -1 if p["transaction"] == "sell" else 0)
    for t, netn in by_ticker.items():
        rows.append({"date": today, "ticker": t, "channel": "politician",
                     "signal": "bullish" if netn > 0 else "bearish" if netn < 0 else "neutral",
                     "net": netn})
    if rows:
        with path.open("a") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    return len(rows)


# ── assemble ──────────────────────────────────────────────────────────────────
def build():
    cfg = _load(SRC / "config.json", {})
    window_days = cfg.get("windowDays", 90)
    tracked = cfg.get("trackedPoliticians", [])

    has_src = (glob.glob(str(SRC / "fmp_insider_*.json"))
               or (SRC / "fmp_senate.json").exists() or (SRC / "fmp_house.json").exists())
    existing = _load(DATA / "positioning.json", {})
    if not has_src:
        print("positioning_src/ has no FMP dumps — existing positioning.json left untouched")
        return None

    insiders = build_insiders(window_days)
    politicians = build_politicians(tracked, window_days)
    out = {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        # 13F / COT stay whatever the last enrich run wrote until src dumps exist for them
        "institutional": existing.get("institutional", []),
        "insider": insiders,
        "politicians": politicians,
        "cot": existing.get("cot", []),
    }
    (DATA / "positioning.json").write_text(json.dumps(out, indent=1) + "\n")
    n_hist = append_history(insiders, politicians)
    print(f"positioning.json: {len(insiders)} insider cards, {len(politicians)} politician rows "
          f"(+{n_hist} history rows)")
    return out


if __name__ == "__main__":
    build()
