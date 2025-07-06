# WHO - https://www.who.int/tools/child-growth-standards/standards/

cd data/raw/who-child-growth-standards

# Length/height-for-age
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/expandable-tables/lhfa-boys-zscore-expanded-tables.xlsx -O "who-child_growth-stature-m.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-height-for-age/expandable-tables/lhfa-girls-zscore-expanded-tables.xlsx -O "who-child_growth-stature-f.xlsx"

# Weight-for-age
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-age/expanded-tables/wfa-boys-zscore-expanded-tables.xlsx -O "who-child_growth-weight-m.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-age/expanded-tables/wfa-girls-zscore-expanded-tables.xlsx -O "who-child_growth-weight-f.xlsx"

# Weight-for-length (0-2 years)
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-length-height/expanded-tables/wfl-boys-zscore-expanded-table.xlsx -O "who-child_growth-weight_length-m.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-length-height/expanded-tables/wfl-girls-zscore-expanded-table.xlsx -O "who-child_growth-weight_length-f.xlsx"

# Weight-for-height (2-5 years)
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-length-height/expanded-tables/wfh-boys-zscore-expanded-tables.xlsx -O "who-child_growth-weight_height-m.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-for-length-height/expanded-tables/wfh-girls-zscore-expanded-tables.xlsx -O "who-child_growth-weight_height-f.xlsx"

# Body mass index-for-age
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/body-mass-index-for-age/expanded-tables/bfa-boys-zscore-expanded-tables.xlsx -O "who-child_growth-body_mass_index-m.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/body-mass-index-for-age/expanded-tables/bfa-girls-zscore-expanded-tables.xlsx -O "who-child_growth-body_mass_index-f.xlsx"

# Head circumference-for-age
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/head-circumference-for-age/expanded-tables/hcfa-boys-zscore-expanded-tables.xlsx -O "who-child_growth-head_circumference-m.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/head-circumference-for-age/expanded-tables/hcfa-girls-zscore-expanded-tables.xlsx -O "who-child_growth-head_circumference-f.xlsx"

# Weight velocity - 1 month
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-velocity/ttt-weight-boys-1mon-z.xlsx -O "who-child_growth-weight_velocity-m-1mon.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-velocity/ttt-weight-girls-1mon-z.xlsx -O "who-child_growth-weight_velocity-f-1mon.xlsx"

# Weight velocity - 2 months
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-velocity/ttt-weight-boys-2mon-z.xlsx -O "who-child_growth-weight_velocity-m-2mon.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/weight-velocity/ttt-weight-girls-2mon-z.xlsx -O "who-child_growth-weight_velocity-f-2mon.xlsx"

# Length/height velocity - 2 months
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-velocity/ttt_length_boys_2mon_z.xlsx -O "who-child_growth-length_velocity-m.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/length-velocity/ttt_length_girls_2mon_z.xlsx -O "who-child_growth-length_velocity-f.xlsx"

# Head circumference velocity - 2 months
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/head-circumference-velocity/ttt_headc_boys_2mon_z.xlsx -O "who-child_growth-head_circumference_velocity-m.xlsx"
wget https://cdn.who.int/media/docs/default-source/child-growth/child-growth-standards/indicators/head-circumference-velocity/ttt_headc_girls_2mon_z.xlsx -O "who-child_growth-head_circumference_velocity-f.xlsx"
