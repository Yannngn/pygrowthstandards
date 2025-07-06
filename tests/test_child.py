import datetime

import pytest

from src.calculator.child import Child


class TestChild:
    """Test suite for the Child class."""

    def test_init_basic(self):
        """Test basic initialization."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M")

        assert child.birthday_date == birthday
        assert child.sex == "M"
        assert child.gestational_age is None
        assert child.is_very_preterm is None
        assert child.lmp_date is None

    def test_init_with_gestational_age(self):
        """Test initialization with gestational age."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="F", gestational_age_weeks=40, gestational_age_days=2)

        assert child.birthday_date == birthday
        assert child.sex == "F"
        assert child.gestational_age == datetime.timedelta(weeks=40, days=2)
        assert child.is_very_preterm is False
        assert child.lmp_date is not None

    def test_init_very_preterm(self):
        """Test initialization with very preterm gestational age."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, sex="M", gestational_age_weeks=30, gestational_age_days=5)

        assert child.is_very_preterm is True
        assert child.chronological_age is not None

    def test_init_default_sex(self):
        """Test initialization with default sex."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        assert child.sex == "U"

    def test_set_gestational_age(self):
        """Test setting gestational age after initialization."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        child.set_gestational_age(38, 3)

        assert child.gestational_age == datetime.timedelta(weeks=38, days=3)
        assert child.is_very_preterm is False
        assert child.lmp_date is not None

    def test_set_gestational_age_very_preterm(self):
        """Test setting very preterm gestational age."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        child.set_gestational_age(28, 0)

        assert child.gestational_age == datetime.timedelta(weeks=28, days=0)
        assert child.is_very_preterm is True
        assert child.chronological_age is not None

    def test_age_calculation_normal(self):
        """Test age calculation for normal child."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        test_date = datetime.date(2023, 6, 1)
        age = child.age(test_date)

        expected_age = test_date - birthday
        assert age == expected_age

    def test_age_calculation_today(self):
        """Test age calculation for today's date."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        age = child.age()
        expected_age = datetime.date.today() - birthday
        assert age == expected_age

    def test_age_calculation_very_preterm_within_64_weeks(self):
        """Test age calculation for very preterm child within 64 weeks."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=28)

        # Test within 64 weeks from LMP
        test_date = birthday + datetime.timedelta(weeks=20)
        age = child.age(test_date)

        # Should be calculated from LMP date
        expected_age = test_date - child.lmp_date
        assert age == expected_age

    def test_age_calculation_very_preterm_beyond_64_weeks(self):
        """Test age calculation for very preterm child beyond 64 weeks."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=28)

        # Test beyond 64 weeks from LMP
        test_date = birthday + datetime.timedelta(weeks=70)
        age = child.age(test_date)

        # Should be calculated from birthday
        expected_age = test_date - birthday
        assert age == expected_age

    def test_age_calculation_very_preterm_no_lmp(self):
        """Test age calculation for very preterm child without LMP."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)
        child.is_very_preterm = True  # Set manually without gestational age

        with pytest.raises(ValueError, match="LMP date is not set"):
            child.age()

    def test_term_status_none(self):
        """Test term status when gestational age is None."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        assert child.term is None

    def test_term_status_extreme_preterm(self):
        """Test term status for extreme preterm."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=26)

        assert child.term == "extreme_preterm"

    def test_term_status_very_preterm(self):
        """Test term status for very preterm."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=30)

        assert child.term == "very_preterm"

    def test_term_status_moderate_preterm(self):
        """Test term status for moderate preterm."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=33)

        assert child.term == "moderate_preterm"

    def test_term_status_late_preterm(self):
        """Test term status for late preterm."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=35)

        assert child.term == "late_preterm"

    def test_term_status_early_term(self):
        """Test term status for early term."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=37)

        assert child.term == "early_term"

    def test_term_status_full_term(self):
        """Test term status for full term."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=40)

        assert child.term == "full_term"

    def test_term_status_postterm(self):
        """Test term status for postterm."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=43)

        assert child.term == "postterm"

    def test_term_status_simplified(self):
        """Test simplified term status."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=35)

        simplified_term = child._get_term_status(simplified=True)
        assert simplified_term == "preterm"

    def test_chronological_age_calculation(self):
        """Test chronological age calculation."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=28)

        chronological_age = child._get_chronological_age()
        expected_age = datetime.date.today() - child.lmp_date
        assert chronological_age == expected_age

    def test_chronological_age_no_lmp(self):
        """Test chronological age calculation without LMP."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        with pytest.raises(ValueError, match="Gestational age must be given"):
            child._get_chronological_age()

    def test_str_representation(self):
        """Test string representation."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        str_repr = str(child)
        assert "child(birthday_date=01-01-2023" in str_repr
        assert "age=" in str_repr

    def test_birth_weight_status_extreme_low(self):
        """Test birth weight status for extreme low birth weight."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        status = child._get_birth_weight_status(0.8)
        assert status == "extreme_low_birth_weight"

    def test_birth_weight_status_very_low(self):
        """Test birth weight status for very low birth weight."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        status = child._get_birth_weight_status(1.2)
        assert status == "very_low_birth_weight"

    def test_birth_weight_status_low(self):
        """Test birth weight status for low birth weight."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        status = child._get_birth_weight_status(2.0)
        assert status == "low_birth_weight"

    def test_birth_weight_status_normal(self):
        """Test birth weight status for normal birth weight."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday)

        status = child._get_birth_weight_status(3.5)
        assert status == "normal_birth_weight"

    def test_lmp_date_calculation(self):
        """Test LMP date calculation."""
        birthday = datetime.date(2023, 1, 1)
        child = Child(birthday_date=birthday, gestational_age_weeks=40)

        expected_lmp = birthday - datetime.timedelta(weeks=40)
        assert child.lmp_date == expected_lmp

    def test_is_very_preterm_flag(self):
        """Test is_very_preterm flag for different gestational ages."""
        birthday = datetime.date(2023, 1, 1)

        # Test very preterm (< 32 weeks)
        child1 = Child(birthday_date=birthday, gestational_age_weeks=30)
        assert child1.is_very_preterm is True

        # Test not very preterm (>= 32 weeks)
        child2 = Child(birthday_date=birthday, gestational_age_weeks=35)
        assert child2.is_very_preterm is False

        # Test exactly 32 weeks
        child3 = Child(birthday_date=birthday, gestational_age_weeks=32)
        assert child3.is_very_preterm is False
        assert child3.is_very_preterm is False
