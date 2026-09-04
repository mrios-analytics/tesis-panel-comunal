clear all
cls

use "output/thesis_commune_year_panel_1982_2017.dta", clear

keep if inlist(year, 1982, 1992, 2002, 2017)

gen gini_100 = gini * 100
gen fgt0_100 = fgt0 * 100

* Identificar comunas con 20% o más de ruralidad en 1982
bysort cut_2026: egen rural_1982 = max(cond(year == 1982, rural_share, .))

gen rural_sample = .
replace rural_sample = 1 if rural_1982 >= 20
replace rural_sample = 0 if rural_1982 < 20

label variable rural_sample "Comuna con 20% o más de ruralidad en 1982"


* Pobreza

ivreg2 fgt0_100 schooling dependency_rate sh_second_pea sh_third_pea i.region_id#i.year (ln_UF_pop_cum = share_eligible_area), cluster(cut_2026) first

ivreg2 fgt0_100 schooling dependency_rate sh_second_pea sh_third_pea i.region_id#i.year (ln_UF_pop_cum = share_eligible_area) if rural_sample == 1, cluster(cut_2026) first


* Desigualdad

ivreg2 gini_100 schooling dependency_rate sh_second_pea sh_third_pea i.region_id#i.year (ln_UF_pop_cum = share_eligible_area), cluster(cut_2026) first

ivreg2 gini_100 schooling dependency_rate sh_second_pea sh_third_pea i.region_id#i.year (ln_UF_pop_cum = share_eligible_area) if rural_sample == 1, cluster(cut_2026) first