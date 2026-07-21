from pathlib import Path


def test_render_blueprint_hosts_the_fastapi_websocket_service_on_free_plan():
    blueprint = Path("render.yaml").read_text(encoding="utf-8")

    assert "type: web" in blueprint
    assert "plan: free" in blueprint
    assert "pip install -r requirements.txt" in blueprint
    assert "uvicorn app.main:app --host 0.0.0.0 --port $PORT" in blueprint
    assert "healthCheckPath: /api/health" in blueprint
    assert "key: OPENAI_API_KEY" in blueprint
    assert "sync: false" in blueprint


def test_browser_uses_secure_websocket_on_an_https_deployment():
    call_client = Path("public/call.js").read_text(encoding="utf-8")

    assert "location.protocol === 'https:' ? 'wss' : 'ws'" in call_client
    assert "${location.host}/ws/calls/" in call_client

