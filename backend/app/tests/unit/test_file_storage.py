from pathlib import Path

import pytest

from app.storage.file_storage import resolve_uploaded_file, save_upload


def test_save_and_resolve_upload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))

    from importlib import reload

    import app.core.config as config_module
    import app.storage.local_storage as local_storage_module

    reload(config_module)
    reload(local_storage_module)

    import app.storage.file_storage as file_storage_module

    reload(file_storage_module)

    response = file_storage_module.save_upload("sample.png", b"png-bytes", "image/png")
    assert response.file_url == f"/api/files/{response.file_id}"
    assert response.mime_type == "image/png"
    assert response.size_bytes == len(b"png-bytes")

    resolved = file_storage_module.resolve_uploaded_file(response.file_id)
    assert resolved is not None
    assert resolved.exists()
    assert resolved.read_bytes() == b"png-bytes"


def test_reject_unsupported_mime_type(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path))

    from importlib import reload

    import app.core.config as config_module
    import app.storage.local_storage as local_storage_module

    reload(config_module)
    reload(local_storage_module)

    import app.storage.file_storage as file_storage_module

    reload(file_storage_module)

    with pytest.raises(ValueError, match="Unsupported image mime type"):
        file_storage_module.save_upload("sample.pdf", b"pdf", "application/pdf")
