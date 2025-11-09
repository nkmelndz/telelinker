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
                                clearable=False,
                                searchable=False,
                                className="platform-dropdown",
                                style={"width": "100%"},
                            ),
                        ],
                        style={"flex": "0 0 30%"},
                    ),
                    html.Div(
                        [
                            html.Label("Filtro por fechas"),
                            build_date_filter(min_date, max_date, filter_id="platform-date-range"),
                        ],
                        style={"flex": "1 0 70%"},
                    ),
                ],
                className="filter-bar",
                style={"display": "flex", "gap": "12px", "alignItems": "flex-end", "flexWrap": "nowrap"},
            ),
            html.Div(className="card", children=[dcc.Graph(id="top-authors-by-platform")]),
            html.Div(
                [
                    html.Div(className="card", children=[dcc.Graph(id="top-authors-likes-by-platform")], style={"flex": "1"}),
                    html.Div(className="card", children=[dcc.Graph(id="top-authors-comments-by-platform")], style={"flex": "1"}),
                ],
                className="row",
                style={"display": "flex", "gap": "12px", "flexWrap": "wrap"},
            ),
            html.Div(className="card", children=[dcc.Graph(id="engagement-trend-by-platform")]),
            html.Div(className="card", children=[dcc.Graph(id="top-posts-engagement-by-platform")]),
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


def top_authors_likes_figure(df: pd.DataFrame, plataforma: str | None):
    """Barra horizontal: autores ordenados por suma de likes en la plataforma.
    Muestra Top autores por likes (suma) para la plataforma seleccionada.
    """
    if plataforma is None:
        return px.bar(title="Seleccione una plataforma para ver top autores por likes")
    if df.empty or "plataforma" not in df.columns or "autor_contenido" not in df.columns or "likes" not in df.columns:
        return px.bar(title="Sin datos suficientes para graficar top autores por likes")

    dff = df.copy()
    dff["plataforma"] = dff["plataforma"].astype(str).fillna("Desconocido")
    dff["autor_contenido"] = dff["autor_contenido"].astype(str).fillna("Desconocido")
    dff["likes"] = pd.to_numeric(dff["likes"], errors="coerce").fillna(0)

    dff = dff[dff["plataforma"] == plataforma]
    if dff.empty:
        return px.bar(title=f"Sin datos para la plataforma '{plataforma}'")

    agg = (
        dff.groupby(["autor_contenido"], dropna=False)["likes"]
        .sum()
        .reset_index(name="likes_sum")
    )
    # Seleccionar los 10 autores con mayor suma de likes, luego ordenar ascendente para visualización
    agg = agg.sort_values("likes_sum", ascending=False).head(10)
    agg = agg.sort_values("likes_sum", ascending=True)

    fig = px.bar(
        agg,
        x="likes_sum",
        y="autor_contenido",
        orientation="h",
        title=f"Top autores por likes en {plataforma}",
        text="likes_sum",
        color="autor_contenido",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Autor",
        yaxis={"categoryorder": "array", "categoryarray": agg["autor_contenido"].tolist()},
        showlegend=False,
    )
    return fig


def top_authors_comments_figure(df: pd.DataFrame, plataforma: str | None):
    """Barra horizontal: autores ordenados por suma de comentarios en la plataforma.
    Limita a Top 15 para legibilidad.
    """
    if plataforma is None:
        return px.bar(title="Seleccione una plataforma para ver top autores por comentarios")
    if df.empty or "plataforma" not in df.columns or "autor_contenido" not in df.columns or "comentarios" not in df.columns:
        return px.bar(title="Sin datos suficientes para graficar top autores por comentarios")

    dff = df.copy()
    dff["plataforma"] = dff["plataforma"].astype(str).fillna("Desconocido")
    dff["autor_contenido"] = dff["autor_contenido"].astype(str).fillna("Desconocido")
    dff["comentarios"] = pd.to_numeric(dff["comentarios"], errors="coerce").fillna(0)

    dff = dff[dff["plataforma"] == plataforma]
    if dff.empty:
        return px.bar(title=f"Sin datos para la plataforma '{plataforma}'")

    agg = (
        dff.groupby(["autor_contenido"], dropna=False)["comentarios"]
        .sum()
        .reset_index(name="comentarios_sum")
    )
    # Seleccionar los 10 autores con mayor suma de comentarios, luego ordenar ascendente para visualización
    agg = agg.sort_values("comentarios_sum", ascending=False).head(10)
    agg = agg.sort_values("comentarios_sum", ascending=True)

    fig = px.bar(
        agg,
        x="comentarios_sum",
        y="autor_contenido",
        orientation="h",
        title=f"Top autores por comentarios en {plataforma}",
        text="comentarios_sum",
        color="autor_contenido",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Autor",
        yaxis={"categoryorder": "array", "categoryarray": agg["autor_contenido"].tolist()},
        showlegend=False,
    )
    return fig


