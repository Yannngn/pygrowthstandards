import datetime

from src.calculator.handler import Handler
from src.calculator.measurement import Measurement


class TestHandler:
    """Test suite for the Handler class."""

    def test_init(self):
        """Test Handler initialization."""
        handler = Handler()
        assert handler._measurements == []

    def test_add_measurement_basic(self):
        """Test adding a basic measurement."""
        handler = Handler()
        date = datetime.date(2023, 1, 1)

        handler.add_measurement(stature=110.0, weight=20.0, head_circumference=45.0, date=date)

        assert len(handler._measurements) == 1
        measurement = handler._measurements[0]
        assert measurement.stature == 110.0
        assert measurement.weight == 20.0
        assert measurement.head_circumference == 45.0
        assert measurement.date == date

    def test_add_measurement_with_defaults(self):
        """Test adding a measurement with default values."""
        handler = Handler()

        handler.add_measurement(stature=110.0)

        assert len(handler._measurements) == 1
        measurement = handler._measurements[0]
        assert measurement.stature == 110.0
        assert measurement.weight is None
        assert measurement.head_circumference is None
        assert measurement.date == datetime.date.today()

    def test_add_measurement_sorting(self):
        """Test that measurements are sorted by date."""
        handler = Handler()

        date1 = datetime.date(2023, 6, 1)
        date2 = datetime.date(2023, 1, 1)
        date3 = datetime.date(2023, 3, 1)

        handler.add_measurement(stature=110.0, date=date1)
        handler.add_measurement(stature=115.0, date=date2)
        handler.add_measurement(stature=120.0, date=date3)

        assert len(handler._measurements) == 3
        assert handler._measurements[0].date == date2  # January (earliest)
        assert handler._measurements[1].date == date3  # March
        assert handler._measurements[2].date == date1  # June (latest)

    def test_add_measurement_object(self):
        """Test adding a Measurement object."""
        handler = Handler()
        date = datetime.date(2023, 1, 1)

        measurement = Measurement(stature=110.0, weight=20.0, head_circumference=45.0, date=date)

        handler.add_measurement_object(measurement)

        assert len(handler._measurements) == 1
        assert handler._measurements[0] == measurement

    def test_add_measurement_object_sorting(self):
        """Test that measurement objects are sorted by date."""
        handler = Handler()

        date1 = datetime.date(2023, 6, 1)
        date2 = datetime.date(2023, 1, 1)

        measurement1 = Measurement(stature=110.0, date=date1)
        measurement2 = Measurement(stature=115.0, date=date2)

        handler.add_measurement_object(measurement1)
        handler.add_measurement_object(measurement2)

        assert len(handler._measurements) == 2
        assert handler._measurements[0].date == date2  # January (earlier)
        assert handler._measurements[1].date == date1  # June (later)

    def test_add_measurements_from_collections(self):
        """Test adding measurements from collections."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)

        measurements_data = [
            [110.0, 20.0, 45.0, date1],  # stature, weight, head_circumference, date
            [115.0, 22.0, 46.0, date2],
        ]

        handler.add_measurements(measurements_data)

        assert len(handler._measurements) == 2
        assert handler._measurements[0].stature == 110.0
        assert handler._measurements[0].weight == 20.0
        assert handler._measurements[0].head_circumference == 45.0
        assert handler._measurements[0].date == date1

        assert handler._measurements[1].stature == 115.0
        assert handler._measurements[1].weight == 22.0
        assert handler._measurements[1].head_circumference == 46.0
        assert handler._measurements[1].date == date2

    def test_add_measurements_from_tuples(self):
        """Test adding measurements from tuples."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)

        measurements_data = [(110.0, 20.0, 45.0, date1), (115.0, 22.0, 46.0, date2)]

        handler.add_measurements(measurements_data)

        assert len(handler._measurements) == 2
        assert handler._measurements[0].stature == 110.0
        assert handler._measurements[1].stature == 115.0

    def test_add_measurements_sorting(self):
        """Test that batch added measurements are sorted by date."""
        handler = Handler()

        date1 = datetime.date(2023, 6, 1)
        date2 = datetime.date(2023, 1, 1)
        date3 = datetime.date(2023, 3, 1)

        measurements_data = [[110.0, 20.0, 45.0, date1], [115.0, 22.0, 46.0, date2], [120.0, 24.0, 47.0, date3]]

        handler.add_measurements(measurements_data)

        assert len(handler._measurements) == 3
        assert handler._measurements[0].date == date2  # January (earliest)
        assert handler._measurements[1].date == date3  # March
        assert handler._measurements[2].date == date1  # June (latest)

    def test_add_measurement_objects_collection(self):
        """Test adding multiple Measurement objects."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)

        measurements = [Measurement(stature=110.0, weight=20.0, date=date1), Measurement(stature=115.0, weight=22.0, date=date2)]

        handler.add_measurement_objects(measurements)

        assert len(handler._measurements) == 2
        assert handler._measurements[0].stature == 110.0
        assert handler._measurements[1].stature == 115.0

    def test_add_measurement_objects_sorting(self):
        """Test that measurement objects are sorted by date."""
        handler = Handler()

        date1 = datetime.date(2023, 6, 1)
        date2 = datetime.date(2023, 1, 1)

        measurements = [Measurement(stature=110.0, date=date1), Measurement(stature=115.0, date=date2)]

        handler.add_measurement_objects(measurements)

        assert len(handler._measurements) == 2
        assert handler._measurements[0].date == date2  # January (earlier)
        assert handler._measurements[1].date == date1  # June (later)

    def test_get_measurements(self):
        """Test getting all measurements."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)

        handler.add_measurement(stature=110.0, date=date1)
        handler.add_measurement(stature=115.0, date=date2)

        measurements = handler.get_measurements()

        assert len(measurements) == 2
        assert measurements[0].stature == 110.0
        assert measurements[1].stature == 115.0

    def test_get_measurements_by_date(self):
        """Test getting measurements by specific date."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)

        handler.add_measurement(stature=110.0, date=date1)
        handler.add_measurement(stature=115.0, date=date2)
        handler.add_measurement(stature=120.0, date=date1)  # Same date as first

        measurements_date1 = handler.get_measurements_by_date(date1)
        measurements_date2 = handler.get_measurements_by_date(date2)

        assert len(measurements_date1) == 2
        assert len(measurements_date2) == 1

        # Check that both measurements for date1 are returned
        statures = [m.stature for m in measurements_date1]
        assert 110.0 in statures
        assert 120.0 in statures

        # Check that only one measurement for date2 is returned
        assert measurements_date2[0].stature == 115.0

    def test_get_measurements_by_date_not_found(self):
        """Test getting measurements by date when no measurements exist."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)

        handler.add_measurement(stature=110.0, date=date1)

        measurements = handler.get_measurements_by_date(date2)

        assert len(measurements) == 0

    def test_get_measurements_by_date_range_both_dates(self):
        """Test getting measurements by date range with both start and end dates."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)
        date3 = datetime.date(2023, 3, 1)
        date4 = datetime.date(2023, 4, 1)

        handler.add_measurement(stature=110.0, date=date1)
        handler.add_measurement(stature=115.0, date=date2)
        handler.add_measurement(stature=120.0, date=date3)
        handler.add_measurement(stature=125.0, date=date4)

        measurements = handler.get_measurements_by_date_range(date2, date3)

        assert len(measurements) == 2
        assert measurements[0].stature == 115.0  # February
        assert measurements[1].stature == 120.0  # March

    def test_get_measurements_by_date_range_start_only(self):
        """Test getting measurements by date range with only start date."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)
        date3 = datetime.date(2023, 3, 1)

        handler.add_measurement(stature=110.0, date=date1)
        handler.add_measurement(stature=115.0, date=date2)
        handler.add_measurement(stature=120.0, date=date3)

        measurements = handler.get_measurements_by_date_range(date2, None)

        assert len(measurements) == 2
        assert measurements[0].stature == 115.0  # February
        assert measurements[1].stature == 120.0  # March

    def test_get_measurements_by_date_range_end_only(self):
        """Test getting measurements by date range with only end date."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)
        date3 = datetime.date(2023, 3, 1)

        handler.add_measurement(stature=110.0, date=date1)
        handler.add_measurement(stature=115.0, date=date2)
        handler.add_measurement(stature=120.0, date=date3)

        measurements = handler.get_measurements_by_date_range(None, date2)

        assert len(measurements) == 2
        assert measurements[0].stature == 110.0  # January
        assert measurements[1].stature == 115.0  # February

    def test_get_measurements_by_date_range_no_dates(self):
        """Test getting measurements by date range with no dates specified."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)

        handler.add_measurement(stature=110.0, date=date1)
        handler.add_measurement(stature=115.0, date=date2)

        measurements = handler.get_measurements_by_date_range(None, None)

        assert len(measurements) == 2
        assert measurements[0].stature == 110.0
        assert measurements[1].stature == 115.0

    def test_get_zscores(self):
        """Test getting z-scores for all measurements."""
        handler = Handler()

        # Mock the _calculate_all method
        handler._calculate_all = lambda measurements: None

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)

        measurement1 = Measurement(stature=110.0, date=date1)
        measurement2 = Measurement(stature=115.0, date=date2)

        # Set some z-scores manually
        measurement1.stature_z = 1.0
        measurement1.weight_z = 0.5
        measurement2.stature_z = 1.5
        measurement2.head_circumference_z = -0.5

        handler.add_measurement_object(measurement1)
        handler.add_measurement_object(measurement2)

        z_scores = handler.get_zscores()

        assert len(z_scores) == 2
        assert z_scores[0]["stature"] == 1.0
        assert z_scores[0]["weight"] == 0.5
        assert z_scores[1]["stature"] == 1.5
        assert z_scores[1]["head_circumference"] == -0.5

    def test_mixed_operations(self):
        """Test mixing different add operations."""
        handler = Handler()

        date1 = datetime.date(2023, 1, 1)
        date2 = datetime.date(2023, 2, 1)
        date3 = datetime.date(2023, 3, 1)

        # Add individual measurement
        handler.add_measurement(stature=110.0, date=date2)

        # Add measurement object
        measurement = Measurement(stature=115.0, date=date1)
        handler.add_measurement_object(measurement)

        # Add measurements from collections
        measurements_data = [[120.0, 25.0, 48.0, date3]]
        handler.add_measurements(measurements_data)

        assert len(handler._measurements) == 3
        # Should be sorted by date
        assert handler._measurements[0].date == date1  # January
        assert handler._measurements[1].date == date2  # February
        assert handler._measurements[2].date == date3  # March

    def test_empty_handler_operations(self):
        """Test operations on empty handler."""
        handler = Handler()

        # Test empty get operations
        assert handler.get_measurements() == []
        assert handler.get_measurements_by_date(datetime.date(2023, 1, 1)) == []
        assert handler.get_measurements_by_date_range(datetime.date(2023, 1, 1), datetime.date(2023, 12, 31)) == []

        # Test z-scores on empty handler
        handler._calculate_all = lambda measurements: None
        assert handler.get_zscores() == []
