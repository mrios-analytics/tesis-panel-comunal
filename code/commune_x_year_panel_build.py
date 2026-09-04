import pandas as pd
import numpy as np
from pathlib import Path


# Carpetas del repositorio
repo_folder = Path(__file__).resolve().parent.parent
data_folder = repo_folder / "data"
output_folder = repo_folder / "output"

output_folder.mkdir(exist_ok=True)


# Archivos de entrada
cut_file = data_folder / "cut_82-92-02-17-26.csv"

census_files = {
    1982: data_folder / "census_1982_commune.csv",
    1992: data_folder / "census_1992_commune.csv",
    2002: data_folder / "census_2002_commune.csv",
    2017: data_folder / "census_2017_commune.csv"
}

irrigation_file = data_folder / "irrigation_commune_year.csv"
welfare_file = data_folder / "fgt0_gini_commune_x_year.csv"
land_file = data_folder / "land_capability_class_to_csv.csv"


# Archivos de salida
output_csv = output_folder / "thesis_commune_year_panel_1982_2017.csv"
output_dta = output_folder / "thesis_commune_year_panel_1982_2017.dta"


def standardize_current_code(df):

    if "cut2026" in df.columns:
        df = df.rename(columns={"cut2026": "cut_2026"})

    if "cod_BCN" in df.columns:
        df = df.rename(columns={"cod_BCN": "cut_2026"})

    return df


# Cargar crosswalk territorial

cut = pd.read_csv(cut_file)
cut = standardize_current_code(cut)

cut["cut_2026"] = pd.to_numeric(
    cut["cut_2026"],
    errors="raise"
).astype(int)

for variable in ["cut82", "cut92", "cut02"]:
    cut[variable] = pd.to_numeric(
        cut[variable],
        errors="raise"
    ).astype(int)


# Crear panel comuna x año

years = pd.DataFrame({
    "year": range(1982, 2018)
})

panel = cut.merge(
    years,
    how="cross"
)

panel = panel.sort_values(
    ["cut_2026", "year"]
).reset_index(drop=True)


# Incorporar Censo 1982

census_1982 = pd.read_csv(
    census_files[1982]
)

census_1982["cut82"] = pd.to_numeric(
    census_1982["cut82"],
    errors="raise"
).astype(int)

mapping_1982 = cut[
    ["cut_2026", "cut82"]
]

census_1982 = mapping_1982.merge(
    census_1982,
    on="cut82",
    how="left"
)

census_1982["year"] = 1982

census_1982 = census_1982.drop(
    columns=[
        column
        for column in [
            "cut82",
            "cut92",
            "cut02",
            "cut17",
            "cut2026",
            "cod_BCN",
            "muni_string"
        ]
        if column in census_1982.columns
    ]
)


# Incorporar Censo 1992

census_1992 = pd.read_csv(
    census_files[1992]
)

census_1992["cut92"] = pd.to_numeric(
    census_1992["cut92"],
    errors="raise"
).astype(int)

mapping_1992 = cut[
    ["cut_2026", "cut92"]
]

census_1992 = mapping_1992.merge(
    census_1992,
    on="cut92",
    how="left"
)

census_1992["year"] = 1992

census_1992 = census_1992.drop(
    columns=[
        column
        for column in [
            "cut82",
            "cut92",
            "cut02",
            "cut17",
            "cut2026",
            "cod_BCN",
            "muni_string"
        ]
        if column in census_1992.columns
    ]
)


# Incorporar Censo 2002

census_2002 = pd.read_csv(
    census_files[2002]
)

census_2002["cut02"] = pd.to_numeric(
    census_2002["cut02"],
    errors="raise"
).astype(int)

mapping_2002 = cut[
    ["cut_2026", "cut02"]
]

census_2002 = mapping_2002.merge(
    census_2002,
    on="cut02",
    how="left"
)

census_2002["year"] = 2002

census_2002 = census_2002.drop(
    columns=[
        column
        for column in [
            "cut82",
            "cut92",
            "cut02",
            "cut17",
            "cut2026",
            "cod_BCN",
            "muni_string"
        ]
        if column in census_2002.columns
    ]
)


# Incorporar Censo 2017
# cut17 es equivalente a cut_2026

census_2017 = pd.read_csv(
    census_files[2017]
)

