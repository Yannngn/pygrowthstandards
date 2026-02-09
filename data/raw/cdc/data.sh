#!/bin/bash

cd "$(dirname "$0")" || exit 1

# CDC - https://www.cdc.gov/growthcharts/who-data-files.htm

# Weight-for-age charts, Birth to 24 Months, LMS parameters and selected smoothed weight percentiles in kilograms, by age
wget -O cdc-child_growth-weight-m.csv https://ftp.cdc.gov/pub/Health_Statistics/NCHS/growthcharts/WHO-Boys-Weight-for-age-Percentiles.csv
wget -O cdc-child_growth-weight-f.csv https://ftp.cdc.gov/pub/Health_Statistics/NCHS/growthcharts/WHO-Girls-Weight-for-age%20Percentiles.csv

# Length-for-age charts, Birth to 24 Months, LMS parameters and selected smoothed recumbent length percentiles in centimeters, by age
wget -O cdc-child_growth-length-m.csv https://ftp.cdc.gov/pub/Health_Statistics/NCHS/growthcharts/WHO-Boys-Length-for-age-Percentiles.csv
wget -O cdc-child_growth-length-f.csv https://ftp.cdc.gov/pub/Health_Statistics/NCHS/growthcharts/WHO-Girls-Length-for-age-Percentiles.csv

# Weight-for-length charts, LMS parameters and selected smoothed weight percentiles in kilograms, by recumbent length (in centimeters)
wget -O cdc-child_growth-weight_length-m.csv https://ftp.cdc.gov/pub/Health_Statistics/NCHS/growthcharts/WHO-Boys-Weight-for-length-Percentiles.csv
wget -O cdc-child_growth-weight_length-f.csv https://ftp.cdc.gov/pub/Health_Statistics/NCHS/growthcharts/WHO-Girls-Weight-for-length-Percentiles.csv

# Head circumference-for-age charts, Birth to 24 Months, LMS parameters and selected smoothed head circumference percentiles in centimeters, by age
wget -O cdc-child_growth-head_circumference-m.csv https://ftp.cdc.gov/pub/Health_Statistics/NCHS/growthcharts/WHO-Boys-Head-Circumference-for-age-Percentiles.csv
wget -O cdc-child_growth-head_circumference-f.csv https://ftp.cdc.gov/pub/Health_Statistics/NCHS/growthcharts/WHO-Girls-Head-Circumference-for-age-Percentiles.csv