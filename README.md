# Chilean Commune-Year Panel for Irrigation and Rural Development

This repository contains the data-processing workflow used to construct a longitudinal commune-year dataset for the analysis of irrigation subsidies, poverty, inequality, and rural development in Chile.

The final panel covers 346 communes between 1982 and 2017.

## Data

The `data/` folder contains the processed datasets used to build the final panel:

- `census_1982_commune.csv`
- `census_1992_commune.csv`
- `census_2002_commune.csv`
- `census_2017_commune.csv`
- `cut_82-92-02-17-26.csv`
- `fgt0_gini_commune_x_year.csv`
- `irrigation_commune_year.csv`
- `land_capability_class_to_csv.csv`

### Census data

Commune-level demographic and socioeconomic indicators were constructed from Chilean census microdata for 1982, 1992, 2002 and 2017.

The census processing workflow is documented in:

`code/build_variables_census.py`

The main variables constructed from census data are:

- population
- dependency rate
- mean years of schooling among the population aged 15 or older
- rural population share
- share of the economically active population in the primary sector
- share in the secondary sector
- share in the tertiary sector

The original census microdata are not redistributed in this repository.

### Territorial harmonization

Chile's communal boundaries changed between censuses.

The file:

`data/cut_82-92-02-17-26.csv`

contains a territorial crosswalk linking the commune identifiers used in the 1982, 1992 and 2002 census datasets to the current commune identifier.

The main identifiers are:

- `cut82`
- `cut92`
- `cut02`
- `cut2026`
- `muni_string`
- `region_id`
- `region_string`

When a current commune did not exist as an independent territorial unit in an earlier census, it was associated with the historical commune from which its territory originated.

### Irrigation subsidies

`irrigation_commune_year.csv` contains irrigation subsidies aggregated at the commune-year level.

The original administrative records were obtained through Chilean transparency mechanisms and contain information at the project level. For this reason, the original project-level dataset is not redistributed here.

The main variable is:

- `bonus_total_uf`: total irrigation subsidy received by a commune during a given year, expressed in UF.

### Poverty and inequality

`fgt0_gini_commune_x_year.csv` contains commune-level measures of poverty and inequality.

The main variables are:

- `fgt0`: poverty headcount ratio
- `gini`: Gini coefficient

Historical commune-level estimates were constructed using Small Area Estimation methods following Elbers, Lanjouw and Lanjouw (2003).

For 2017, commune-level poverty information was complemented with official data from the Chilean Ministry of Social Development and Family.

### Agricultural land capability

`land_capability_class_to_csv.csv` contains commune-level land capability information derived from CR2 data.

Land capability classes I, II, III and IV were considered agriculturally eligible land.

This eligible area is used in the instrumental-variable strategy.

## Panel construction

The final commune-year panel is built using:

`code/commune_x_year_panel_build.py`

The script combines:

- census indicators
- territorial codes
- irrigation subsidies
- poverty and inequality
- agricultural land characteristics

The panel covers 346 communes and the years 1982–2017.

### Population interpolation

Population is directly observed in census years.

The variable:

`pop_hat`

is created using linear interpolation between census years.

### Irrigation subsidy transformations

The following variables are constructed:

- `bonus_total_uf`: annual irrigation subsidy
- `UF_cum`: cumulative irrigation subsidy
- `UF_pop_cum`: cumulative irrigation subsidy per capita
- `ln_UF_pop_cum`: natural logarithm of cumulative irrigation subsidy per capita plus one

The transformations are:

`UF_pop_cum = UF_cum / pop_hat`

and

`ln_UF_pop_cum = ln(UF_pop_cum + 1)`

The addition of 1 allows observations with zero accumulated subsidies to remain in the sample.

## Rural sample

A rural subsample is defined using the rural population share observed in 1982.

A commune is classified as rural when:

`rural_share >= 20`

in 1982.

This classification is then kept fixed for all years.

## Econometric analysis

The instrumental-variable analysis is implemented in:

`code/analysis_IV.do`

The main outcomes are:

- poverty (`fgt0`)
- inequality (`gini`)

The main explanatory variable is:

`ln_UF_pop_cum`

The specifications include controls for:

- schooling
- dependency rate
- employment structure

The models also include:

- region × year fixed effects
- standard errors clustered at the commune level
- full-sample specifications
- rural-sample specifications

## References

Elbers, C., Lanjouw, J. O., & Lanjouw, P. (2003). Micro-Level Estimation of Poverty and Inequality. Econometrica, 71(1), 355–364.