census_2017["cut17"] = pd.to_numeric(
    census_2017["cut17"],
    errors="raise"
).astype(int)

census_2017 = census_2017.rename(
    columns={"cut17": "cut_2026"}
)

census_2017["year"] = 2017

census_2017 = census_2017.drop(
    columns=[
        column
        for column in [
            "cut82",
            "cut92",
            "cut02",
            "cut2026",
            "cod_BCN",
            "muni_string"
        ]
        if column in census_2017.columns
    ]
)


# Unir los cuatro censos

census_long = pd.concat(
    [
        census_1982,
        census_1992,
        census_2002,
        census_2017
    ],
    ignore_index=True
)

panel = panel.merge(
    census_long,
    on=["cut_2026", "year"],
    how="left"
)


# Interpolación lineal de población

panel = panel.sort_values(
    ["cut_2026", "year"]
)

panel["pop_hat"] = (
    panel
    .groupby("cut_2026")["population"]
    .transform(
        lambda x: x.interpolate(
            method="linear"
        )
    )
)


# Incorporar subsidios de riego

irrigation = pd.read_csv(
    irrigation_file
)

irrigation = standardize_current_code(
    irrigation
)

irrigation["cut_2026"] = pd.to_numeric(
    irrigation["cut_2026"],
    errors="raise"
).astype(int)

irrigation["year"] = pd.to_numeric(
    irrigation["year"],
    errors="raise"
).astype(int)

irrigation = (
    irrigation
    .groupby(
        ["cut_2026", "year"],
        as_index=False
    )
    .agg(
        bonus_total_uf=(
            "bonus_total_uf",
            "sum"
        )
    )
)

panel = panel.merge(
    irrigation,
    on=["cut_2026", "year"],
    how="left"
)

panel["bonus_total_uf"] = (
    panel["bonus_total_uf"]
    .fillna(0)
)

# Los subsidios comienzan en 1987
panel.loc[
    panel["year"] < 1987,
    "bonus_total_uf"
] = 0


# Subsidio acumulado

panel = panel.sort_values(
    ["cut_2026", "year"]
)

panel["UF_cum"] = (
    panel
    .groupby("cut_2026")["bonus_total_uf"]
    .cumsum()
)


# Subsidio acumulado per cápita

panel["UF_pop_cum"] = (
    panel["UF_cum"]
    / panel["pop_hat"]
)


# Logaritmo natural del subsidio acumulado per cápita

panel["ln_UF_pop_cum"] = np.log1p(
    panel["UF_pop_cum"]
)


# Incorporar pobreza y desigualdad

welfare = pd.read_csv(
    welfare_file
)

welfare = standardize_current_code(
    welfare
)

welfare["cut_2026"] = pd.to_numeric(
    welfare["cut_2026"],
    errors="raise"
).astype(int)

welfare["year"] = pd.to_numeric(
    welfare["year"],
    errors="raise"
).astype(int)

welfare = welfare[
    [
        "cut_2026",
        "year",
        "fgt0",
        "gini"
    ]
]

panel = panel.merge(
    welfare,
    on=["cut_2026", "year"],
    how="left"
)


# Incorporar capacidad de uso de suelo

land = pd.read_csv(
    land_file
)

land = standardize_current_code(
    land
)

land["cut_2026"] = pd.to_numeric(
    land["cut_2026"],
    errors="raise"
).astype(int)

land_variables = [
    variable
    for variable in land.columns
    if variable == "cut_2026"
    or variable not in panel.columns
]

panel = panel.merge(
    land[land_variables],
    on="cut_2026",
    how="left"
)


# Ordenar base final

panel = panel.sort_values(
    ["cut_2026", "year"]
).reset_index(drop=True)

panel["year"] = panel["year"].astype(int)


# Guardar archivos

panel.to_csv(
    output_csv,
    index=False
)

panel.to_stata(
    output_dta,
    write_index=False,
    version=118
)


print("Proceso terminado")
print("Filas:", len(panel))
print(
    "Comunas:",
    panel["cut_2026"].nunique()
)
print(
    "Años:",
    panel["year"].min(),
    "-",
    panel["year"].max()
)
print(
    "Observaciones esperadas:",
    346 * 36
)
print("CSV:", output_csv)
print("DTA:", output_dta)
