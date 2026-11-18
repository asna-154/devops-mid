import json
from pathlib import Path
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_metrics_fields():
    r = client.get('/metrics')
    assert r.status_code == 200
    m = r.json()
    for key in ['student_id', 'accuracy', 'training_rows', 'model_version', 'git_sha']:
        assert key in m
    assert m['training_rows'] >= 100
    assert m['accuracy'] > 0.5

def test_predict():
    features = json.loads(Path('config.json').read_text())['features']
    record = {f: 0 for f in features}
    r = client.post('/predict', json={'records': [record]})
    assert r.status_code == 200
    assert len(r.json()['predictions']) == 1