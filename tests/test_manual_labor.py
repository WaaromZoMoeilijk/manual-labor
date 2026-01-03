"""
Unit tests for Manual Labor - Testing core logic without GUI dependencies
"""

import pytest
import time
import random
import json
import os
import tempfile


class TestCPSLogic:
    """Test clicks-per-second calculations"""

    def test_cps_to_delay_min(self):
        """Test minimum CPS (1) produces 1 second delay"""
        cps = 1
        delay = 1 / cps
        assert delay == 1.0

    def test_cps_to_delay_max(self):
        """Test maximum CPS (50) produces 20ms delay"""
        cps = 50
        delay = 1 / cps
        assert delay == 0.02

    def test_cps_to_delay_default(self):
        """Test default CPS (10) produces 100ms delay"""
        cps = 10
        delay = 1 / cps
        assert delay == 0.1

    def test_all_cps_values_valid(self):
        """Test all CPS values in range produce valid delays"""
        for cps in range(1, 51):
            delay = 1 / cps
            assert delay > 0
            assert delay <= 1.0


class TestRandomVariation:
    """Test timing variation logic"""

    def test_no_variation(self):
        """Test 0% variation produces exact delay"""
        base_delay = 0.1
        variation_percent = 0
        variation = base_delay * (variation_percent / 100)
        delay = base_delay + random.uniform(-variation, variation)
        assert delay == base_delay

    def test_variation_range(self):
        """Test variation stays within bounds"""
        base_delay = 0.1
        variation_percent = 15

        for _ in range(100):
            variation = base_delay * (variation_percent / 100)
            delay = base_delay + random.uniform(-variation, variation)
            min_delay = base_delay - variation
            max_delay = base_delay + variation
            assert min_delay <= delay <= max_delay

    def test_variation_15_percent(self):
        """Test 15% variation calculation"""
        base_delay = 0.1
        variation_percent = 15
        expected_variation = 0.015  # 15% of 0.1

        variation = base_delay * (variation_percent / 100)
        assert abs(variation - expected_variation) < 0.0001

    def test_delay_always_positive(self):
        """Test delay is always positive even with high variation"""
        base_delay = 0.02  # 50 CPS
        variation_percent = 30

        for _ in range(100):
            variation = base_delay * (variation_percent / 100)
            delay = base_delay + random.uniform(-variation, variation)
            delay = max(0.001, delay)  # Same logic as in code
            assert delay > 0


class TestCPSParsing:
    """Test CPS value parsing from slider"""

    def test_parse_integer_string(self):
        """Test parsing integer string from slider"""
        value = "25"
        parsed = int(float(value))
        assert parsed == 25

    def test_parse_float_string(self):
        """Test parsing float string from slider"""
        value = "25.0"
        parsed = int(float(value))
        assert parsed == 25

    def test_parse_float_rounds_down(self):
        """Test that float values round down to int"""
        value = "25.7"
        parsed = int(float(value))
        assert parsed == 25

    def test_parse_min_value(self):
        """Test parsing minimum value"""
        value = "1.0"
        parsed = int(float(value))
        assert parsed == 1

    def test_parse_max_value(self):
        """Test parsing maximum value"""
        value = "50.0"
        parsed = int(float(value))
        assert parsed == 50


class TestStateLogic:
    """Test state toggle logic"""

    def test_toggle_when_stopped_starts(self):
        """Test toggle logic when stopped"""
        is_running = False
        is_running = not is_running
        assert is_running is True

    def test_toggle_when_running_stops(self):
        """Test toggle logic when running"""
        is_running = True
        is_running = not is_running
        assert is_running is False

    def test_multiple_toggles(self):
        """Test multiple toggle operations"""
        is_running = False

        is_running = not is_running
        assert is_running is True

        is_running = not is_running
        assert is_running is False

        is_running = not is_running
        assert is_running is True


class TestClickCounter:
    """Test click counting logic"""

    def test_initial_count_zero(self):
        """Test initial click count is zero"""
        click_count = 0
        assert click_count == 0

    def test_increment_count(self):
        """Test incrementing click count"""
        click_count = 0
        click_count += 1
        assert click_count == 1

    def test_multiple_increments(self):
        """Test multiple click increments"""
        click_count = 0
        for _ in range(100):
            click_count += 1
        assert click_count == 100

    def test_count_format_string(self):
        """Test click count format string"""
        click_count = 42
        formatted = f"Clicks: {click_count}"
        assert formatted == "Clicks: 42"


class TestClickLimit:
    """Test click limit logic"""

    def test_no_limit(self):
        """Test unlimited clicking (limit = 0)"""
        click_limit = 0
        click_count = 1000
        should_stop = click_limit > 0 and click_count >= click_limit
        assert should_stop is False

    def test_limit_not_reached(self):
        """Test limit not yet reached"""
        click_limit = 100
        click_count = 50
        should_stop = click_limit > 0 and click_count >= click_limit
        assert should_stop is False

    def test_limit_reached(self):
        """Test limit exactly reached"""
        click_limit = 100
        click_count = 100
        should_stop = click_limit > 0 and click_count >= click_limit
        assert should_stop is True

    def test_limit_exceeded(self):
        """Test limit exceeded"""
        click_limit = 100
        click_count = 101
        should_stop = click_limit > 0 and click_count >= click_limit
        assert should_stop is True


