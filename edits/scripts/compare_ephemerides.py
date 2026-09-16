#!/usr/bin/env python3
"""Compare TYCHOS lunar ephemerides with NASA/JPL Horizons.

Expected TYCHOS format (one position per line):
    YYYY-MM-DD | HH:MM:SS | 21h08m20.6s | -18°16'33.9"

Expected JPL input: Horizons text output containing $$SOE/$$EOE and
CSV columns for ICRF and apparent RA/Dec (QUANTITIES='1,2').

Example to run the ephemerides comparison:
    py edits/scripts/compare_ephemerides.py \
        edits/data/raw/tychos_moon_2000-2026_6h.txt \
        edits/data/raw/jpl_moon_de441_2000-2026_6h.txt \
        -o edits/data/derived/moon_comparison_2000-2026_6h.csv
"""

import argparse
import csv
import math
import re
from datetime import datetime
from pathlib import Path
from statistics import median

TY_RA_RE = re.compile(r"^\s*(\d+)h(\d+)m([\d.]+)s\s*$")
TY_DEC_RE = re.compile(r"^\s*([+-]?)(\d+)°(\d+)'([\d.]+)\"\s*$")


def parse_ty_ra(value):
    m = TY_RA_RE.match(value)
    if not m:
        raise ValueError(f"Could not parse TYCHOS RA: {value!r}")
    h, minute, sec = int(m.group(1)), int(m.group(2)), float(m.group(3))
    return 15.0 * (h + minute / 60.0 + sec / 3600.0)


def parse_ty_dec(value):
    m = TY_DEC_RE.match(value)
    if not m:
        raise ValueError(f"Could not parse TYCHOS Dec: {value!r}")
    sign = -1.0 if m.group(1) == "-" else 1.0
    deg, minute, sec = int(m.group(2)), int(m.group(3)), float(m.group(4))
    return sign * (deg + minute / 60.0 + sec / 3600.0)


def parse_jpl_ra(value):
    p = value.split()
    if len(p) != 3:
        raise ValueError(f"Could not parse JPL RA: {value!r}")
    h, minute, sec = int(p[0]), int(p[1]), float(p[2])
    return 15.0 * (h + minute / 60.0 + sec / 3600.0)


def parse_jpl_dec(value):
    p = value.split()
    if len(p) != 3:
        raise ValueError(f"Could not parse JPL Dec: {value!r}")
    sign = -1.0 if p[0].startswith("-") else 1.0
    deg = abs(int(p[0]))
    minute, sec = int(p[1]), float(p[2])
    return sign * (deg + minute / 60.0 + sec / 3600.0)


def wrap_deg(delta):
    return (delta + 180.0) % 360.0 - 180.0


def angular_separation_deg(ra1, dec1, ra2, dec2):
    r1, d1, r2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    c = (
        math.sin(d1) * math.sin(d2)
        + math.cos(d1) * math.cos(d2) * math.cos(r1 - r2)
    )
    c = max(-1.0, min(1.0, c))
    return math.degrees(math.acos(c))


def read_tychos(path):
    data = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        for line in f:
            if "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 4:
                continue
            try:
                dt = datetime.strptime(parts[0] + " " + parts[1], "%Y-%m-%d %H:%M:%S")
                ra = parse_ty_ra(parts[2])
                dec = parse_ty_dec(parts[3])
            except (ValueError, IndexError):
                continue
            data[dt] = {"ra": ra, "dec": dec}
    return data


