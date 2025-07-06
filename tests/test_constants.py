from src.utils.constants import (
    AGE_CHOICES,
    FILENAME_TO_MEASUREMENT_TYPE,
    MONTH,
    WEEK,
    YEAR,
)


class TestConstants:
    """Test suite for constants module."""

    def test_time_constants(self):
        """Test basic time constants."""
        assert WEEK == 7
        assert MONTH == 30.44
        assert YEAR == 365.25

    def test_age_choices_structure(self):
        """Test structure of AGE_CHOICES."""
        assert isinstance(AGE_CHOICES, dict)

        # Check that all age choices have tuples with two elements
        for key, value in AGE_CHOICES.items():
            assert isinstance(value, tuple)
            assert len(value) == 2
            assert isinstance(value[0], (int, float))
            assert isinstance(value[1], (int, float))
            assert value[0] < value[1]  # Start age should be less than end age

    def test_age_choices_specific_values(self):
        """Test specific values in AGE_CHOICES."""
        # Test 0-2 years
        assert AGE_CHOICES["0-2"] == (0, int(2 * YEAR))
        assert AGE_CHOICES["0-2"] == (0, int(2 * 365.25))

        # Test 2-5 years
        assert AGE_CHOICES["2-5"] == (int(2 * YEAR), int(5 * YEAR))

        # Test 5-10 years
        assert AGE_CHOICES["5-10"] == (int(5 * YEAR), int(10 * YEAR))

        # Test 10-19 years
        assert AGE_CHOICES["10-19"] == (int(10 * YEAR), int(19 * YEAR))

        # Test newborn (gestational age)
        assert AGE_CHOICES["newborn"] == (168, 300)

        # Test very preterm (gestational age)
        assert AGE_CHOICES["very_preterm"] == (189, 448)

    def test_age_choices_non_overlapping(self):
        """Test that age ranges don't overlap inappropriately."""
        # Test that ranges are in logical order
        assert AGE_CHOICES["0-2"][1] == AGE_CHOICES["2-5"][0]
        assert AGE_CHOICES["2-5"][1] == AGE_CHOICES["5-10"][0]
        assert AGE_CHOICES["5-10"][1] == AGE_CHOICES["10-19"][0]

    def test_filename_to_measurement_type_structure(self):
        """Test structure of FILENAME_TO_MEASUREMENT_TYPE."""
        assert isinstance(FILENAME_TO_MEASUREMENT_TYPE, dict)

        # Check that all entries have the required keys
        required_keys = {"source", "measurement_type", "age_group"}
        for filename, mapping in FILENAME_TO_MEASUREMENT_TYPE.items():
            assert isinstance(mapping, dict)
            assert set(mapping.keys()) == required_keys
            assert isinstance(mapping["source"], str)
            assert isinstance(mapping["measurement_type"], str)
            assert isinstance(mapping["age_group"], str)

    def test_filename_to_measurement_type_intergrowth_entries(self):
        """Test Intergrowth-21st entries in FILENAME_TO_MEASUREMENT_TYPE."""
        # Test birth size entries
        birth_size_entries = [
            "intergrowth_21st_birth_size_head_circumference_for_gestational_age",
            "intergrowth_21st_birth_size_length_for_gestational_age",
            "intergrowth_21st_birth_size_weight_for_gestational_age",
        ]

        for entry in birth_size_entries:
            assert entry in FILENAME_TO_MEASUREMENT_TYPE
            mapping = FILENAME_TO_MEASUREMENT_TYPE[entry]
            assert mapping["source"] == "intergrowth_21st"
            assert mapping["age_group"] == "birth_size"
            assert "for_gestational_age" in mapping["measurement_type"]

        # Test very preterm entries
        very_preterm_entries = [
            "intergrowth_21st_very_preterm_growth_head_circumference_for_age",
            "intergrowth_21st_very_preterm_growth_length_for_age",
            "intergrowth_21st_very_preterm_growth_weight_for_age",
        ]

        for entry in very_preterm_entries:
            assert entry in FILENAME_TO_MEASUREMENT_TYPE
            mapping = FILENAME_TO_MEASUREMENT_TYPE[entry]
            assert mapping["source"] == "intergrowth_21st"
            assert mapping["age_group"] == "very_preterm"
            assert "for_age" in mapping["measurement_type"]

    def test_filename_to_measurement_type_who_entries(self):
        """Test WHO entries in FILENAME_TO_MEASUREMENT_TYPE."""
        # Test WHO BMI entry
        who_bmi_entry = "who_growth_0_to_2_body_mass_index_for_age"
        assert who_bmi_entry in FILENAME_TO_MEASUREMENT_TYPE
        mapping = FILENAME_TO_MEASUREMENT_TYPE[who_bmi_entry]
        assert mapping["source"] == "who"
        assert mapping["measurement_type"] == "body_mass_index_for_age"
        assert mapping["age_group"] == "0-2"

    def test_measurement_types_consistency(self):
        """Test consistency of measurement types."""
        # Collect all measurement types
        measurement_types = set()
        for mapping in FILENAME_TO_MEASUREMENT_TYPE.values():
            measurement_types.add(mapping["measurement_type"])

        # Check that measurement types follow expected patterns
        expected_patterns = ["for_gestational_age", "for_age", "for_height", "for_length"]

        for measurement_type in measurement_types:
            # Each measurement type should contain at least one expected pattern
            has_pattern = any(pattern in measurement_type for pattern in expected_patterns)
            assert has_pattern, f"Measurement type '{measurement_type}' doesn't follow expected patterns"

    def test_sources_consistency(self):
        """Test consistency of sources."""
        # Collect all sources
        sources = set()
        for mapping in FILENAME_TO_MEASUREMENT_TYPE.values():
            sources.add(mapping["source"])

        # Check expected sources
        expected_sources = {"intergrowth_21st", "who"}
        assert sources.issubset(expected_sources), f"Unexpected sources found: {sources - expected_sources}"

    def test_age_groups_consistency(self):
        """Test consistency of age groups."""
        # Collect all age groups
        age_groups = set()
        for mapping in FILENAME_TO_MEASUREMENT_TYPE.values():
            age_groups.add(mapping["age_group"])

        # Check that age groups are reasonable
        expected_age_groups = {"birth_size", "very_preterm", "0-2", "2-5", "5-10", "10-19"}

        # All age groups should be in expected set
        unexpected_age_groups = age_groups - expected_age_groups
        assert len(unexpected_age_groups) == 0, f"Unexpected age groups: {unexpected_age_groups}"

    def test_gestational_age_ranges(self):
        """Test gestational age ranges are reasonable."""
        # Newborn range should be reasonable (24-43 weeks approximately)
        newborn_start, newborn_end = AGE_CHOICES["newborn"]
        assert 20 * WEEK < newborn_start < 25 * WEEK  # Around 24 weeks
        assert 42 * WEEK < newborn_end < 44 * WEEK  # Around 43 weeks

        # Very preterm range should be reasonable (27-64 weeks approximately)
        vp_start, vp_end = AGE_CHOICES["very_preterm"]
        assert 26 * WEEK < vp_start < 28 * WEEK  # Around 27 weeks
        assert 63 * WEEK < vp_end < 65 * WEEK  # Around 64 weeks

    def test_postnatal_age_ranges(self):
        """Test postnatal age ranges are reasonable."""
        # Check that ranges convert to reasonable years
        for age_range, (start_days, end_days) in AGE_CHOICES.items():
            if age_range not in ["newborn", "very_preterm"]:
                start_years = start_days / YEAR
                end_years = end_days / YEAR

                # Ages should be reasonable for pediatric use
                assert 0 <= start_years <= 20
                assert 0 <= end_years <= 20
                assert start_years < end_years