def engagement_trend_figure(df: pd.DataFrame, plataforma: str | None, period: str | None = "semanal"):
    """Tendencia temporal de engagement: líneas separadas de likes y comentarios sumados por día.
    Filtra por plataforma seleccionada y usa la columna 'fecha' para agrupar por día.
    """
    if plataforma is None:
        return px.line(title="Seleccione una plataforma para ver la tendencia de engagement")
    if df.empty or "plataforma" not in df.columns or "fecha" not in df.columns:
        return px.line(title="Sin datos suficientes para graficar tendencia de engagement")

    dff = df.copy()
    dff["plataforma"] = dff["plataforma"].astype(str).fillna("Desconocido")
    dff = dff[dff["plataforma"] == plataforma]

    dff["fecha"] = pd.to_datetime(dff["fecha"], errors="coerce")
    dff = dff[dff["fecha"].notna()]
    if dff.empty:
        return px.line(title=f"Sin fechas válidas para graficar en '{plataforma}'")

    dff["likes"] = pd.to_numeric(dff.get("likes", 0), errors="coerce").fillna(0)
    dff["comentarios"] = pd.to_numeric(dff.get("comentarios", 0), errors="coerce").fillna(0)
    dff["compartidos"] = pd.to_numeric(dff.get("compartidos", 0), errors="coerce").fillna(0)
    dff["visitas"] = pd.to_numeric(dff.get("visitas", 0), errors="coerce").fillna(0)

    # Selección de agregación
    period = (period or "diaria").lower()
    if period == "semanal":
        key = "semana"
        dff[key] = dff["fecha"].dt.to_period("W").apply(lambda p: p.start_time.date())
    elif period == "mensual":
        key = "mes"
        dff[key] = dff["fecha"].dt.to_period("M").apply(lambda p: p.start_time.date())
    else:
        key = "dia"
        dff[key] = dff["fecha"].dt.date

    agg = (
        dff.groupby(key, dropna=False)[["likes", "comentarios", "compartidos", "visitas"]]
        .sum()
        .reset_index()
    )
    # Formato largo para dos líneas
    long_df = agg.melt(id_vars=[key], value_vars=["likes", "comentarios", "compartidos", "visitas"], var_name="métrica", value_name="valor")

    fig = px.line(
        long_df,
        x=key,
        y="valor",
        color="métrica",
        markers=True,
        title=f"Tendencia temporal de engagement en {plataforma} ({period})",
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), legend_title_text="Métrica")
    return fig


def top_posts_engagement_figure(df: pd.DataFrame, plataforma: str | None):
    """Top publicaciones por engagement total (likes + comentarios + compartidos + visitas).
    Muestra las 10 publicaciones con mayor engagement en barras horizontales.
    """
    if plataforma is None:
        return px.bar(title="Seleccione una plataforma para ver top publicaciones por engagement")
    if df.empty or "plataforma" not in df.columns or "url" not in df.columns:
        return px.bar(title="Sin datos suficientes para graficar top publicaciones por engagement")

    dff = df.copy()
    dff["plataforma"] = dff["plataforma"].astype(str).fillna("Desconocido")
    dff = dff[dff["plataforma"] == plataforma]
    if dff.empty:
        return px.bar(title=f"Sin datos para la plataforma '{plataforma}'")

    # Métricas robustas: convierte a numérico y rellena nulos
    for col in ["likes", "comentarios", "compartidos", "visitas"]:
        dff[col] = pd.to_numeric(dff.get(col, 0), errors="coerce").fillna(0)
    dff["autor_contenido"] = dff.get("autor_contenido", "Desconocido").astype(str).fillna("Desconocido")

    dff["engagement_total"] = dff["likes"] + dff["comentarios"] + dff["compartidos"] + dff["visitas"]

    agg = (
        dff.groupby(["url", "autor_contenido"], dropna=False)["engagement_total"]
        .sum()
        .reset_index()
    )
    # Top 10 por engagement total, luego orden ascendente para lectura
    agg = agg.sort_values("engagement_total", ascending=False).head(10)
    agg = agg.sort_values("engagement_total", ascending=True)

    fig = px.bar(
        agg,
        x="engagement_total",
        y="url",
        orientation="h",
        title=f"Top publicaciones por engagement total en {plataforma}",
        text="engagement_total",
        color="autor_contenido",
        # Usamos custom_data para controlar el contenido del tooltip explícitamente
        custom_data=["url", "autor_contenido"],
    )
    fig.update_traces(textposition="outside")
    # Tooltip explícito para evitar que Plotly muestre el ticktext (autor) en el campo y/URL
    fig.update_traces(
        hovertemplate="Autor: %{customdata[1]}<br>URL: %{customdata[0]}<br>Engagement: %{x}<extra></extra>"
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        yaxis_title="Autor",
        yaxis={
            "categoryorder": "array",
            "categoryarray": agg["url"].tolist(),
            "tickmode": "array",
            "tickvals": agg["url"].tolist(),
            "ticktext": agg["autor_contenido"].tolist(),
        },
        showlegend=False,
    )
    return fig