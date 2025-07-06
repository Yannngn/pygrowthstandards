# WHO - https://www.who.int/tools/growth-reference-data-for-5to19-years/indicators/

cd data/raw/who-growth-reference-data

# BMI-for-age (5-19 years)
wget "https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/bmi-for-age-(5-19-years)/bmi-boys-z-who-2007-exp.xlsx" -O "who-growth-body_mass_index-m.xlsx"
wget "https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/bmi-for-age-(5-19-years)/bmi-girls-z-who-2007-exp.xlsx" -O "who-growth-body_mass_index-f.xlsx"


# Height-for-age (5-19 years)
wget "https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/height-for-age-(5-19-years)/hfa-boys-z-who-2007-exp.xlsx" -O "who-growth-stature-m.xlsx"
wget "https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/height-for-age-(5-19-years)/hfa-girls-z-who-2007-exp.xlsx" -O "who-growth-stature-f.xlsx"


# Weight-for-age (5-10 years)
wget "https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/weight-for-age-(5-10-years)/hfa-boys-z-who-2007-exp_0ff9c43c-8cc0-4c23-9fc6-81290675e08b.xlsx" -O "who-growth-weight-m.xlsx"
wget "https://cdn.who.int/media/docs/default-source/child-growth/growth-reference-5-19-years/weight-for-age-(5-10-years)/hfa-girls-z-who-2007-exp_7ea58763-36a2-436d-bef0-7fcfbadd2820.xlsx" -O "who-growth-weight-f.xlsx"
