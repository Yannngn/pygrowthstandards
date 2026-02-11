"""Plotting utilities for the OOP API."""

from pygrowthstandards.oop.patient import Patient
from pygrowthstandards.oop.plots.development import DevelopmentPlotterMixin
from pygrowthstandards.oop.plots.growth import GrowthPlotterMixin


# TODO: review if it's better to separate growth and development plotters and call them separately in the Patient class
class Plotter(DevelopmentPlotterMixin, GrowthPlotterMixin):
    """Create reference and patient plots for growth data."""

    def __init__(self, patient: Patient):
        """Initialize the plotter with a patient instance.

        Args:
            patient: Patient containing measurements.
        """
        self.patient = patient
        self.setup()

    def setup(self):
        """Ensure patient calculations are up to date."""
        self.patient.calculate_all()
