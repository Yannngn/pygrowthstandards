import datetime
import os
from pathlib import Path
from typing import cast

import matplotlib
import matplotlib.pyplot as plt
import pytest

from pygrowthstandards.config.growth import PLOT_GROUP_CONFIG, PlotGroup
from pygrowthstandards.oop.growth import MeasurementGroup
from pygrowthstandards.oop.patient import Patient
from pygrowthstandards.oop.plots.plotter import Plotter
from pygrowthstandards.typing.growth import MeasurementAliasType
from tests.validation_utils import get_measurements

matplotlib.use("Agg")


def _get_output_dir(tmp_path: Path) -> Path:
    env_dir = os.environ.get("PYGROWTH_PLOT_OUTPUT_DIR")
    if env_dir:
        output_dir = Path(env_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    output_dir = tmp_path / "plot_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _make_term_patient() -> Patient:
    patient = Patient(
        sex="M",
        birthday_date=datetime.date(2022, 1, 1),
        gestational_age_weeks=40,
    )

    measurements = [
        MeasurementGroup(
            table_name="child_growth",
            date=datetime.date(2022, 1, 1),
            weight=3.4,
            stature=50.0,
            head_circumference=34.0,
        ),
        MeasurementGroup(
            table_name="child_growth",
            date=datetime.date(2022, 7, 1),
            weight=8.2,
            stature=68.0,
            head_circumference=44.0,
        ),
        MeasurementGroup(
            table_name="child_growth",
            date=datetime.date(2024, 7, 1),
            weight=13.0,
            stature=90.0,
            head_circumference=48.0,
        ),
        MeasurementGroup(
            table_name="growth",
            date=datetime.date(2029, 1, 1),
            weight=23.0,
            stature=122.0,
        ),
        MeasurementGroup(
            table_name="growth",
            date=datetime.date(2035, 1, 1),
            weight=45.0,
            stature=155.0,
        ),
    ]

    for group in measurements:
        patient.add_measurements(group)

    return patient


def _make_preterm_patient() -> Patient:
    patient = Patient(
        sex="M",
        birthday_date=datetime.date(2022, 1, 1),
        gestational_age_weeks=28,
    )

    measurements = [
        MeasurementGroup(
            table_name="very_preterm_newborn",
            date=datetime.date(2022, 1, 1),
            weight=1.1,
            stature=36.0,
            head_circumference=26.0,
        ),
        MeasurementGroup(
            table_name="postnatal_growth_preterm",
            date=datetime.date(2022, 1, 15),
            weight=1.4,
            stature=38.0,
            head_circumference=27.0,
        ),
    ]

    for group in measurements:
        patient.add_measurements(group)

    return patient


def _select_patient(plot_group: str, term_patient: Patient, preterm_patient: Patient) -> Patient:
    if plot_group in {PlotGroup.VERY_PRETERM_NEWBORN.value, PlotGroup.POSTNATAL_GROWTH_PRETERM.value}:
        return preterm_patient

    return term_patient


def _select_measurements(measurements: list[str]) -> list[MeasurementAliasType]:
    if not measurements:
        return []

    preferred = ["weight", "stature", "head_circumference", "body_mass_index", "weight_stature_ratio"]
    selected = [m for m in preferred if m in measurements]

    for measurement in measurements:
        if measurement not in selected:
            if measurement in {"length", "height"}:
                selected.append("stature")
            else:
                selected.append(measurement)
        if len(selected) >= 3:
            break

    return cast(list[MeasurementAliasType], selected)


@pytest.mark.parametrize("plot_group,config", list(PLOT_GROUP_CONFIG.items()))
def test_plots_for_plot_group(tmp_path: Path, plot_group, config):
    output_dir = _get_output_dir(tmp_path)

    term_patient = _make_term_patient()
    preterm_patient = _make_preterm_patient()
    patient = _select_patient(config.name, term_patient, preterm_patient)

    measurements = get_measurements(
        plot_group=config.name,
        name=config.table_name,
        sex=patient.sex,
        x_var_type=config.x_var_type,
    )

    selected = _select_measurements(measurements)
    assert len(selected) >= 1

    plotter = Plotter(patient)

    for measurement_type in selected:
        safe_name = f"{config.name}__{measurement_type}".replace("/", "_")

        reference_path = output_dir / f"reference__{safe_name}.png"
        _ax = plotter.reference_plot(
            plot_group=config.name,
            measurement_type=measurement_type,
            show=False,
            output_path=str(reference_path),
        )
        assert reference_path.exists()
        plt.close()

        patient_path = output_dir / f"patient__{safe_name}.png"
        _ax = plotter.plot(
            plot_group=config.name,
            measurement_type=measurement_type,
            show=False,
            output_path=str(patient_path),
        )
        assert patient_path.exists()
        plt.close()
