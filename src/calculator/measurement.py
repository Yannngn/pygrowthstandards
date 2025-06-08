import datetime
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
)
from src.utils.stats import normal_cdf


class Measurement:
    length_height_z: float | None = None
    weight_z: float | None = None
    head_circumference_z: float | None = None
    bmi_z: float | None = None

    def __init__(
        self,
        length_height: float | None = None,
        weight: float | None = None,
        head_circumference: float | None = None,
        date: datetime.date = datetime.date.today(),
    ):
        """
        Initializes a Measurement instance with optional anthropometric data.

            length_height (float | None, optional): The measured length or height of the subject in centimeters. Defaults to None. [cm]
            weight (float | None, optional): The measured weight of the subject in kilograms. Defaults to None. [kg]
            head_circumference (float | None, optional): The measured head circumference of the subject in centimeters. Defaults to None. [cm]
            date (datetime.date, optional): The date when the measurement was taken. Defaults to today's date.

        """
        self.length_height = length_height
        self.weight = weight
        self.head_circumference = head_circumference
        self.date = date

    @property
    def bmi(self) -> float | None:
        if self.weight is not None and self.length_height is not None:
            return 100**2 * self.weight / (self.length_height**2)

        return None

    def __str__(self):
        return f"Measurement(length_height={self.length_height}, weight={self.weight}, head_circumference={self.head_circumference}, bmi={self.bmi:.3f}, date={self.date})"

    def get_z_scores(self):
        """
        Returns the z-scores for length/height, weight, head circumference, and BMI.
        """
        scores = {}
        if self.length_height_z is not None:
            scores["length_height"] = self.length_height_z
        if self.weight_z is not None:
            scores["weight"] = self.weight_z
        if self.head_circumference_z is not None:
            scores["head_circumference"] = self.head_circumference_z
        if self.bmi_z is not None:
            scores["bmi"] = self.bmi_z

        return scores

    def get_percentiles(self) -> dict[str, float]:
        """
        Returns the percentiles for length/height, weight, head circumference, and BMI.
        """

        def percentile(x):
            return normal_cdf(x) if x is not None else None

        percentiles = {}
        if self.length_height_z is not None:
            percentiles["length_height"] = percentile(self.length_height_z)
        if self.weight_z is not None:
            percentiles["weight"] = percentile(self.weight_z)
        if self.head_circumference_z is not None:
            percentiles["head_circumference"] = percentile(self.head_circumference_z)
        if self.bmi_z is not None:
            percentiles["bmi"] = percentile(self.bmi_z)

        return percentiles
