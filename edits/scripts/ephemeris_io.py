"""Identify body sections without discarding Horizons headers or mixing epochs."""
import re


def tychos_blocks(text):
    matches = list(re.finditer(r"^PLANET:[ \t]*([^\r\n]+)", text, re.MULTILINE))
    if not matches:
        raise ValueError("TYCHOS export has no PLANET: sections")
    result = {}
    for i, match in enumerate(matches):
        body = match[1].strip().lower()
        if body in result:
            raise ValueError(f"Duplicate TYCHOS body section: {body}")
        result[body] = text[match.start():matches[i+1].start() if i+1 < len(matches) else len(text)]
    return result


def jpl_blocks(text):
    matches = list(re.finditer(r"^Target body name:[^\r\n]*?\((\d+)\)", text, re.MULTILINE))
    if not matches:
        raise ValueError("Horizons response has no target header; it may contain an API error")
    result = {}
    for i, match in enumerate(matches):
        target = match[1]
        if target in result:
            raise ValueError(f"Duplicate Horizons target section: {target}")
        block = text[match.start():matches[i+1].start() if i+1 < len(matches) else len(text)]
        if block.count('$$SOE') != 1 or block.count('$$EOE') != 1 or block.index('$$SOE') > block.index('$$EOE'):
            raise ValueError(f"Target {target}: incomplete or repeated Horizons table")
        result[target] = block
    return result


def validate_jpl_header(block):
    header = block.split('$$SOE', 1)[0]
    if not re.search(r"Center body name:.*?\(399\)", header) or not re.search(r"Center-site name:\s*GEOCENTRIC", header):
        raise ValueError("Expected Earth geocentric reference")
    if not all(token in header for token in ('Date__(UT)', '(ICRF)', '(a-app)')):
        raise ValueError("Expected UT CSV with ICRF and apparent RA/Dec")
    return header


def select_block(blocks, key, source):
    if key is None:
        if len(blocks) != 1:
            raise ValueError(f"{source} contains multiple bodies; select a body/target explicitly")
        return next(iter(blocks.values()))
    if str(key) not in blocks:
        raise ValueError(f"Missing {source} body/target: {key}")
    return blocks[str(key)]
