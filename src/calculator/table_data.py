import csv
import os
import sys
from dataclasses import dataclass
from decimal import Decimal as D
from typing import Any, Literal, NamedTuple

import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))


import src.utils.stats as stats
from src.data.objects import DataPoint
from src.utils.choices import (
    AGE_GROUP_CHOICES,
    AGE_GROUP_TYPE,
    MEASUREMENT_TYPE_CHOICES,
    MEASUREMENT_TYPE_TYPE,
    TABLE_NAME_CHOICES,
    TABLE_NAME_TYPE,
)
from src.utils.errors import (
    InvalidAgeGroupError,
    InvalidKeyPairError,
    InvalidMeasurementTypeError,
    InvalidTableNameError,
)


@dataclass
class ArrayTable:
    name: Any
    measurement_type: str  # 'stature'
    sex: str  # 'F'
    unit_name: str  # 'age'

    x: np.ndarray
    L: np.ndarray
    M: np.ndarray
    S: np.ndarray

    @classmethod
    def from_points(cls, name: str, sex: str, measurement_type: str, unit_name: str, points: list[DataPoint]):
        """
        Creates an ArrayTable from a Table object.

        :param table: The Table object to convert.
        :return: An ArrayTable object.
        """
        return cls(
            name=name,
            sex=sex,
            measurement_type=measurement_type,
            unit_name=unit_name,
            x=np.array([getattr(point, "x") for point in points]).astype(float),
            L=np.array([getattr(point, "L") for point in points]).astype(float),
            M=np.array([getattr(point, "M") for point in points]).astype(float),
            S=np.array([getattr(point, "S") for point in points]).astype(float),
        )

    def add_point(self, x: int | float) -> None:
        """
        Interpolates a new point
        """
        L, M, S = stats.interpolate_lms(x_values=self.x, l_values=self.L, m_values=self.M, s_values=self.S, x=x)

        # Find the index where x should be inserted to keep the array sorted
        insert_idx = np.searchsorted(self.x, x)

        # Insert x, L, M, S at the correct position in each array
        self.x = np.insert(self.x, insert_idx, x)
        self.L = np.insert(self.L, insert_idx, L)
        self.M = np.insert(self.M, insert_idx, M)
        self.S = np.insert(self.S, insert_idx, S)

    def get_point(self, x: int | float) -> tuple[float, float, float]:
        """
        Returns the LMS values for a given x value.

        :param x: The x value for which to get the LMS values.
        :return: The LMS values.
        """
        if x not in self.x:
            self.add_point(x)

        idx = np.searchsorted(self.x, x)

        return (self.L[idx], self.M[idx], self.S[idx])


@dataclass
class PlotTable(ArrayTable):
    name: AGE_GROUP_TYPE


@dataclass
class Table(ArrayTable):
    name: TABLE_NAME_TYPE


DataType = NamedTuple(
    "DataType",
    [
        ("name", TABLE_NAME_TYPE),
        ("measurement_type", MEASUREMENT_TYPE_TYPE),
        ("sex", str),
        ("unit_name", str),
    ],
)
PlotDataType = NamedTuple(
    "PlotDataType",
    [
        ("age_group", AGE_GROUP_TYPE),
        ("measurement_type", MEASUREMENT_TYPE_TYPE),
        ("sex", str),
        ("unit_name", str),
    ],
)


