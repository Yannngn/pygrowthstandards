import datetime

import pytest

from src.calculator.kid import Kid


def test_kid_init_sets_attributes():
    birthday_date = datetime.date(2020, 1, 1)
    kid = Kid(sex="F", birthday_date=birthday_date, gestational_age_weeks=40)
    assert kid.sex == "F"
    assert kid.birthday_date == birthday_date
    assert kid.gestational_age_weeks == 40


def test_age_days():
    birthday_date = datetime.date(2020, 1, 1)
    kid = Kid(sex="M", birthday_date=birthday_date, gestational_age_weeks=40)
    ref_date = datetime.date(2020, 1, 11)
    assert kid.age_days(ref_date) == 10


def test_very_preterm_property():
    birthday_date = datetime.date(2020, 1, 1)
    kid = Kid(sex="F", birthday_date=birthday_date, gestational_age_weeks=27, gestational_age_days=6)
    assert hasattr(kid, "very_preterm")
    assert kid.very_preterm is True

    birthday_date = datetime.date(2020, 1, 1)
    kid = Kid(sex="F", birthday_date=birthday_date, gestational_age_weeks=28)
    assert hasattr(kid, "very_preterm")
    assert kid.very_preterm is False

def test_repr_returns_string():
    birthday_date = datetime.date(2020, 1, 1)
    kid = Kid(sex="M", birthday_date=birthday_date, gestational_age_weeks=38)
    s = repr(kid)
    assert isinstance(s, str)
