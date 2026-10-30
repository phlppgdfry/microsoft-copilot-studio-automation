import json
import hashlib
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

ARTIFACT = Path(__file__).resolve().parents[1] / 'solution/releases/PhlppPortfolioApproval_1_0_0_0.zip'


def test_actual_tenant_export_contains_only_agent_operations():
    with zipfile.ZipFile(ARTIFACT) as archive:
        names = archive.namelist()
        definition = json.loads(archive.read(next(n for n in names if n.endswith('_openapidefinition.json'))))
        manifest = ET.fromstring(archive.read('solution.xml'))
        assert manifest.find('.//UniqueName').text == 'PhlppPortfolioApproval'
        assert set(definition['paths']) == {'/requests', '/requests/{request_id}'}
        assert definition['host'] == 'portfolio-api.example.com'
        assert len(manifest.findall('.//RootComponent')) >= 1


def test_export_has_no_connection_credentials_or_active_flows():
    with zipfile.ZipFile(ARTIFACT) as archive:
        names = archive.namelist()
        parameters = json.loads(archive.read(next(n for n in names if n.endswith('_connectionparameters.json'))))
        assert set(parameters) == {'api_key'}
        assert parameters['api_key']['type'] == 'securestring'
        assert 'value' not in parameters['api_key']
        assert not any(n.startswith(('Workflows/', 'ConnectionReferences/')) for n in names)


def test_export_integrity_and_authentication_match_recorded_artifact():
    record = json.loads((ARTIFACT.parents[2] / 'evidence/tenant-artifact-2026-10-29.json').read_text())
    assert hashlib.sha256(ARTIFACT.read_bytes()).hexdigest() == record['sha256']
    with zipfile.ZipFile(ARTIFACT) as archive:
        assert archive.testzip() is None
        assert all(not n.startswith('/') and '..' not in Path(n).parts for n in archive.namelist())
        definition = json.loads(archive.read(next(n for n in archive.namelist() if n.endswith('_openapidefinition.json'))))
        assert definition['securityDefinitions']['api_key'] == {'type':'apiKey','in':'header','name':'X-API-Key'}
        assert definition['security'] == [{'api_key': []}]
