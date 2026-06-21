"""
Smoke tests for the API surface. These don't require trained weights —
they verify the app boots, routes exist, and respond with sane shapes
even before any violation has been recorded.

Run with: pytest -v  (from the backend/ directory)
"""
import io

import numpy as np
import cv2
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    # TestClient must be used as a context manager for startup/shutdown
    # events (our DB initialization) to actually run.
    with TestClient(app) as c:
        yield c


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "Helmet Non Compliance" in body["implemented_modules"]
    assert "Triple Riding" in body["implemented_modules"]
    assert "Seatbelt Violation" in body["architecture_modules"]
    assert "Red Light Violation" in body["architecture_modules"]


def test_analytics_summary_empty_db(client):
    resp = client.get("/api/analytics/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_violations" in body
    assert isinstance(body["implemented_modules"], list)


def test_violations_list_empty_ok(client):
    resp = client.get("/api/violations")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_detect_rejects_garbage_image(client):
    fake_bytes = b"not an image"
    resp = client.post(
        "/api/detect",
        files={"image": ("bad.jpg", io.BytesIO(fake_bytes), "image/jpeg")},
    )
    assert resp.status_code == 400


def test_detect_blank_image_no_violation(client):
    # A blank frame has no motorcycle/person, so this should be a clean
    # 422 ("no violation detected") rather than a crash.
    blank = np.full((480, 640, 3), 255, dtype=np.uint8)
    ok, buf = cv2.imencode(".jpg", blank)
    assert ok
    resp = client.post(
        "/api/detect",
        files={"image": ("blank.jpg", io.BytesIO(buf.tobytes()), "image/jpeg")},
    )
    assert resp.status_code == 422
