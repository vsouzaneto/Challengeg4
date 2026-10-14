"""Generate the same contract registry for Edge and frontend; no source data."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from domain.source_contracts import CONTRACTS,CONTRACT_VERSION

def main():
    registry={name:{key:{'kind':field.kind,'nullable':field.nullable} for key,field in columns.items()} for name,columns in CONTRACTS.items()}
    source='// Generated from domain/source_contracts.py; regenerate instead of diverging.\nexport const contracts = '+json.dumps(registry,indent=2)+';\nexport const contractVersion = '+json.dumps(CONTRACT_VERSION)+';\n'
    for target in [ROOT/'web/domain/contracts.mjs',ROOT/'web/frontend/lib/contracts.mjs']:
        target.write_text(source)
if __name__=='__main__':main()
