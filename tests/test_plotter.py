"""Tests for the plotter module."""

import os
import tempfile
import unittest
from datetime import date
from unittest.mock import patch

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from src.calculator.child import Child
from src.calculator.measurement import Measurement
from src.calculator.plotter import Plotter


class TestPlotter(unittest.TestCase):
    """Test cases for the Plotter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.child = Child(sex="M", birthday_date=date(2020, 1, 1))
        self.plotter = Plotter(self.child)

        # Add some test measurements
        self.plotter._measurements = [
            Measurement(date=date(2020, 6, 1), weight=7.5, stature=65.0),
            Measurement(date=date(2020, 12, 1), weight=9.2, stature=75.0),
            Measurement(date=date(2021, 6, 1), weight=11.0, stature=80.0),
        ]

    def test_init(self):
        """Test plotter initialization."""
        self.assertEqual(self.plotter.child, self.child)
        self.assertEqual(self.plotter._data.sex, "M")
        self.assertIsInstance(self.plotter._measurements, list)

    def test_plot_table_basic(self):
        """Test basic table plotting functionality."""
        with patch("matplotlib.pyplot.show"):
            ax = self.plotter.plot_table("weight", show=False)
            self.assertIsInstance(ax, Axes)
            self.assertTrue(ax.get_xlabel())
            self.assertTrue(ax.get_ylabel())
            self.assertTrue(ax.get_title())

    def test_plot_table_with_custom_lines(self):
        """Test table plotting with custom percentile lines."""
        with patch("matplotlib.pyplot.show"):
            ax = self.plotter.plot_table("weight", lines=[-2, 0, 2], show=False)
            self.assertIsInstance(ax, Axes)

    def test_plot_table_with_age_group(self):
        """Test table plotting with different age groups."""
        with patch("matplotlib.pyplot.show"):
            ax = self.plotter.plot_table("weight", age_group="2-5", show=False)
            self.assertIsInstance(ax, Axes)

    def test_plot_table_with_output_path(self):
        """Test table plotting with output path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_plot.png")

            with patch("matplotlib.pyplot.show"):
                ax = self.plotter.plot_table("weight", output_path=output_path, show=False)
                self.assertIsInstance(ax, Axes)
                self.assertTrue(os.path.exists(output_path))

    def test_plot_measurements_basic(self):
        """Test basic measurements plotting."""
        with patch("matplotlib.pyplot.show"):
            ax = self.plotter.plot_measurements("weight", show=False)
            self.assertIsInstance(ax, Axes)

    def test_plot_measurements_with_custom_parameters(self):
        """Test measurements plotting with custom parameters."""
        with patch("matplotlib.pyplot.show"):
            ax = self.plotter.plot_measurements("weight", age_group="0-2", lines=[-1, 0, 1], show=False)
            self.assertIsInstance(ax, Axes)

    def test_plot_measurements_with_output_path(self):
        """Test measurements plotting with output path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_measurements.png")

            with patch("matplotlib.pyplot.show"):
                ax = self.plotter.plot_measurements("weight", output_path=output_path, show=False)
                self.assertIsInstance(ax, Axes)
                self.assertTrue(os.path.exists(output_path))

    def test_age_plot(self):
        """Test age-based plotting."""
        with patch("matplotlib.pyplot.show"):
            ax = self.plotter._age_plot("weight", show=False)
            self.assertIsInstance(ax, Axes)

    def test_measurement_plot(self):
        """Test measurement-based plotting."""
        with patch("matplotlib.pyplot.show"):
            ax = self.plotter._measurement_plot("weight_length", show=False)
            self.assertIsInstance(ax, Axes)

    def test_plot_generic(self):
        """Test generic plotting method."""
        test_values = {"x": [1.0, 2, 3, 4, 5], "-2": [10, 11, 12, 13, 14], "0": [15, 16, 17, 18, 19], "2": [20, 21, 22, 23, 24]}

        with patch("matplotlib.pyplot.show"):
            ax = self.plotter._plot(test_values, x_label="Test X", y_label="Test Y")
            self.assertIsInstance(ax, Axes)
            self.assertEqual(ax.get_xlabel(), "Test x")
            self.assertEqual(ax.get_ylabel(), "Test y")

    def test_plot_with_existing_axes(self):
        """Test plotting on existing axes."""
        fig, ax = plt.subplots()

        with patch("matplotlib.pyplot.show"):
            result_ax = self.plotter.plot_table("weight", ax=ax, show=False)
            self.assertEqual(result_ax, ax)

        plt.close(fig)

    def test_save_plot_not_implemented(self):
        """Test that save_plot raises NotImplementedError."""
        with self.assertRaises(NotImplementedError):
            self.plotter.save_plot("test.png")

    def test_plotter_inheritance(self):
        """Test that Plotter inherits from Handler."""
        from src.calculator.handler import Handler

        self.assertIsInstance(self.plotter, Handler)

    def test_measurements_property(self):
        """Test measurements property access."""
        self.assertEqual(len(self.plotter._measurements), 3)
        self.assertIsInstance(self.plotter._measurements[0], Measurement)

    def test_child_property(self):
        """Test child property access."""
        self.assertEqual(self.plotter.child.sex, "M")
        self.assertEqual(self.plotter.child.birthday_date, date(2020, 1, 1))

    def test_data_property(self):
        """Test data property access."""
        self.assertEqual(self.plotter._data.sex, "M")


if __name__ == "__main__":
    unittest.main()
