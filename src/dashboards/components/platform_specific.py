import pandas as pd
from dash import html, dcc
import plotly.express as px


def build_platform_specific_layout(plataformas: list[str]) -> html.Div:
    """Sección por plataforma: selector y gráfico de top autores por URLs subidas."""
    return html.Div(
        [
            html.H3("Por plataforma"),
            html.Div(
                [
                    html.Label("Plataforma"),
                    dcc.Dropdown(
                        id="platform-select",
                        options=[{"label": p, "value": p} for p in sorted(plataformas)],
                        value=None,
                        placeholder="Selecciona una plataforma",
                        clearable=True,
                        searchable=True,
                    ),
                ],
                className="filter-bar",
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