from pathlib import Path

from fastapi.testclient import TestClient


def test_v6d_uploads_are_isolated_to_pytest_tmp_dir(tmp_path: Path) -> None:
    from app.core.config import settings
    from app.main import app
    from app.storage.file_storage import resolve_uploaded_file

    client = TestClient(app)
    response = client.post(
        "/api/files/upload",
        files={"file": ("sample.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )

    assert response.status_code == 200
    uploaded = response.json()
    resolved = resolve_uploaded_file(uploaded["fileId"])

    assert resolved is not None
    assert resolved.exists()
    assert Path(settings.upload_dir).is_relative_to(tmp_path)
    assert resolved.is_relative_to(tmp_path)
    assert not (Path.cwd() / "uploads" / "user_anonymous" / f'{uploaded["fileId"]}.png').exists()
