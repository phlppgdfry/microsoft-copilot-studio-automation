import json
from pathlib import Path
import sys
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from package_connector import package


def test_generated_connector_retains_least_privilege(tmp_path):
    manifest = package('https://synthetic-approval.example.com', tmp_path)
    definition = json.loads((tmp_path / 'apiDefinition.swagger.json').read_text())
    assert definition['host'] == 'synthetic-approval.example.com'
    assert set(definition['paths']) == {'/requests', '/requests/{request_id}'}
    assert manifest['tenant_import_verified'] is False and manifest['solution_export'] is False
    assert manifest['credentials_included'] is False
    properties = json.loads((tmp_path / 'apiProperties.json').read_text())
    assert properties['properties']['connectionParameters']['api_key']['type'] == 'securestring'


@pytest.mark.parametrize('origin', ['http://localhost:8085', 'https://a.invalid', 'https://host/path',
                                    'https://user:password@host', 'https://host/?key=secret'])
def test_packaging_rejects_unsafe_deployment_origin(tmp_path, origin):
    with pytest.raises(ValueError):
        package(origin, tmp_path)
