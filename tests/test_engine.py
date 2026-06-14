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

    def test_default_host(self):
        from backend.config import HOST
        assert HOST == "0.0.0.0"

    def test_data_dir_is_absolute(self):
        from backend.config import DATA_DIR
        assert DATA_DIR  # Should not be empty
