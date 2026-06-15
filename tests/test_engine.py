"""Tests for the TTS engine module (unit tests, no Supertonic required)."""


class TestVoiceStyle:
    def test_voice_style_creation(self):
        from backend.tts_engine import VoiceStyle
        v = VoiceStyle("M1", "M1 — Test", "A test voice", "male", ["warm"])
        assert v.name == "M1"
        assert v.display_name == "M1 — Test"
        assert v.gender == "male"
        assert "warm" in v.tags

    def test_voice_style_to_dict(self):
        from backend.tts_engine import VoiceStyle
        v = VoiceStyle("F1", "F1 — Test", "Desc", "female")
        d = v.to_dict()
        assert d["name"] == "F1"
        assert d["gender"] == "female"
        assert "tags" in d

    def test_voice_style_default_tags(self):
        from backend.tts_engine import VoiceStyle
        v = VoiceStyle("M3", "M3", "desc", "male")
        assert v.tags == []


class TestPresetVoices:
    def test_preset_voices_count(self):
        from backend.tts_engine import PRESET_VOICES
        assert len(PRESET_VOICES) == 10

    def test_male_voices(self):
        from backend.tts_engine import PRESET_VOICES
        male = [v for v in PRESET_VOICES if v.gender == "male"]
        assert len(male) == 5
        male_names = {v.name for v in male}
        assert male_names == {"M1", "M2", "M3", "M4", "M5"}

    def test_female_voices(self):
        from backend.tts_engine import PRESET_VOICES
        female = [v for v in PRESET_VOICES if v.gender == "female"]
        assert len(female) == 5
        female_names = {v.name for v in female}
        assert female_names == {"F1", "F2", "F3", "F4", "F5"}

    def test_all_voices_have_descriptions(self):
        from backend.tts_engine import PRESET_VOICES
        for v in PRESET_VOICES:
            assert len(v.description) > 10, f"Voice {v.name} has short description"
            assert "—" in v.display_name, f"Voice {v.name} missing em-dash in display name"


class TestLanguages:
    def test_languages_count(self):
        from backend.tts_engine import LANGUAGES
        assert len(LANGUAGES) == 31

    def test_english_present(self):
        from backend.tts_engine import LANGUAGES
        assert LANGUAGES["en"] == "English"

    def test_all_language_codes_are_two_chars(self):
        from backend.tts_engine import LANGUAGES
        for code in LANGUAGES:
            assert len(code) == 2


class TestExpressionTags:
    def test_tags_count(self):
        from backend.tts_engine import EXPRESSION_TAGS
        assert len(EXPRESSION_TAGS) == 6

    def test_tags_format(self):
        from backend.tts_engine import EXPRESSION_TAGS
        for name, tag in EXPRESSION_TAGS.items():
            assert tag.startswith("<"), f"Tag {name} doesn't start with <"
            assert tag.endswith(">"), f"Tag {name} doesn't end with >"


class TestConfig:
    def test_default_port(self):
        from backend.config import PORT
        assert PORT == 8765

    def test_default_host_is_localhost(self):
        """Issue 4.3: Default bind should be 127.0.0.1, not 0.0.0.0."""
        from backend.config import HOST
        assert HOST == "127.0.0.1"

    def test_data_dir_is_absolute(self):
        from backend.config import DATA_DIR
        assert DATA_DIR

    def test_max_concurrency_default(self):
        from backend.config import MAX_CONCURRENCY
        assert MAX_CONCURRENCY == 4

    def test_db_path_configured(self):
        from backend.config import DB_PATH
        assert DB_PATH.endswith(".db")


class TestExceptions:
    def test_voice_not_found_error_is_value_error(self):
        from backend.tts_engine import VoiceNotFoundError
        err = VoiceNotFoundError("Voice 'X99' is not available")
        assert isinstance(err, ValueError)
        assert "X99" in str(err)

    def test_engine_not_ready_error_is_runtime_error(self):
        from backend.tts_engine import EngineNotReadyError
        err = EngineNotReadyError("TTS engine could not be initialized")
        assert isinstance(err, RuntimeError)


class TestDataStore:
    """Tests for the SQLite-backed data store."""

    def test_init_db_creates_tables(self, tmp_path):
        import os
        os.environ["VOXCRAFT_DATA_DIR"] = str(tmp_path)
        try:
            from backend.data_store import init_db
            import importlib
            import backend.data_store as ds
            importlib.reload(ds)
            ds.DB_PATH = tmp_path / "voxcraft.db"
            init_db()
            import sqlite3
            conn = sqlite3.connect(str(ds.DB_PATH))
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
            table_names = {t[0] for t in tables}
            assert "exports" in table_names
            assert "history" in table_names
            assert "schema_version" in table_names
            conn.close()
        finally:
            if "VOXCRAFT_DATA_DIR" in os.environ:
                del os.environ["VOXCRAFT_DATA_DIR"]

    def test_save_and_get_export(self, tmp_path):
        import os
        os.environ["VOXCRAFT_DATA_DIR"] = str(tmp_path)
        try:
            import importlib
            import backend.data_store as ds
            import backend.config as cfg
            importlib.reload(cfg)
            importlib.reload(ds)

            ds.init_db()
            meta = {
                "id": "abcd1234",
                "filename": "voxcraft_abcd1234_20260101_000000",
                "text": "Hello world",
                "voice": "M1",
                "language": "en",
                "duration_seconds": 2.5,
                "format": "wav",
                "sample_rate": 44100,
                "speed": 1.0,
                "quality": 8,
                "created_at": "20260101_000000",
                "audio_path": "/tmp/test.wav",
            }
            ds.save_export(meta)
            result = ds.get_export("abcd1234")
            assert result is not None
            assert result["text"] == "Hello world"
            assert result["voice"] == "M1"
        finally:
            if "VOXCRAFT_DATA_DIR" in os.environ:
                del os.environ["VOXCRAFT_DATA_DIR"]

    def test_get_history_returns_list(self, tmp_path):
        import os
        os.environ["VOXCRAFT_DATA_DIR"] = str(tmp_path)
        try:
            import importlib
            import backend.data_store as ds
            importlib.reload(ds)
            ds.init_db()
            history = ds.get_history(limit=10)
            assert isinstance(history, list)
        finally:
            if "VOXCRAFT_DATA_DIR" in os.environ:
                del os.environ["VOXCRAFT_DATA_DIR"]

    def test_delete_nonexistent_returns_zero(self, tmp_path):
        import os
        os.environ["VOXCRAFT_DATA_DIR"] = str(tmp_path)
        try:
            import importlib
            import backend.data_store as ds
            importlib.reload(ds)
            ds.init_db()
            result = ds.delete_export("nonexistent_id")
            assert result == 0
        finally:
            if "VOXCRAFT_DATA_DIR" in os.environ:
                del os.environ["VOXCRAFT_DATA_DIR"]
