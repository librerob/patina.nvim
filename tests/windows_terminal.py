"""Validate both Windows Terminal scheme objects with Microsoft's JSON schema."""
from pathlib import Path
import json
import sys
from jsonschema import Draft202012Validator

root = Path(__file__).resolve().parents[1]
schema = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
validator = Draft202012Validator({'$defs': schema['$defs'], '$ref': '#/$defs/SchemeList'})
for path in (root / 'ports/windows-terminal').glob('*.json'):
    data = json.loads(path.read_text(encoding='utf-8'))
    validator.validate([data])
    definition = schema['$defs']['SchemeList']['items']
    unknown = data.keys() - definition['properties'].keys()
    assert not unknown, f'Unknown Windows Terminal scheme properties: {unknown}'
print('Both schemes passed the official Windows Terminal schema; no unknown properties')
