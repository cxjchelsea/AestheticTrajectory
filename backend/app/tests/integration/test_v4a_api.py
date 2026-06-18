from fastapi.testclient import TestClient

from app.main import app


def test_multimodal_input_and_file_upload_api() -> None:
    client = TestClient(app)

    music_response = client.post(
        "/api/inputs",
        json={
            "type": "music",
            "title": "ambient loop",
            "fileUrl": "https://example.com/track",
            "description": "metadata only",
        },
    )
    assert music_response.status_code == 200
    assert music_response.json()["type"] == "music"

    video_response = client.post(
        "/api/inputs",
        json={
            "type": "video",
            "title": "slow motion",
            "fileUrl": "https://example.com/clip",
        },
    )
    assert video_response.status_code == 200
    assert video_response.json()["type"] == "video"

    text_response = client.post(
        "/api/inputs",
        json={
            "type": "text",
            "contentText": "quiet sample",
            "title": "quiet sample",
        },
    )
    assert text_response.status_code == 200

    upload_response = client.post(
        "/api/files/upload",
        files={"file": ("sample.png", b"\x89PNG\r\n\x1a\n", "image/png")},
    )
    assert upload_response.status_code == 200
    uploaded = upload_response.json()
    assert uploaded["fileUrl"].startswith("/api/files/")
    assert uploaded["mimeType"] == "image/png"

    image_response = client.post(
        "/api/inputs",
        json={
            "type": "image",
            "title": "uploaded image",
            "fileUrl": uploaded["fileUrl"],
        },
    )
    assert image_response.status_code == 200

    job_response = client.post(
        "/api/analysis-jobs",
        json={
            "inputIds": [
                music_response.json()["id"],
                video_response.json()["id"],
                text_response.json()["id"],
            ]
        },
    )
    assert job_response.status_code == 200
    job = job_response.json()
    assert job["status"] == "completed"

    debug_response = client.get(f"/api/analysis-jobs/{job['id']}/debug")
    assert debug_response.status_code == 200
    debug = debug_response.json()
    chroma_warning = next(
        item for item in debug["boundaryWarnings"] if item["capability"] == "ChromaDB runtime writes"
    )
    assert chroma_warning["status"] == "not_used"
    assert debug["fallbackEvents"]
    assert debug["fallbackEvents"][0]["stepId"] == "write_vectors"
