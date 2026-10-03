#!/usr/bin/env python3
"""Download sequential Horizons responses into one reusable plain-text file."""
import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from compare_ephemerides import parse_jpl
from ephemeris_io import jpl_blocks, validate_jpl_header

ROOT = Path(__file__).resolve().parents[2]
ENDPOINT = 'https://ssd.jpl.nasa.gov/api/horizons.api'


def load_defaults():
    return json.loads(Path(__file__).with_name('analysis_config.json').read_text(encoding='utf-8'))


def build_url(target, start, stop, step):
    params = {
        'format': 'text', 'COMMAND': target, 'OBJ_DATA': 'NO', 'MAKE_EPHEM': 'YES',
        'EPHEM_TYPE': 'OBSERVER', 'CENTER': '500@399', 'START_TIME': start, 'STOP_TIME': stop,
        'STEP_SIZE': step, 'QUANTITIES': '1,2', 'TIME_TYPE': 'UT', 'TIME_DIGITS': 'SECONDS',
        'REF_SYSTEM': 'ICRF', 'ANG_FORMAT': 'HMS', 'EXTRA_PREC': 'YES', 'CSV_FORMAT': 'YES',
    }
    return ENDPOINT+'?'+urlencode({k: v if k == 'format' else f"'{v}'" for k, v in params.items()})


def fetch(url):
    request = Request(url, headers={'User-Agent': 'TSN-ephemeris-analysis/1.0'})
    with urlopen(request, timeout=60) as response:
        return response.read().decode('utf-8-sig')


def expected_dates(start, stop, step):
    first, last = datetime.fromisoformat(start), datetime.fromisoformat(stop)
    if first.tzinfo or last.tzinfo or first >= last:
        raise ValueError('Use increasing UTC dates without timezone suffixes')
    match = re.fullmatch(r'([1-9][0-9]*)\s*([mhd])', step)
    if not match:
        raise ValueError('Step must be a positive integer followed by m, h or d (e.g. 6 h)')
    seconds = int(match[1])*{'m': 60, 'h': 3600, 'd': 86400}[match[2]]
    return [first+timedelta(seconds=seconds*i) for i in range(int((last-first).total_seconds()//seconds)+1)]


def main(argv=None):
    defaults = load_defaults()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bodies', nargs='*', help='Default: bodies from analysis_config.json')
    parser.add_argument('--start', default=defaults['start'])
    parser.add_argument('--stop', default=defaults['stop'])
    parser.add_argument('--step', default=defaults['step'])
    parser.add_argument('--output', type=Path, default=ROOT/defaults['jpl'])
    args = parser.parse_args(argv)
    registry = json.loads(Path(__file__).with_name('bodies.json').read_text(encoding='utf-8'))
    bodies = list(dict.fromkeys(args.bodies or defaults['bodies']))
    if not bodies or set(bodies)-set(registry):
        parser.error('Select bodies registered in bodies.json')
    dates = expected_dates(args.start, args.stop, args.step)
    chunks = ['# TSN Horizons bundle\n# Downloaded UTC: '+datetime.now(timezone.utc).isoformat()+'\n']
    # Horizons requires one request at a time. Do not parallelize this loop.
    for body in bodies:
        target = registry[body]['target_id']
        url = build_url(target, args.start, args.stop, args.step)
        print(f'Downloading {body} ({target})...', flush=True)
        response = fetch(url)
        blocks = jpl_blocks(response)
        if set(blocks) != {target}:
            raise ValueError(f'{body}: unexpected Horizons target')
        validate_jpl_header(blocks[target])
        rows = parse_jpl(blocks[target], strict=True)
        if sorted(rows) != dates:
            raise ValueError(f'{body}: returned timestamps do not match the requested grid')
        chunks.append(f'# REQUEST BODY: {body}\n# REQUEST URL: {url}\n'+response.rstrip()+'\n')
        print(f'Validated {len(rows)} rows for {body}', flush=True)
    # Publish only after ALL responses pass validation; never truncate a good cache on error.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=args.output.parent, prefix='.jpl-download-', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write('\n'.join(chunks))
        os.replace(temporary, args.output)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    print(f'Saved {len(bodies)} bodies to {args.output}')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        raise SystemExit(str(error))