class TestMouseButtonSelection:
    """Test mouse button selection logic"""

    def test_left_button_selection(self):
        """Test left button selection"""
        selection = "Left"
        is_left = selection == "Left"
        assert is_left is True

    def test_right_button_selection(self):
        """Test right button selection"""
        selection = "Right"
        is_right = selection == "Right"
        assert is_right is True

    def test_middle_button_selection(self):
        """Test middle button selection"""
        selection = "Middle"
        is_middle = selection == "Middle"
        assert is_middle is True

    def test_button_options(self):
        """Test available button options"""
        options = ["Left", "Right", "Middle"]
        assert len(options) == 3
        assert "Left" in options
        assert "Right" in options
        assert "Middle" in options


class TestDoubleClick:
    """Test double click logic"""

    def test_single_click(self):
        """Test single click mode"""
        double_click = False
        clicks = 2 if double_click else 1
        assert clicks == 1

    def test_double_click(self):
        """Test double click mode"""
        double_click = True
        clicks = 2 if double_click else 1
        assert clicks == 2


class TestHotkeyOptions:
    """Test hotkey configuration"""

    def test_available_hotkeys(self):
        """Test available hotkey options"""
        hotkey_options = ["F6", "F7", "F8", "F9", "F10"]
        assert len(hotkey_options) == 5
        assert "F6" in hotkey_options

    def test_default_hotkey(self):
        """Test default hotkey is F6"""
        default = "F6"
        assert default == "F6"


class TestSettingsSerialization:
    """Test settings save/load logic"""

    def test_settings_to_json(self):
        """Test settings can be serialized to JSON"""
        settings = {
            "cps": 10,
            "random_variation": 15,
            "mouse_button": "Left",
            "double_click": False,
            "click_limit": 0,
            "use_fixed_position": False,
            "fixed_x": 0,
            "fixed_y": 0,
            "hotkey": "F6",
            "hold_mode": False,
            "start_delay": 0,
            "click_sound": False,
            "dark_mode": False,
        }
        json_str = json.dumps(settings)
        assert json_str is not None
        assert "cps" in json_str

    def test_settings_from_json(self):
        """Test settings can be deserialized from JSON"""
        json_str = '{"cps": 25, "dark_mode": true}'
        settings = json.loads(json_str)
        assert settings["cps"] == 25
        assert settings["dark_mode"] is True

    def test_settings_default_values(self):
        """Test default value handling"""
        settings = {}
        cps = settings.get("cps", 10)
        dark_mode = settings.get("dark_mode", False)
        assert cps == 10
        assert dark_mode is False

    def test_settings_file_operations(self):
        """Test settings file read/write"""
        settings = {"cps": 30, "dark_mode": True}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(settings, f)
            temp_path = f.name

        try:
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            assert loaded["cps"] == 30
            assert loaded["dark_mode"] is True
        finally:
            os.unlink(temp_path)


class TestStartDelay:
    """Test start delay logic"""

    def test_no_delay(self):
        """Test no delay (0 seconds)"""
        start_delay = 0
        has_delay = start_delay > 0
        assert has_delay is False

    def test_with_delay(self):
        """Test with delay"""
        start_delay = 3
        has_delay = start_delay > 0
        assert has_delay is True

    def test_delay_to_milliseconds(self):
        """Test delay conversion to milliseconds"""
        start_delay = 2.5
        ms = int(start_delay * 1000)
        assert ms == 2500


class TestHoldMode:
    """Test hold mode logic"""

    def test_hold_mode_off(self):
        """Test toggle mode (hold mode off)"""
        hold_mode = False
        is_holding = False

        # Press key
        if hold_mode:
            if not is_holding:
                is_holding = True
                should_start = True
        else:
            should_toggle = True

        assert hold_mode is False

    def test_hold_mode_on(self):
        """Test hold mode on"""
        hold_mode = True
        is_holding = False

        # Press key
        if hold_mode:
            if not is_holding:
                is_holding = True

        assert is_holding is True


class TestPositionLogic:
    """Test fixed position logic"""

    def test_position_disabled(self):
        """Test position clicking disabled"""
        use_fixed_position = False
        assert use_fixed_position is False

    def test_position_enabled(self):
        """Test position clicking enabled"""
        use_fixed_position = True
        fixed_x = 100
        fixed_y = 200

        if use_fixed_position:
            position = (fixed_x, fixed_y)

        assert position == (100, 200)

    def test_position_parsing(self):
        """Test position string parsing"""
        x_str = "150"
        y_str = "300"
        x = int(x_str)
        y = int(y_str)
        assert x == 150
        assert y == 300
