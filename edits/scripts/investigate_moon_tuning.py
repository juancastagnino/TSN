"""Screen lunar geometry parameters against the saved JPL comparison data."""

import csv
import copy
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
D2R = math.pi / 180
EPOCH = datetime(2000, 6, 21, 12)
YEAR_DAYS = 365.2425


def rx(a):
    c, s = np.cos(a), np.sin(a)
    out = np.zeros((len(np.atleast_1d(a)), 3, 3)) if np.ndim(a) else np.empty((3, 3))
    if np.ndim(a):
        out[:, 0, 0] = 1; out[:, 1, 1] = c; out[:, 1, 2] = -s; out[:, 2, 1] = s; out[:, 2, 2] = c
    else:
        out[:] = ((1, 0, 0), (0, c, -s), (0, s, c))
    return out


def ry(a):
    c, s = np.cos(a), np.sin(a)
    out = np.zeros((len(np.atleast_1d(a)), 3, 3)) if np.ndim(a) else np.empty((3, 3))
    if np.ndim(a):
        out[:, 0, 0] = c; out[:, 0, 2] = s; out[:, 1, 1] = 1; out[:, 2, 0] = -s; out[:, 2, 2] = c
    else:
        out[:] = ((c, 0, s), (0, 1, 0), (-s, 0, c))
    return out


def rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array(((c, -s, 0), (s, c, 0), (0, 0, 1)))


def apply(m, v):
    return np.einsum("nij,nj->ni", m, v) if m.ndim == 3 else v @ m.T


def setting_map(path):
    return {item["name"]: item for item in json.loads(path.read_text(encoding="utf-8"))}


def f(s, key):
    return float(s.get(key, 0) or 0)


def load_reference():
    rows = list(csv.DictReader((ROOT / "edits/data/derived/moon_comparison.csv").open(encoding="utf-8")))
    dates = [datetime.fromisoformat(r["date"]) for r in rows]
    pos = np.array([(d - EPOCH).total_seconds() / 86400 / YEAR_DAYS for d in dates])
    jra = np.deg2rad([float(r["jpl_ra_icrf_deg"]) for r in rows])
    jdec = np.deg2rad([float(r["jpl_dec_icrf_deg"]) for r in rows])
    tyra = np.deg2rad([float(r["ty_ra_deg"]) for r in rows])
    tydec = np.deg2rad([float(r["ty_dec_deg"]) for r in rows])
    def vec(ra, dec):
        return np.column_stack((np.sin(ra)*np.cos(dec), np.sin(dec), np.cos(ra)*np.cos(dec)))
    return pos, vec(jra, jdec), vec(tyra, tydec)


def model(settings, pos):
    node, plane = settings["Moon Node"], settings["Moon Plane"]
    da, moon = settings["Moon deferent A"], settings["Moon"]
    db = settings.get("Moon deferent B", {
        "speed": 0, "startPos": 0, "orbitRadius": 0,
        "orbitCentera": 0, "orbitCenterb": 0, "orbitCenterc": 0,
        "orbitTilta": 0, "orbitTiltb": 0,
    })
    n = f(node, "speed")*pos - f(node, "startPos")*D2R
    p = f(plane, "speed")*pos - f(plane, "startPos")*D2R
    aa = f(da, "speed")*pos - f(da, "startPos")*D2R
    ba = f(db, "speed")*pos - f(db, "startPos")*D2R
    ma = f(moon, "speed")*pos - f(moon, "startPos")*D2R
    zero = np.zeros(len(pos))
    radius = lambda s: np.column_stack((np.full(len(pos), f(s,"orbitRadius")), zero, zero))
    centre = lambda s: np.array((f(s,"orbitCentera"),f(s,"orbitCenterc"),f(s,"orbitCenterb")))
    tilt = lambda s: rx(f(s,"orbitTilta")*D2R) @ rz(f(s,"orbitTiltb")*D2R)
    v = centre(moon) + apply(tilt(moon), apply(ry(ma), radius(moon)))
    v = centre(db) + apply(tilt(db), apply(ry(ba), radius(db) + v))
    v = centre(da) + apply(tilt(da), apply(ry(aa), radius(da) + v))
    v = apply(ry(-n), v)
    v = centre(plane) + apply(tilt(plane), apply(ry(p), radius(plane) + v))
    v = centre(node) + apply(tilt(node), apply(ry(n), radius(node) + v))
    earth = settings["Earth"]
    # Three.js Euler XYZ rotation is Rx * Ry * Rz for column vectors.
    er = rx(f(earth,"tiltb")*D2R) @ rz(f(earth,"tilt")*D2R)
    v = apply(er.T, v)
    return v / np.linalg.norm(v, axis=1)[:, None]


