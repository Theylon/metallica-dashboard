#!/usr/bin/env python3
"""Build data/positioning.json — insider + institutional (smart money) channels.

Reads raw TrueNorth MCP dumps committed under data/positioning_src/ (saved
verbatim by the Routine in scripts/positioning_refresh.md):

  truenorth_insider_<TKR>.json  — mcp__TrueNorth__financial_insider_trades per name
  truenorth_13f_<TKR>.json      — mcp__TrueNorth__financial_institutional_ownership per name
  config.json                   — {"windowDays": 90}

and normalizes them into positioning.json, preserving the existing insider[]
contract the Risk tab renders ({ticker, direction, netInsiderShares, window})
while adding the classification layer the process requires:

  Insider rule (codified from the research notes): an open-market BUY is always
  discretionary — "there are many reasons to sell, but only one reason to buy".
  A SELL is TECHNICAL (not signal) when it is tax-withholding / an option
  exercise (codes F/M, or an S filed the same day as an M by the same insider),
  an award/gift/conversion (A/G/C/X/D-to-issuer), or a small trim (<10% of
  post-transaction holdings). Everything else is a DISCRETIONARY sell.

TrueNorth serves raw SEC Form 4 rows — single-letter transaction codes and
post-transaction holdings, the same semantics this classifier was written
against — so the dumps normalize by key rename alone (_norm_insider below).

Every build also appends one row per (ticker, channel) per UTC day to
data/positioning_history.jsonl — the accumulation feed channel_accuracy.py
scores the insider channel from.

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
MAX_HOLDERS = 20                                         # 13F holders summarized per name


def _load(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text())
    except Exception as e:
        print(f"  ! skip {pathlib.Path(path).name}: {e}")
        return default


def _rows(doc):
    """Dumps arrive as a bare list or wrapped ({insider_trades|holders|data: [...]})."""
    if isinstance(doc, list):
        return doc
    if isinstance(doc, dict):
        for k in ("insider_trades", "holders", "data", "results", "items", "trades"):
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
    """Form 4 transaction code — 'S', or an 'S-Sale' / 'P-Purchase' style field."""
    t = _first(row, "transactionType", "transactionCode", "type")
    return str(t).strip().upper()[:1] if t else None


def _role(row):
    """Insider role string from TrueNorth's boolean flags (falls back to a label)."""
    label = _first(row, "typeOfOwner", "position", "officerTitle")
    if label:
        return label
    bits = []
    if row.get("is_officer"):
        bits.append(row.get("officer_title") or "Officer")
    if row.get("is_director"):
        bits.append("Director")
    if row.get("is_ten_percent_owner"):
        bits.append("10% owner")
    return ", ".join(bits) or None


def _norm_insider(row):
    """TrueNorth Form 4 row → the canonical shape classify()/build_insiders() read.

    A pure key rename: TrueNorth already serves single-letter transaction codes
    and *post*-transaction holdings, which is exactly what the small-trim rule
    in classify() assumes (pct = transacted / (owned + transacted)).
    """
    if not isinstance(row, dict):
        return None
    if "transaction_code" not in row:
        return row          # already canonical (or a shape we don't recognise)
    return {
        "transactionDate": row.get("transaction_date"),
        "reportingName": row.get("reporting_owner_name"),
        "transactionCode": row.get("transaction_code"),
        "securitiesTransacted": row.get("transaction_shares"),
        "price": row.get("transaction_price_per_share"),
        "securitiesOwned": row.get("shares_owned_following_transaction"),
        "acquistionOrDisposition": row.get("transaction_acquired_disposed_code"),
        "typeOfOwner": _role(row),
        "securityType": row.get("security_type"),
    }


def _is_form4(row):
    """Guard against a dump that is not what its filename claims."""
    return isinstance(row, dict) and _code(row) and _first(
        row, "transactionDate", "date") is not None


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
    for path in sorted(glob.glob(str(SRC / "truenorth_insider_*.json"))):
        ticker = pathlib.Path(path).stem.replace("truenorth_insider_", "").upper()
        rows = [_norm_insider(r) for r in _rows(_load(path, []))]
        rows = [r for r in rows if _is_form4(r)]
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


# ── institutional (13F) ───────────────────────────────────────────────────────
def build_institutional():
    """Summarize the top-N 13F holders per name into one card.

    `topOwnPct` is the **top-N cohort's** share of outstanding, not total
    institutional ownership — TrueNorth serves ranked holders, not a market-wide
    total, and reporting the cohort as if it were the total would overstate a
    trim and understate a build. `qoqChange` is that same cohort's move in
    percentage points, derived from each holder's change_in_shares against a
    share count implied by its own ownership_percentage.
    """
    out = []
    for path in sorted(glob.glob(str(SRC / "truenorth_13f_*.json"))):
        ticker = pathlib.Path(path).stem.replace("truenorth_13f_", "").upper()
        doc = _load(path, {})
        holders = [h for h in _rows(doc)[:MAX_HOLDERS] if isinstance(h, dict)]
        if not holders:
            continue
        now_pct = prev_pct = 0.0
        top = []
        for h in holders:
            pct = _num(h.get("ownership_percentage"))
            shares = _num(h.get("shares_held"))
            delta = _num(h.get("change_in_shares")) or 0.0
            if pct is None or not shares:
                continue
            now_pct += pct
            # shares outstanding implied by this holder's own stake
            outstanding = shares / (pct / 100.0) if pct else None
            prev_pct += ((shares - delta) / outstanding * 100.0) if outstanding else pct
            if len(top) < 5:
                top.append({
                    "holder": h.get("holder_name"),
                    "ownPct": round(pct, 2),
                    "changeShares": round(delta),
                    "isNew": bool(h.get("is_new")),
                })
        if not now_pct:
            continue
        out.append({
            "ticker": ticker,
            "topOwnPct": round(now_pct, 2),
            "qoqChange": round(now_pct - prev_pct, 2),
            "holdersCounted": len(holders),
            "reportPeriod": doc.get("report_period") if isinstance(doc, dict) else None,
            "topHolders": top,
        })
    out.sort(key=lambda r: r["ticker"])
    return out


# ── history feed for channel_accuracy ─────────────────────────────────────────
def append_history(insiders, institutional):
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
    for c in institutional:
        chg = c["qoqChange"]
        rows.append({"date": today, "ticker": c["ticker"], "channel": "institutional",
                     "signal": "bullish" if chg > 0 else "bearish" if chg < 0 else "neutral",
                     "net": chg})
    if rows:
        with path.open("a") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
    return len(rows)


# ── assemble ──────────────────────────────────────────────────────────────────
def build():
    cfg = _load(SRC / "config.json", {})
    window_days = cfg.get("windowDays", 90)

    has_src = (glob.glob(str(SRC / "truenorth_insider_*.json"))
               or glob.glob(str(SRC / "truenorth_13f_*.json")))
    existing = _load(DATA / "positioning.json", {})
    if not has_src:
        print("positioning_src/ has no TrueNorth dumps — existing positioning.json left untouched")
        return None

    insiders = build_insiders(window_days)
    institutional = build_institutional()
    out = {
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "institutional": institutional,
        "insider": insiders,
        # COT needs a futures feed no connected provider serves; kept so the key
        # never disappears from under the dashboard.
        "cot": existing.get("cot", []),
    }
    (DATA / "positioning.json").write_text(json.dumps(out, indent=1) + "\n")
    n_hist = append_history(insiders, institutional)
    print(f"positioning.json: {len(insiders)} insider cards, {len(institutional)} 13F cards "
          f"(+{n_hist} history rows)")
    return out


if __name__ == "__main__":
    build()
