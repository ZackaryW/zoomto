import pytest
from datetime import datetime, timedelta
from src.zoomto.utils import parse_time

class TestParseTime:
    def test_parse_seconds(self):
        assert parse_time("30") == 30

    def test_parse_12hour_format_with_colon(self):
        now = datetime.now()
        target_time = now.replace(hour=10, minute=25, second=0, microsecond=0)
        if target_time <= now:
            target_time += timedelta(days=1)
        expected = int((target_time - now).total_seconds())
        assert parse_time("10:25am") == pytest.approx(expected, abs=1)

    def test_parse_12hour_format_without_colon(self):
        now = datetime.now()
        target_time = now.replace(hour=22, minute=35, second=0, microsecond=0)
        if target_time <= now:
            target_time += timedelta(days=1)
        expected = int((target_time - now).total_seconds())
        assert parse_time("1035pm") == pytest.approx(expected, abs=1)

    def test_parse_24hour_format_with_colon(self):
        now = datetime.now()
        target_time = now.replace(hour=14, minute=30, second=0, microsecond=0)
        if target_time <= now:
            target_time += timedelta(days=1)
        expected = int((target_time - now).total_seconds())
        assert parse_time("14:30") == pytest.approx(expected, abs=1)

    def test_invalid_time_format(self):
        with pytest.raises(ValueError, match="Invalid time format: 25:00"):
            parse_time("25:00")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="Invalid time format: "):
            parse_time("")

    def test_non_numeric_string(self):
        with pytest.raises(ValueError, match="Invalid time format: abc"):
            parse_time("abc")

    def test_time_rollover(self):
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        test_time = f"{current_hour:02d}:{current_minute:02d}"
        result = parse_time(test_time)
        assert result > 0
        assert result <= 24 * 60 * 60  # Should not be more than 24 hours
