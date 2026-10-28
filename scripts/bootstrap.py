import json
import secrets
from pathlib import Path

path = Path('.env')
if path.exists():
    raise SystemExit('.env already exists; refusing to overwrite')
profiles = {'agent': {'subject': 'synthetic-agent', 'tenant': 'synthetic-firm', 'role': 'agent'}, 'reviewer': {'subject': 'synthetic-reviewer', 'tenant': 'synthetic-firm', 'role': 'reviewer'}, 'executor': {'subject': 'synthetic-executor', 'tenant': 'synthetic-firm', 'role': 'executor'}}
keys = {secrets.token_urlsafe(32): profile for profile in profiles.values()}
content = "AUTOMATION_PRINCIPALS='" + json.dumps(keys) + "'\n"
with path.open('x') as file:
    file.write(content)
path.chmod(0o600)
print('Created local .env with random keys; inspect it privately for role-specific keys.')
