import json
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