def read_jpl(path):
    data = {}
    inside = False
    with open(path, "r", encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if line == "$$SOE":
                inside = True
                continue
            if line == "$$EOE":
                break
            if not inside or not line:
                continue

            cols = [c.strip() for c in raw.split(",")]
            if len(cols) < 7:
                continue
            try:
                dt = datetime.strptime(cols[0], "%Y-%b-%d %H:%M:%S")
                ra_icrf = parse_jpl_ra(cols[3])
                dec_icrf = parse_jpl_dec(cols[4])
                ra_app = parse_jpl_ra(cols[5])
                dec_app = parse_jpl_dec(cols[6])
            except (ValueError, IndexError):
                continue

            data[dt] = {
                "ra_icrf": ra_icrf,
                "dec_icrf": dec_icrf,
                "ra_app": ra_app,
                "dec_app": dec_app,
            }
    return data


def rms(values):
    return math.sqrt(sum(v * v for v in values) / len(values))


def percentile(values, p):
    s = sorted(values)
    if not s:
        return float("nan")
    x = (len(s) - 1) * p
    lo = math.floor(x)
    hi = math.ceil(x)
    if lo == hi:
        return s[lo]
    return s[lo] * (hi - x) + s[hi] * (x - lo)


def print_summary(rows, label, prefix):
    dra = [r[f"dra_{prefix}_deg"] for r in rows]
    ddec = [r[f"ddec_{prefix}_deg"] for r in rows]
    sep = [r[f"sep_{prefix}_deg"] for r in rows]
    worst_dec = max(rows, key=lambda r: abs(r[f"ddec_{prefix}_deg"]))
    worst_sep = max(rows, key=lambda r: r[f"sep_{prefix}_deg"])

    print("\n" + "=" * 70)
    print(label)
    print("=" * 70)
    print(f"N matched                    : {len(rows)}")
    print(f"RA RMS (coordinate deg)      : {rms(dra):.6f} deg")
    print(f"Dec RMS                      : {rms(ddec):.6f} deg")
    print(f"Median |Dec error|           : {median(abs(v) for v in ddec):.6f} deg")
    print(f"95th percentile |Dec error|  : {percentile([abs(v) for v in ddec], .95):.6f} deg")
    print(f"Angular separation RMS       : {rms(sep):.6f} deg")
    print(f"Max |Dec error|              : {abs(worst_dec[f'ddec_{prefix}_deg']):.6f} deg")
    print(f"  date                       : {worst_dec['date']}")
    print(f"Max angular separation       : {worst_sep[f'sep_{prefix}_deg']:.6f} deg")
    print(f"  date                       : {worst_sep['date']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tychos", help="TYCHOS ephemeris text file")
    parser.add_argument("jpl", help="JPL Horizons text file")
    parser.add_argument(
        "-o", "--output", default="moon_comparison.csv", help="Output CSV path"
    )
    args = parser.parse_args()

    ty = read_tychos(args.tychos)
    jp = read_jpl(args.jpl)
    common = sorted(set(ty) & set(jp))

    print(f"TYCHOS positions parsed : {len(ty)}")
    print(f"JPL positions parsed    : {len(jp)}")
    print(f"Exact timestamps matched: {len(common)}")

    if not common:
        raise SystemExit("No exact matching timestamps found.")

    rows = []
    for dt in common:
        t = ty[dt]
        j = jp[dt]

        dra_icrf = wrap_deg(t["ra"] - j["ra_icrf"])
        ddec_icrf = t["dec"] - j["dec_icrf"]
        dra_app = wrap_deg(t["ra"] - j["ra_app"])
        ddec_app = t["dec"] - j["dec_app"]

        mean_dec_icrf = math.radians((t["dec"] + j["dec_icrf"]) / 2.0)
        mean_dec_app = math.radians((t["dec"] + j["dec_app"]) / 2.0)

        rows.append({
            "date": dt.strftime("%Y-%m-%d %H:%M:%S"),
            "ty_ra_deg": t["ra"],
            "ty_dec_deg": t["dec"],
            "jpl_ra_icrf_deg": j["ra_icrf"],
            "jpl_dec_icrf_deg": j["dec_icrf"],
            "dra_icrf_deg": dra_icrf,
            "dra_icrf_seconds_time": dra_icrf * 240.0,
            "dra_icrf_cosdec_deg": dra_icrf * math.cos(mean_dec_icrf),
            "ddec_icrf_deg": ddec_icrf,
            "sep_icrf_deg": angular_separation_deg(
                t["ra"], t["dec"], j["ra_icrf"], j["dec_icrf"]
            ),
            "jpl_ra_app_deg": j["ra_app"],
            "jpl_dec_app_deg": j["dec_app"],
            "dra_app_deg": dra_app,
            "dra_app_seconds_time": dra_app * 240.0,
            "dra_app_cosdec_deg": dra_app * math.cos(mean_dec_app),
            "ddec_app_deg": ddec_app,
            "sep_app_deg": angular_separation_deg(
                t["ra"], t["dec"], j["ra_app"], j["dec_app"]
            ),
        })

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print_summary(rows, "JPL ICRF ASTROMETRIC", "icrf")
    print_summary(rows, "JPL APPARENT", "app")
    print(f"\nCSV written to: {output}")


if __name__ == "__main__":
    main()
