"""Build parameterized files for pac connector create; not a tenant-exported solution."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

from export_connector import document


def package(origin, output):
    parsed = urlsplit(origin)
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.path not in ('', '/') or parsed.query or parsed.fragment
            or parsed.hostname.endswith('.invalid')):
        raise ValueError('A deployed HTTPS API origin is required; no keys or query parameters')
    swagger = document()
    swagger['host'] = parsed.netloc
    properties = {'properties': {'connectionParameters': {'api_key': {
        'type': 'securestring', 'uiDefinition': {'displayName': 'Agent proposal API key',
        'description': 'Use only an agent role credential. Never reviewer or executor credentials.',
        'tooltip': 'Server-configured agent identity',
        'constraints': {'required': 'true', 'tabIndex': 2, 'clearText': False}}}},
        'iconBrandColor': '#216B64', 'capabilities': []}}
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for filename, data in [('apiDefinition.swagger.json', swagger), ('apiProperties.json', properties)]:
        raw = (json.dumps(data, indent=2, sort_keys=True) + '\n').encode()
        (output / filename).write_bytes(raw)
        hashes[filename] = hashlib.sha256(raw).hexdigest()
    manifest = {'artifact_type': 'pac-custom-connector-input', 'tenant_import_verified': False,
                'solution_export': False, 'files_sha256': hashes,
                'permissions': ['ProposeDossierTask', 'GetDossierTask'], 'credentials_included': False}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', required=True)
    parser.add_argument('--out', type=Path, default=Path('build/connector'))
    args = parser.parse_args()
    print(json.dumps(package(args.origin, args.out), indent=2))


if __name__ == '__main__':
    main()
