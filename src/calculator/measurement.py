import datetime
import os
import sys
from dataclasses import dataclass, field
from typing import Callable

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))
from src.utils.stats import normal_cdf


@dataclass
class Measurement:
    stature: float | None = None
    weight: float | None = None
    head_circumference: float | None = None
    date: datetime.date = field(default_factory=datetime.date.today)

    body_mass_index: float | None = field(init=False, repr=False)
    weight_stature: float | None = field(init=False, repr=False)

    z_scores: dict[str, float] = field(default_factory=dict, repr=False)

    def __post_init__(self):
        if self.weight is not None and self.stature is not None:
            self.body_mass_index = pow(100, 2) * self.weight / pow(self.stature, 2)
            self.weight_stature = self.weight / self.stature

    @property
    def values(self) -> dict[str, float]:
        """
        Returns a dictionary of the measurement values.
        """
        result = {}
        if self.stature is not None:
            result["stature"] = self.stature
        if self.weight is not None:
            result["weight"] = self.weight
        if self.head_circumference is not None:
            result["head_circumference"] = self.head_circumference
        if self.body_mass_index is not None:
            result["body_mass_index"] = self.body_mass_index
        if self.weight_stature is not None:
            result["weight_stature_ratio"] = self.weight_stature
        return result

    def compute_z_scores(self, z_score_fn: Callable):
        """
        Returns the z-scores for stature, weight, head circumference, and BMI.
        """
        if self.stature is not None:
            self.z_scores["stature"] = z_score_fn(y=self.stature)
        if self.weight is not None:
            self.z_scores["weight"] = z_score_fn(y=self.weight)
        if self.head_circumference is not None:
            self.z_scores["head_circumference"] = z_score_fn(y=self.head_circumference)
        if self.body_mass_index is not None:
            self.z_scores["body_mass_index"] = z_score_fn(y=self.body_mass_index)
        if self.weight_stature is not None:
            self.z_scores["weight_stature_ratio"] = z_score_fn(y=self.weight_stature)

    def compute_centiles(self, z_score_fn: Callable | None = None) -> dict[str, float]:
        """
        Returns the centiles for length/height, weight, head circumference, and BMI.
        """

        def percentile(x):
            return normal_cdf(x)

        if self.z_scores:
            return {k: percentile(v) for k, v in self.z_scores.items()}

        if z_score_fn is None:
            raise ValueError("A z-score function must be provided to compute z-scores.")

        self.compute_z_scores(z_score_fn)

        return {k: percentile(v) for k, v in self.z_scores.items()}