class TableData:
    def __init__(self, sex: Literal["M", "F", "U"] | None, age: int | None = None, very_preterm: bool | None = None):
        self.sex = sex
        self.age = age
        self.very_preterm = very_preterm

        self.measurement_choices: list[MEASUREMENT_TYPE_TYPE] = []

        self.data, self.plot_data = self._get_data()

    def _get_data(self) -> tuple[dict[DataType, Table], dict[PlotDataType, PlotTable]]:
        """Gets up the data for various anthropometric measurements based on the child's age and preterm status."""

        data_path = os.path.join("data", "pygrowthstandards.csv")

        with open(data_path, "r", newline="") as f:
            reader = csv.DictReader(f)

            if self.sex is not None:
                assert self.sex in ["M", "F", "U"]
                sex = "F" if self.sex == "U" else self.sex

                reader = filter(lambda row: row["sex"] == sex, reader)

            if self.very_preterm is not None:
                assert isinstance(self.very_preterm, bool)

                if self.very_preterm:
                    reader = filter(lambda row: row["table"] not in ["newborn"], reader)
                    # TODO: after 64 weeks use 0-2 data for very preterm children
                else:
                    reader = filter(lambda row: row["table"] not in ["very_preterm_growth", "very_preterm_newborn"], reader)

            if self.age is not None:
                if self.age < 5:
                    reader = filter(lambda row: row["table"] not in ["growth"], reader)

            # GROUP BY
            tables: dict[DataType, list] = {}
            plot_tables: dict[PlotDataType, list] = {}
            for row in reader:
                name: TABLE_NAME_TYPE = row["table"]  # type: ignore
                age_group: AGE_GROUP_TYPE = row["age_group"]  # type: ignore
                measurement_type: MEASUREMENT_TYPE_TYPE = row["measurement_type"]  # type: ignore
                sex: str = row["sex"]
                unit_name: str = row["unit_name"]

                assert name in TABLE_NAME_CHOICES, InvalidTableNameError(name)
                assert age_group in AGE_GROUP_CHOICES, InvalidAgeGroupError(age_group)
                assert measurement_type in MEASUREMENT_TYPE_CHOICES, InvalidMeasurementTypeError(measurement_type)

                point = DataPoint(x=D(row["x"]), L=D(row["L"]), M=D(row["M"]), S=D(row["S"]))

                data_key = DataType(name, measurement_type, sex, unit_name)
                if data_key not in tables:
                    tables[data_key] = []

                plot_key = PlotDataType(age_group, measurement_type, sex, unit_name)
                if plot_key not in plot_tables:
                    plot_tables[plot_key] = []

                tables[data_key].append(point)
                plot_tables[plot_key].append(point)

        array_tables = {key: Table.from_points(*key, points=table) for key, table in tables.items()}
        array_plot_tables = {key: PlotTable.from_points(*key, points=table) for key, table in plot_tables.items()}

        return array_tables, array_plot_tables

    def get_table(
        self, name: TABLE_NAME_TYPE, measurement_type: MEASUREMENT_TYPE_TYPE, sex: str | None = None, unit_name: str = "age"
    ) -> Table:
        sex_ = (self.sex or sex) or "F"

        if measurement_type in ["weight_stature_ratio"] and unit_name == "age":
            measurement_type = "weight"
            unit_name = "stature"

        assert measurement_type in MEASUREMENT_TYPE_CHOICES, InvalidMeasurementTypeError(measurement_type)
        assert name in TABLE_NAME_CHOICES, InvalidTableNameError(name)

        data_key = DataType(name, measurement_type, sex_, unit_name)
        if data_key not in self.data:
            raise InvalidKeyPairError(name, measurement_type)

        return self.data[data_key]

    def get_plot_table(self, age_group: AGE_GROUP_TYPE, measurement_type: str, sex: str | None = None, unit_name: str = "age") -> PlotTable:
        sex_ = (self.sex or sex) or "F"

        if measurement_type in ["weight_stature_ratio"] and unit_name == "age":
            measurement_type = "weight"
            unit_name = "stature"

        assert age_group in AGE_GROUP_CHOICES, InvalidAgeGroupError(age_group)
        assert measurement_type in MEASUREMENT_TYPE_CHOICES, InvalidMeasurementTypeError(measurement_type)

        data_key = PlotDataType(age_group, measurement_type, sex_, unit_name)  # type: ignore

        if data_key not in self.plot_data:
            raise InvalidKeyPairError(age_group, measurement_type)

        return self.plot_data[data_key]

    def get_cutoffs(self, data: ArrayTable) -> tuple[int | float, int | float]:
        """
        Returns the start and end ages for the specified table.

        """
        return data.x.min(), data.x.max()

    def get_point(self, data: ArrayTable, x: int | float) -> tuple[float, float, float]:
        return data.get_point(x)
