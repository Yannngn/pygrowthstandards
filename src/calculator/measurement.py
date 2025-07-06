import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from src.utils.stats import normal_cdf


class Measurement:
    stature_z: float | None = None
    weight_z: float | None = None
    head_circumference_z: float | None = None
    body_mass_index_z: float | None = None

    # TODO: Add more z-scores
    weight_stature_ratio_z: float | None = None

    def __init__(
        self,
        stature: float | None = None,
        weight: float | None = None,
        head_circumference: float | None = None,
        date: datetime.date = datetime.date.today(),
    ):
        """
        Initializes a Measurement instance with optional anthropometric data.

            stature (float | None, optional): The measured length or height of the subject in centimeters. Defaults to None. [cm]
            weight (float | None, optional): The measured weight of the subject in kilograms. Defaults to None. [kg]
            head_circumference (float | None, optional): The measured head circumference of the subject in centimeters. Defaults to None. [cm]
            date (datetime.date, optional): The date when the measurement was taken. Defaults to today's date.

        """
        self.stature = stature
        self.weight = weight
        self.head_circumference = head_circumference
        self.date = date

    @property
    def body_mass_index(self) -> float | None:
        if self.weight is not None and self.stature is not None:
            return 100**2 * self.weight / (self.stature**2)

        return None

    @property
    def weight_stature_ratio(self) -> float | None:
        """
        Returns the weight-to-stature ratio (kg/cm).
        """
        if self.weight is not None and self.stature is not None:
            return self.weight / self.stature

        return None

    def __str__(self):
        return f"Measurement(stature={self.stature}, weight={self.weight}, head_circumference={self.head_circumference}, body_mass_index={self.body_mass_index:.2f}, date={self.date})"

    def get_z_scores(self):
        """
        Returns the z-scores for stature, weight, head circumference, and BMI.
        """
        scores = {}
        if self.stature_z is not None:
            scores["stature"] = self.stature_z
        if self.weight_z is not None:
            scores["weight"] = self.weight_z
        if self.head_circumference_z is not None:
            scores["head_circumference"] = self.head_circumference_z
        if self.body_mass_index_z is not None:
            scores["body_mass_index"] = self.body_mass_index_z
        if self.weight_stature_ratio_z is not None:
            scores["weight_stature_ratio"] = self.weight_stature_ratio_z

        return scores

    def get_percentiles(self) -> dict[str, float]:
        """
        Returns the percentiles for length/height, weight, head circumference, and BMI.
        """

        def percentile(x):
            return normal_cdf(x)

        scores = self.get_z_scores()

        return {k: percentile(v) for k, v in scores.items()}
