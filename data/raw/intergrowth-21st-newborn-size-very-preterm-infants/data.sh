# Intergrowth 21st - https://intergrowth21.com/tools-resources/newborn-size-very-preterm-infants

cd data/raw/intergrowth-21st-newborn-size-very-preterm-infants

# # Birthweight standards
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-ct-boys_bw_table.pdf -O intergrowth_very-preterm-birth_wfa_boys_perc.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-zs-boys_bw_table.pdf -O intergrowth_very-preterm-birth_wfa_boys_z.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-ct-girls_bw_table.pdf -O intergrowth_very-preterm-birth_wfa_girls_perc.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-zs-girls_bw_table.pdf -O intergrowth_very-preterm-birth_wfa_girls_z.pdf

# # Head Circumference standards
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-ct-boys_hc_table.pdf -O intergrowth_very-preterm-birth_hcfa_boys_perc.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-zs-boys_hc_table.pdf -O intergrowth_very-preterm-birth_hcfa_boys_z.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-ct-girls_hc_table.pdf -O intergrowth_very-preterm-birth_hcfa_girls_perc.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-zs-girls_hc_table.pdf -O intergrowth_very-preterm-birth_hcfa_girls_z.pdf

# # Length standards
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-ct-boys_lt_table.pdf -O intergrowth_very-preterm-birth_lfa_boys_perc.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-zs-boys_lt_table.pdf -O intergrowth_very-preterm-birth_lfa_boys_z.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-ct-girls_lt_table.pdf -O intergrowth_very-preterm-birth_lfa_girls_perc.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-zs-girls_lt_table.pdf -O intergrowth_very-preterm-birth_lfa_girls_z.pdf

# # Weight-length ratio standards
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-wlr-ct-boys_table.pdf -O intergrowth_very-preterm-birth_wlr_boys_perc.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-wlr-zs-boys_table.pdf -O intergrowth_very-preterm-birth_wlr_boys_z.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-wlr-ct-girls_table.pdf -O intergrowth_very-preterm-birth_wlr_girls_perc.pdf
# wget https://intergrowth21.com/sites/default/files/2023-01/grow_verypreterm-wlr-zs-girls_table.pdf -O intergrowth_very-preterm-birth_wlr_girls_z.pdf

# Rename files: replace 'female' with 'girls' and 'male' with 'boys'
for f in *female*; do
    newname="${f//female/girls}"
    mv "$f" "$newname"
done

for f in *male*; do
    newname="${f//male/boys}"
    mv "$f" "$newname"
done