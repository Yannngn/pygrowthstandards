WEEK = 7  # Days in a week
MONTH = 30.44  # Average days in a month
YEAR = 365.25  # Average days in a year

AGE_CHOICES = {
    "0-2": (0, int(2 * YEAR)),
    "2-5": (int(2 * YEAR), int(5 * YEAR)),
    "5-10": (int(5 * YEAR), int(10 * YEAR)),
    "10-19": (int(10 * YEAR), int(19 * YEAR)),
    "newborn": (168, 300),  # Gestational age
    "very_preterm": (189, 448),  # Gestational age for very preterm infants
}


FILENAME_TO_MEASUREMENT_TYPE = {
    "intergrowth_21st_birth_size_head_circumference_for_gestational_age": {
        "source": "intergrowth_21st",
        "measurement_type": "head_circumference_for_gestational_age",
        "age_group": "birth_size",
    },
    "intergrowth_21st_birth_size_length_for_gestational_age": {
        "source": "intergrowth_21st",
        "measurement_type": "length_for_gestational_age",
        "age_group": "birth_size",
    },
    "intergrowth_21st_birth_size_weight_for_gestational_age": {
        "source": "intergrowth_21st",
        "measurement_type": "weight_for_gestational_age",
        "age_group": "birth_size",
    },
    "intergrowth_21st_very_preterm_growth_head_circumference_for_age": {
        "source": "intergrowth_21st",
        "measurement_type": "head_circumference_for_age",
        "age_group": "very_preterm",
    },
    "intergrowth_21st_very_preterm_growth_length_for_age": {
        "source": "intergrowth_21st",
        "measurement_type": "length_for_age",
        "age_group": "very_preterm",
    },
    "intergrowth_21st_very_preterm_growth_weight_for_age": {
        "source": "intergrowth_21st",
        "measurement_type": "weight_for_age",
        "age_group": "very_preterm",
    },
    "who_growth_0_to_2_body_mass_index_for_age": {
        "source": "who",
        "measurement_type": "body_mass_index_for_age",
        "age_group": "0-2",
    },
    "who_growth_0_to_2_head_circumference_for_age": {
        "source": "who",
        "measurement_type": "head_circumference_for_age",
        "age_group": "0-2",
    },
    "who_growth_0_to_2_length_for_age": {
        "source": "who",
        "measurement_type": "length_for_age",
        "age_group": "0-2",
    },
    "who_growth_0_to_2_weight_for_age": {
        "source": "who",
        "measurement_type": "weight_for_age",
        "age_group": "0-2",
    },
    "who_growth_2_to_5_body_mass_index_for_age": {
        "source": "who",
        "measurement_type": "body_mass_index_for_age",
        "age_group": "2-5",
    },
    "who_growth_2_to_5_head_circumference_for_age": {
        "source": "who",
        "measurement_type": "head_circumference_for_age",
        "age_group": "2-5",
    },
    "who_growth_2_to_5_height_for_age": {
        "source": "who",
        "measurement_type": "height_for_age",
        "age_group": "2-5",
    },
    "who_growth_2_to_5_weight_for_age": {
        "source": "who",
        "measurement_type": "weight_for_age",
        "age_group": "2-5",
    },
    "who_growth_5_to_10_body_mass_index_for_age": {
        "source": "who",
        "measurement_type": "body_mass_index_for_age",
        "age_group": "5-10",
    },
    "who_growth_5_to_10_height_for_age": {
        "source": "who",
        "measurement_type": "height_for_age",
        "age_group": "5-10",
    },
    "who_growth_5_to_10_weight_for_age": {
        "source": "who",
        "measurement_type": "weight_for_age",
        "age_group": "5-10",
    },
    "who_growth_10_to_19_body_mass_index_for_age": {
        "source": "who",
        "measurement_type": "body_mass_index_for_age",
        "age_group": "10-19",
    },
    "who_growth_10_to_19_height_for_age": {
        "source": "who",
        "measurement_type": "height_for_age",
        "age_group": "10-19",
    },
}