def score(pred, ref):
    sep = np.rad2deg(np.arccos(np.clip(np.sum(pred*ref, axis=1), -1, 1)))
    ra = np.unwrap(np.arctan2(pred[:,0],pred[:,2])); rr = np.unwrap(np.arctan2(ref[:,0],ref[:,2]))
    dec = np.arcsin(pred[:,1]); rd = np.arcsin(ref[:,1])
    eps = 23.439291111*D2R
    def eclip(v):
        # Model axes are x=sin(RA)cos(dec), y=sin(dec), z=cos(RA)cos(dec).
        xe = v[:,2]
        ye = v[:,0]*np.cos(eps) + v[:,1]*np.sin(eps)
        ze = -v[:,0]*np.sin(eps) + v[:,1]*np.cos(eps)
        return np.unwrap(np.arctan2(ye,xe)), np.arcsin(ze)
    lon, lat = eclip(pred); rlon, rlat = eclip(ref)
    rms=lambda x: float(np.sqrt(np.mean(np.rad2deg(x)**2)))
    return dict(sep=float(np.sqrt(np.mean(sep**2))), ra=rms(ra-rr), dec=rms(dec-rd), lon=rms(lon-rlon), lat=rms(lat-rlat))


def main():
    pos, ref, exported = load_reference()
    settings = setting_map(ROOT / "src/settings/celestial-settings.json")
    print("reconstruction_vs_export", score(model(settings,pos), exported))
    print("current_vs_jpl", score(model(settings,pos), ref))

    scans = [
        ("Moon Plane", "orbitTilta", np.linspace(-0.5, 0.8, 27)),
        ("Moon Plane", "orbitTiltb", np.linspace(-5.8, -4.2, 33)),
        ("Moon Plane", "orbitCentera", np.linspace(-0.002, 0.005, 29)),
        ("Moon Plane", "orbitCenterb", np.linspace(-0.002, 0.006, 33)),
        ("Moon Node", "startPos", np.linspace(-310, -282, 29)),
        ("Moon deferent A", "startPos", np.linspace(165, 187, 23)),
        ("Moon deferent A", "orbitRadius", np.linspace(0.015, 0.031, 33)),
        ("Moon", "startPos", np.linspace(304, 315, 23)),
        ("Moon", "speed", np.linspace(83.2848, 83.2856, 33)),
    ]
    print("univariate scans (minimum separation RMS, all other values current)")
    for body, key, values in scans:
        results=[]
        for value in values:
            trial=copy.deepcopy(settings); trial[body][key]=float(value)
            results.append((score(model(trial,pos),ref)["sep"],float(value),score(model(trial,pos),ref)))
        best=min(results,key=lambda x:x[0])
        print(body,key,best)

    # Local coordinate descent is only a screening aid; simulator exports remain
    # the authoritative validation and should change one parameter at a time.
    trial = copy.deepcopy(settings)
    dimensions = [
        ("Moon deferent A", "orbitRadius", 0.002),
        ("Moon Plane", "orbitCentera", 0.0005),
        ("Moon Plane", "orbitCenterb", 0.0005),
        ("Moon Plane", "orbitTilta", 0.1),
        ("Moon Plane", "orbitTiltb", 0.1),
        ("Moon Node", "startPos", 1.0),
        ("Moon", "startPos", 0.1),
        ("Moon", "speed", 0.0001),
    ]
    best_score = score(model(trial,pos),ref)["sep"]
    for round_no in range(6):
        for body,key,initial_step in dimensions:
            step=initial_step/(2**round_no)
            current=float(trial[body][key])
            choices=[]
            for value in (current-step,current,current+step):
                candidate=copy.deepcopy(trial); candidate[body][key]=value
                choices.append((score(model(candidate,pos),ref)["sep"],value,candidate))
            best_score,value,trial=min(choices,key=lambda x:x[0])
        print("descent",round_no,best_score,{f"{b}.{k}":float(trial[b][k]) for b,k,_ in dimensions})
    print("descent metrics",score(model(trial,pos),ref))
    staged=copy.deepcopy(settings)
    stages=[
        ("radius only", {("Moon deferent A","orbitRadius"):0.027}),
        ("then plane centres", {("Moon Plane","orbitCentera"):0.0007,("Moon Plane","orbitCenterb"):0.001}),
        ("then plane orientation", {("Moon Plane","orbitTilta"):0.1,("Moon Plane","orbitTiltb"):-5.18,("Moon Node","startPos"):-297.4}),
        ("then fine phase/rate", {("Moon","startPos"):309.45,("Moon","speed"):83.28505}),
    ]
    for label,changes in stages:
        for (body,key),value in changes.items(): staged[body][key]=value
        print("stage",label,score(model(staged,pos),ref))


if __name__ == "__main__":
    main()
