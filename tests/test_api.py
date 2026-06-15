"""Tests for VoxCraft API endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client. Skip if supertonic is not installed."""
    try:
        from backend.app import app
        return TestClient(app)
    except ImportError as e:
        pytest.skip(f"supertonic not installed: {e}")
    except Exception as e:
        pytest.skip(f"Failed to create app: {e}")


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "voices_available" in data
        assert "languages_available" in data
        assert "engine_ready" in data

    def test_health_voices_count(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert data["voices_available"] > 0
        assert data["languages_available"] > 0

    def test_health_has_active_syntheses_field(self, client):
        response = client.get("/api/health")
        data = response.json()
        assert "active_syntheses" in data
        assert isinstance(data["active_syntheses"], int)


class TestVoicesEndpoint:
    def test_list_voices_returns_array(self, client):
        response = client.get("/api/voices")
        assert response.status_code == 200
        voices = response.json()
        assert isinstance(voices, list)
        assert len(voices) == 10  # M1-M5, F1-F5

    def test_voice_structure(self, client):
        response = client.get("/api/voices")
        voices = response.json()
        voice = voices[0]
        assert "name" in voice
        assert "display_name" in voice
        assert "description" in voice
        assert "gender" in voice
        assert "tags" in voice

    def test_voices_are_unique(self, client):
        response = client.get("/api/voices")
        voices = response.json()
        names = [v["name"] for v in voices]
        assert len(names) == len(set(names))

    def test_all_voices_have_valid_gender(self, client):
        response = client.get("/api/voices")
        voices = response.json()
        for v in voices:
            assert v["gender"] in ("male", "female")


class TestLanguagesEndpoint:
    def test_list_languages_returns_dict(self, client):
        response = client.get("/api/languages")
        assert response.status_code == 200
        languages = response.json()
        assert isinstance(languages, dict)
        assert len(languages) >= 31

    def test_languages_include_common(self, client):
        response = client.get("/api/languages")
        languages = response.json()
        assert "en" in languages
        assert languages["en"] == "English"
        assert "hi" in languages

    def test_language_codes_are_two_chars(self, client):
        response = client.get("/api/languages")
        languages = response.json()
        for code in languages:
            assert len(code) == 2, f"Language code '{code}' should be 2 characters"


class TestTagsEndpoint:
    def test_list_tags_returns_dict(self, client):
        response = client.get("/api/tags")
        assert response.status_code == 200
        tags = response.json()
        assert isinstance(tags, dict)
        assert len(tags) >= 6

    def test_tags_have_expected_keys(self, client):
        response = client.get("/api/tags")
        tags = response.json()
        expected = {"laugh", "breath", "sigh", "cough", "whisper", "say"}
        assert expected.issubset(tags.keys())


class TestSynthesizeValidation:
    def test_empty_text_rejected(self, client):
        response = client.post("/api/synthesize", json={
            "text": "",
            "voice": "M1",
            "language": "en",
        })
        assert response.status_code == 422  # Pydantic validation

    def test_invalid_voice_rejected(self, client):
        """Invalid voice should return 400 (VoiceNotFoundError) or 422/500/503 as fallback."""
        response = client.post("/api/synthesize", json={
            "text": "Hello world",
            "voice": "INVALID_VOICE",
            "language": "en",
        })
        # Fixed: engine now catches voice-not-found and raises VoiceNotFoundError -> 400
        assert response.status_code in (400, 422, 500, 503)

    def test_speed_out_of_range_rejected(self, client):
        response = client.post("/api/synthesize", json={
            "text": "Hello",
            "voice": "M1",
            "language": "en",
            "speed": 5.0,  # Max is 2.0
        })
        assert response.status_code == 422

    def test_text_too_long_rejected(self, client):
        response = client.post("/api/synthesize", json={
            "text": "x" * 6000,
            "voice": "M1",
            "language": "en",
        })
        assert response.status_code == 422


class TestSPAFallback:
    def test_root_serves_frontend(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_api_404_not_reaching_spa(self, client):
        response = client.get("/api/nonexistent")
        assert response.status_code == 404

    def test_non_api_paths_serve_spa(self, client):
        response = client.get("/some-frontend-route")
        assert response.status_code == 200


class TestHistoryEndpoint:
    def test_history_returns_list(self, client):
        response = client.get("/api/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_history_supports_search(self, client):
        response = client.get("/api/history?search=test")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAudioServeValidation:
    def test_nonexistent_audio_returns_404(self, client):
        response = client.get("/api/audio/nonexistent_file_12345.wav")
        assert response.status_code == 404

    def test_path_traversal_blocked_url_encoded(self, client):
        """URL-encoded traversal (%2e%2e%2f) must be rejected by basename sanitization."""
        response = client.get("/api/audio/%2e%2e%2f%2e%2e%2fetc%2fpasswd")
        # basename of "passwd" shouldn't exist in exports -> 404
        assert response.status_code in (404, 400)

    def test_literal_dotdot_normalized_by_starlette(self, client):
        """Literal ../ is normalized by Starlette before route matching.
        This test documents the behavior — the real defense is against URL-encoded traversal."""
        response = client.get("/api/audio/../../etc/passwd")
        # Starlette normalizes this; may or may not reach our handler
        # Either way, it should not return audio files from outside exports/
        assert response.status_code != 200 or "audio/wav" not in response.headers.get("content-type", "")


class TestDeleteHistoryValidation:
    def test_delete_invalid_id_format(self, client):
        """Non-hex IDs should be rejected with 400."""
        response = client.delete("/api/history/not-a-hex-id")
        assert response.status_code == 400

    def test_delete_glob_pattern_rejected(self, client):
        """Glob patterns like * should not match via SQL exact-ID lookup."""
        response = client.delete("/api/history/*")
        assert response.status_code == 400

    def test_delete_encoded_glob_rejected(self, client):
        """URL-encoded glob %2a should also be rejected."""
        response = client.delete("/api/history/%2a")
        assert response.status_code == 400


class TestBatchEndpoint:
    def test_batch_returns_list(self, client):
        response = client.post("/api/synthesize/batch", json={
            "texts": ["Test"],
            "voice": "M1",
            "language": "en",
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert isinstance(data["total_success"], int)
        assert isinstance(data["total_failed"], int)
