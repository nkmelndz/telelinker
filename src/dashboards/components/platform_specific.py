import pandas as pd
from dash import html, dcc
import plotly.express as px
from datetime import date
from .filters import build_date_filter


def build_platform_specific_layout(plataformas: list[str], min_date: date | None, max_date: date | None) -> html.Div:
    """Sección por plataforma: selector, filtro de fecha y gráfico de top autores por URLs subidas."""
    sorted_plats = sorted(plataformas)
    default_value = sorted_plats[0] if sorted_plats else None
    return html.Div(
        [
            html.H3("Por plataforma"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Plataforma"),
                            dcc.Dropdown(
                                id="platform-select",
                                options=[{"label": p, "value": p} for p in sorted_plats],
                                value=default_value,
                                placeholder="Selecciona una plataforma",
                                clearable=True,
                                searchable=True,
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("Filtro por fechas"),
                            build_date_filter(min_date, max_date, filter_id="platform-date-range"),
                        ]
                    ),
                ],
                className="filter-bar",
                style={"display": "flex", "gap": "12px", "alignItems": "flex-end", "flexWrap": "wrap"},
            ),
            html.Div(className="card", children=[dcc.Graph(id="top-authors-by-platform")]),
        ],
        className="section",
    )


def top_authors_figure(df: pd.DataFrame, plataforma: str | None):
    """Devuelve un treemap jerárquico plataforma → autor, tamaño por cantidad de URLs.
    Si no hay plataforma seleccionada o no hay datos, devuelve un gráfico vacío con mensaje.
    """
    if plataforma is None:
        return px.bar(title="Seleccione una plataforma para ver top autores")
    if df.empty or "plataforma" not in df.columns or "autor_contenido" not in df.columns or "url" not in df.columns:
        return px.bar(title="Sin datos suficientes para graficar top autores")

    dff = df.copy()
    dff["plataforma"] = dff["plataforma"].astype(str).fillna("Desconocido")
    dff["autor_contenido"] = dff["autor_contenido"].astype(str).fillna("Desconocido")

    dff = dff[dff["plataforma"] == plataforma]
    if dff.empty:
        return px.bar(title=f"Sin datos para la plataforma '{plataforma}'")

    agg = (
        dff.groupby(["plataforma", "autor_contenido"], dropna=False)["url"]
        .count()
        .reset_index(name="conteo_urls")
    )

    # Treemap jerárquico: plataforma → autor
    fig = px.treemap(
        agg,
        path=["plataforma", "autor_contenido"],
        values="conteo_urls",
        title=f"URLs por autor en {plataforma} (Treemap)",
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig