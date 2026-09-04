import pandas as pd
from pathlib import Path


# Carpetas del proyecto

repo_folder = Path(__file__).resolve().parent.parent

raw_data_folder = repo_folder / "raw_data"
output_folder = repo_folder / "data"


# Archivos originales

person_1982_file = (
    raw_data_folder
    / "census_1982"
    / "censo_1982_persona.dta"
)

housing_1982_file = (
    raw_data_folder
    / "census_1982"
    / "censo_1982_vivienda.dta"
)

person_1992_file = (
    raw_data_folder
    / "census_1992"
    / "persona.dta"
)

portfolio_1992_file = (
    raw_data_folder
    / "census_1992"
    / "portafolios.dta"
)

activity_1992_file = (
    raw_data_folder
    / "census_1992"
    / "rama_actividad.dta"
)

person_2002_file = (
    raw_data_folder
    / "census_2002"
    / "persona.dta"
)

portfolio_2002_file = (
    raw_data_folder
    / "census_2002"
    / "portafolios.dta"
)

activity_2002_file = (
    raw_data_folder
    / "census_2002"
    / "glosa_p32.dta"
)

person_2017_file = (
    raw_data_folder
    / "census_2017"
    / "Microdato_Censo2017-Personas.csv"
)


def build_1982():

    person = pd.read_stata(
        person_1982_file,
        convert_categoricals=False
    )

    housing = pd.read_stata(
        housing_1982_file,
        convert_categoricals=False
    )

    person = person.rename(
        columns={"comuna": "cut82"}
    )

    housing = housing.rename(
        columns={"comuna": "cut82"}
    )

    # Tasa de dependencia

    person["dependent"] = (
        (person["edad"] <= 14)
        | (person["edad"] >= 65)
    ).astype(int)

    person["working_age"] = (
        person["edad"]
        .between(15, 64)
        .astype(int)
    )

    # Escolaridad

    person["schooling_ind"] = float("nan")

    person.loc[
        (person["edad"] >= 15)
        & (
            person["tipo_educacion"].isna()
            | (person["tipo_educacion"] == 0)
            | (person["curso"] == 0)
        ),
        "schooling_ind"
    ] = 0

    mask = (
        (person["edad"] >= 15)
        & (person["tipo_educacion"] == 1)
        & (person["curso"] > 0)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = person.loc[
        mask,
        "curso"
    ].clip(upper=8)

    mask = (
        (person["edad"] >= 15)
        & person["tipo_educacion"].between(2, 8)
        & (person["curso"] > 0)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        8
        + person.loc[
            mask,
            "curso"
        ].clip(upper=4)
    )

    mask = (
        (person["edad"] >= 15)
        & (person["tipo_educacion"] == 9)
        & (person["curso"] > 0)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        12
        + person.loc[
            mask,
            "curso"
        ].clip(upper=6)
    )

    # Población económicamente activa

    person["pea"] = (
        person["situacion_empleo"]
        .between(1, 5)
        .astype(int)
    )

    # Sectores económicos

    person["primary"] = (
        (person["pea"] == 1)
        & person["rama_actividad"].between(1000, 2999)
    ).astype(int)

    person["secondary"] = (
        (person["pea"] == 1)
        & person["rama_actividad"].between(3000, 5999)
    ).astype(int)

    person["tertiary"] = (
        (person["pea"] == 1)
        & person["rama_actividad"].between(6000, 9999)
    ).astype(int)

    # Agregación comunal

    commune = person.groupby(
        "cut82",
        as_index=False
    ).agg(
        population=("cut82", "size"),
        dependent=("dependent", "sum"),
        working_age=("working_age", "sum"),
        schooling=("schooling_ind", "mean"),
        pea=("pea", "sum"),
        primary=("primary", "sum"),
        secondary=("secondary", "sum"),
        tertiary=("tertiary", "sum")
    )

    commune["dependency_rate"] = (
        commune["dependent"]
        / commune["working_age"]
        * 100
    )

    commune["sh_first_pea"] = (
        commune["primary"]
        / commune["pea"]
        * 100
    )

    commune["sh_second_pea"] = (
        commune["secondary"]
        / commune["pea"]
        * 100
    )

    commune["sh_third_pea"] = (
        commune["tertiary"]
        / commune["pea"]
        * 100
    )

    # Ruralidad

    housing["rural"] = (
        housing["area"] == 2
    ).astype(int)

    rurality = housing.groupby(
        "cut82",
        as_index=False
    ).agg(
        rural_share=("rural", "mean")
    )

    rurality["rural_share"] *= 100

    commune = commune.merge(
        rurality,
        on="cut82",
        how="left"
    )

    commune["year"] = 1982

    commune = commune[
        [
            "cut82",
            "year",
            "population",
            "dependency_rate",
            "schooling",
            "rural_share",
            "sh_first_pea",
            "sh_second_pea",
            "sh_third_pea"
        ]
    ]

    output_file = (
        output_folder
        / "census_1982_commune.csv"
    )

    commune.to_csv(
        output_file,
        index=False
    )

    print(
        "1982:",
        len(commune),
        "communes"
    )


def build_1992():

    person = pd.read_stata(
        person_1992_file,
        columns=[
            "PORTAFOL",
            "EDAD",
            "TIPO_EDU",
            "CURSO",
            "SITUACIO",
            "RAMA_ACT"
        ],
        convert_categoricals=False
    )

    portfolio = pd.read_stata(
        portfolio_1992_file,
        columns=[
            "PORTAFOL",
            "COMUNA",
            "AREA"
        ],
        convert_categoricals=False
    )

    activity = pd.read_stata(
        activity_1992_file,
        columns=[
            "RAMA_ACT",
            "SECTOR"
        ],
        convert_categoricals=False
    )

    person = person.merge(
        portfolio,
        on="PORTAFOL",
        how="left"
    )

    person = person.merge(
        activity,
        on="RAMA_ACT",
        how="left"
    )

    person = person.rename(
        columns={"COMUNA": "cut92"}
    )

    # Tasa de dependencia

    person["dependent"] = (
        (person["EDAD"] <= 14)
        | (person["EDAD"] >= 65)
    ).astype(int)

    person["working_age"] = (
        person["EDAD"]
        .between(15, 64)
        .astype(int)
    )

    # Escolaridad

    person["schooling_ind"] = float("nan")

    person.loc[
        (person["EDAD"] >= 15)
        & (
            person["TIPO_EDU"].isin([0, 1])
            | (person["CURSO"] == 0)
        ),
        "schooling_ind"
    ] = 0

    mask = (
        (person["EDAD"] >= 15)
        & (person["TIPO_EDU"] == 2)
        & (person["CURSO"] > 0)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = person.loc[
        mask,
        "CURSO"
    ]

    mask = (
        (person["EDAD"] >= 15)
        & person["TIPO_EDU"].between(3, 11)
        & (person["CURSO"] > 0)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        8
        + person.loc[
            mask,
            "CURSO"
        ].clip(upper=4)
    )

    mask = (
        (person["EDAD"] >= 15)
        & (person["TIPO_EDU"] == 12)
        & (person["CURSO"] > 0)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        12
        + person.loc[
            mask,
            "CURSO"
        ].clip(upper=3)
    )

    mask = (
        (person["EDAD"] >= 15)
        & (person["TIPO_EDU"] == 13)
        & (person["CURSO"] > 0)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        12
        + person.loc[
            mask,
            "CURSO"
        ].clip(upper=4)
    )

    mask = (
        (person["EDAD"] >= 15)
        & (person["TIPO_EDU"] == 14)
        & (person["CURSO"] > 0)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        12
        + person.loc[
            mask,
            "CURSO"
        ].clip(upper=6)
    )

    # Ruralidad

    person["rural"] = (
        person["AREA"] == 2
    ).astype(int)

    # Población económicamente activa

    person["pea"] = (
        person["SITUACIO"]
        .between(1, 5)
        .astype(int)
    )

    # Sectores económicos

    person["primary"] = (
        (person["pea"] == 1)
        & (person["SECTOR"] == "P")
    ).astype(int)

    person["secondary"] = (
        (person["pea"] == 1)
        & (person["SECTOR"] == "S")
    ).astype(int)

    person["tertiary"] = (
        (person["pea"] == 1)
        & (person["SECTOR"] == "T")
    ).astype(int)

    # Agregación comunal

    commune = person.groupby(
        "cut92",
        as_index=False
    ).agg(
        population=("cut92", "size"),
        dependent=("dependent", "sum"),
        working_age=("working_age", "sum"),
        schooling=("schooling_ind", "mean"),
        rural_share=("rural", "mean"),
        pea=("pea", "sum"),
        primary=("primary", "sum"),
        secondary=("secondary", "sum"),
        tertiary=("tertiary", "sum")
    )

    commune["dependency_rate"] = (
        commune["dependent"]
        / commune["working_age"]
        * 100
    )

    commune["rural_share"] *= 100

    commune["sh_first_pea"] = (
        commune["primary"]
        / commune["pea"]
        * 100
    )

    commune["sh_second_pea"] = (
        commune["secondary"]
        / commune["pea"]
        * 100
    )

    commune["sh_third_pea"] = (
        commune["tertiary"]
        / commune["pea"]
        * 100
    )

    commune["year"] = 1992

    commune = commune[
        [
            "cut92",
            "year",
            "population",
            "dependency_rate",
            "schooling",
            "rural_share",
            "sh_first_pea",
            "sh_second_pea",
            "sh_third_pea"
        ]
    ]

    output_file = (
        output_folder
        / "census_1992_commune.csv"
    )

    commune.to_csv(
        output_file,
        index=False
    )

    print(
        "1992:",
        len(commune),
        "communes"
    )


def build_2002():

    person = pd.read_stata(
        person_2002_file,
        columns=[
            "PORTAFOL",
            "P19",
            "P26A",
            "P26B",
            "P29",
            "P32"
        ],
        convert_categoricals=False
    )

    portfolio = pd.read_stata(
        portfolio_2002_file,
        columns=[
            "PORTAFOL",
            "COMUNA",
            "AREA"
        ],
        convert_categoricals=False
    )

    activity = pd.read_stata(
        activity_2002_file,
        columns=[
            "GRUPO",
            "SECTOR"
        ],
        convert_categoricals=False
    )

    person = person.merge(
        portfolio,
        on="PORTAFOL",
        how="left"
    )

    person = person.merge(
        activity,
        left_on="P32",
        right_on="GRUPO",
        how="left"
    )

    person = person.rename(
        columns={"COMUNA": "cut02"}
    )

    # Tasa de dependencia

    person["dependent"] = (
        (person["P19"] <= 14)
        | (person["P19"] >= 65)
    ).astype(int)

    person["working_age"] = (
        person["P19"]
        .between(15, 64)
        .astype(int)
    )

    # Escolaridad

    person["schooling_ind"] = float("nan")

    person.loc[
        (person["P19"] >= 15)
        & person["P26A"].isin([1, 2]),
        "schooling_ind"
    ] = 0

    mask = (
        (person["P19"] >= 15)
        & (person["P26A"] == 4)
        & person["P26B"].between(1, 8)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = person.loc[
        mask,
        "P26B"
    ]

    mask = (
        (person["P19"] >= 15)
        & person["P26A"].between(5, 12)
        & person["P26B"].between(1, 8)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        8
        + person.loc[
            mask,
            "P26B"
        ].clip(upper=4)
    )

    mask = (
        (person["P19"] >= 15)
        & (person["P26A"] == 13)
        & person["P26B"].between(1, 8)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        12
        + person.loc[
            mask,
            "P26B"
        ].clip(upper=3)
    )

    mask = (
        (person["P19"] >= 15)
        & (person["P26A"] == 14)
        & person["P26B"].between(1, 8)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        12
        + person.loc[
            mask,
            "P26B"
        ].clip(upper=4)
    )

    mask = (
        (person["P19"] >= 15)
        & (person["P26A"] == 15)
        & person["P26B"].between(1, 8)
    )

    person.loc[
        mask,
        "schooling_ind"
    ] = (
        12
        + person.loc[
            mask,
            "P26B"
        ].clip(upper=6)
    )

    # Ruralidad

    person["rural"] = (
        person["AREA"] == 2
    ).astype(int)

    # Población económicamente activa

    person["pea"] = (
        person["P29"]
        .between(1, 5)
        .astype(int)
    )

    # Sectores económicos

    person["primary"] = (
        (person["pea"] == 1)
        & (person["SECTOR"] == "P")
    ).astype(int)

    person["secondary"] = (
        (person["pea"] == 1)
        & (person["SECTOR"] == "S")
    ).astype(int)

    person["tertiary"] = (
        (person["pea"] == 1)
        & (person["SECTOR"] == "T")
    ).astype(int)

    # Agregación comunal

    commune = person.groupby(
        "cut02",
        as_index=False
    ).agg(
        population=("cut02", "size"),
        dependent=("dependent", "sum"),
        working_age=("working_age", "sum"),
        schooling=("schooling_ind", "mean"),
        rural_share=("rural", "mean"),
        pea=("pea", "sum"),
        primary=("primary", "sum"),
        secondary=("secondary", "sum"),
        tertiary=("tertiary", "sum")
    )

    commune["dependency_rate"] = (
        commune["dependent"]
        / commune["working_age"]
        * 100
    )

    commune["rural_share"] *= 100

    commune["sh_first_pea"] = (
        commune["primary"]
        / commune["pea"]
        * 100
    )

    commune["sh_second_pea"] = (
        commune["secondary"]
        / commune["pea"]
        * 100
    )

    commune["sh_third_pea"] = (
        commune["tertiary"]
        / commune["pea"]
        * 100
    )

    commune["year"] = 2002

    commune = commune[
        [
            "cut02",
            "year",
            "population",
            "dependency_rate",
            "schooling",
            "rural_share",
            "sh_first_pea",
            "sh_second_pea",
            "sh_third_pea"
        ]
    ]

    output_file = (
        output_folder
        / "census_2002_commune.csv"
    )

    commune.to_csv(
        output_file,
        index=False
    )

    print(
        "2002:",
        len(commune),
        "communes"
    )


def build_2017():

    variables = [
        "COMUNA",
        "AREA",
        "P09",
        "ESCOLARIDAD",
        "P17",
        "P18"
    ]

    commune_parts = []

    for person in pd.read_csv(
        person_2017_file,
        sep=";",
        encoding="utf-8-sig",
        usecols=variables,
        chunksize=500000
    ):

        person = person.rename(
            columns={"COMUNA": "cut17"}
        )

        # Tasa de dependencia

        person["dependent"] = (
            (person["P09"] <= 14)
            | (person["P09"] >= 65)
        ).astype(int)

        person["working_age"] = (
            person["P09"]
            .between(15, 64)
            .astype(int)
        )

        # Escolaridad

        person["schooling_15plus"] = (
            person["ESCOLARIDAD"]
            .where(person["P09"] >= 15)
        )

        # Ruralidad

        person["rural"] = (
            person["AREA"] == 2
        ).astype(int)

        # Población económicamente activa

        person["pea"] = (
            person["P17"]
            .isin([1, 2, 3, 4])
            .astype(int)
        )

        # Sectores económicos

        activity = (
            person["P18"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        person["primary"] = (
            (person["pea"] == 1)
            & activity.isin(["A", "B"])
        ).astype(int)

        person["secondary"] = (
            (person["pea"] == 1)
            & activity.isin(
                ["C", "D", "E", "F"]
            )
        ).astype(int)

        person["tertiary"] = (
            (person["pea"] == 1)
            & activity.isin(
                [
                    "G", "H", "I", "J", "K",
                    "L", "M", "N", "O", "P",
                    "Q", "R", "S", "T", "U"
                ]
            )
        ).astype(int)

        part = person.groupby(
            "cut17",
            as_index=False
        ).agg(
            population=("cut17", "size"),
            dependent=("dependent", "sum"),
            working_age=("working_age", "sum"),
            schooling_sum=("schooling_15plus", "sum"),
            schooling_n=("schooling_15plus", "count"),
            rural=("rural", "sum"),
            pea=("pea", "sum"),
            primary=("primary", "sum"),
            secondary=("secondary", "sum"),
            tertiary=("tertiary", "sum")
        )

        commune_parts.append(part)

    commune = pd.concat(
        commune_parts,
        ignore_index=True
    )

    commune = commune.groupby(
        "cut17",
        as_index=False
    ).sum()

    commune["dependency_rate"] = (
        commune["dependent"]
        / commune["working_age"]
        * 100
    )

    commune["schooling"] = (
        commune["schooling_sum"]
        / commune["schooling_n"]
    )

    commune["rural_share"] = (
        commune["rural"]
        / commune["population"]
        * 100
    )

    commune["sh_first_pea"] = (
        commune["primary"]
        / commune["pea"]
        * 100
    )

    commune["sh_second_pea"] = (
        commune["secondary"]
        / commune["pea"]
        * 100
    )

    commune["sh_third_pea"] = (
        commune["tertiary"]
        / commune["pea"]
        * 100
    )

    commune["year"] = 2017

    commune = commune[
        [
            "cut17",
            "year",
            "population",
            "dependency_rate",
            "schooling",
            "rural_share",
            "sh_first_pea",
            "sh_second_pea",
            "sh_third_pea"
        ]
    ]

    output_file = (
        output_folder
        / "census_2017_commune.csv"
    )

    commune.to_csv(
        output_file,
        index=False
    )

    print(
        "2017:",
        len(commune),
        "communes"
    )


print("Building 1982 census dataset...")
build_1982()

print("Building 1992 census dataset...")
build_1992()

print("Building 2002 census dataset...")
build_2002()

print("Building 2017 census dataset...")
build_2017()

print("Process finished.")
