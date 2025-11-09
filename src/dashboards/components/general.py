import pandas as pd
from dash import html, dcc
import plotly.express as px
from datetime import date
from .filters import build_date_filter


def build_general_layout(min_date: date | None = None, max_date: date | None = None) -> html.Div:
    """Contenedor de gráficos generales: título, filtro de fechas y cuatro gráficos.
    El DatePickerRange se construye internamente (id='date-range') como en la sección por plataforma.
    """
    return html.Div(
        [
            html.H3("Gráficos generales"),
            html.Div(
                [
                    html.Label("Filtro por fechas"),
                    build_date_filter(min_date, max_date),
                ],
                className="filter-bar",
            ),
            html.Div(
                [
                    html.Div(className="card", children=[dcc.Graph(id="url-count-by-platform", style={"height": "360px"})]),
                    html.Div(className="card", children=[dcc.Graph(id="likes-sum-by-platform", style={"height": "360px"})]),
                    html.Div(className="card", children=[dcc.Graph(id="comments-sum-by-platform", style={"height": "360px"})]),
                ],
                className="cards",
            ),
            # Gráfico de tendencia temporal a ancho completo, debajo de los tres gráficos
            html.Div(className="card", children=[dcc.Graph(id="time-trend-by-platform")]),
        ],
        className="section",
    )


def likes_sum_figure(df: pd.DataFrame):
    if df.empty or "plataforma" not in df.columns or "likes" not in df.columns:
        return px.pie(title="Sin datos de 'likes' para graficar")
    agg = (
        df.assign(likes=pd.to_numeric(df["likes"], errors="coerce").fillna(0))
        .groupby("plataforma", dropna=False)["likes"].sum().reset_index()
    )
    # Asegurar que la etiqueta sea la columna 'plataforma'
    agg["plataforma"] = agg["plataforma"].astype(str)
    fig = px.pie(
        agg,
        names="plataforma",
        values="likes",
        title="Suma de likes por plataforma (Pie)",
    )
    fig.update_traces(textinfo="label+value+percent")
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), legend_title_text="")
    return fig


def comments_sum_figure(df: pd.DataFrame):
    if df.empty or "plataforma" not in df.columns or "comentarios" not in df.columns:
        return px.pie(title="Sin datos de 'comentarios' para graficar")
    agg = (
        df.assign(comentarios=pd.to_numeric(df["comentarios"], errors="coerce").fillna(0))
        .groupby("plataforma", dropna=False)["comentarios"].sum().reset_index()
    )
    agg["plataforma"] = agg["plataforma"].astype(str)
    fig = px.pie(
        agg,
        names="plataforma",
        values="comentarios",
        title="Suma de comentarios por plataforma (Donut)",
        hole=0.45,
    )
    fig.update_traces(textinfo="label+value+percent")
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), legend_title_text="")
    return fig


def url_count_figure(df: pd.DataFrame):
    if df.empty or "plataforma" not in df.columns or "url" not in df.columns:
        return px.bar(title="Sin datos de 'url' para graficar")
    agg = df.groupby("plataforma", dropna=False)["url"].count().reset_index(name="conteo")
    agg["plataforma"] = agg["plataforma"].astype(str)
    plataformas = agg["plataforma"].unique().tolist()
    color_map = _get_platform_color_map(plataformas)
    fig = px.bar(
        agg,
        x="plataforma",
        y="conteo",
        title="Recuento de URLs por plataforma",
        text="conteo",
        color="plataforma",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), legend_title_text="")
    return fig


def time_trend_figure(df: pd.DataFrame):
    """Línea temporal semanal del recuento de URLs por plataforma.
    Agrega por semana (inicio de semana) y colorea por plataforma.
    """
    if df.empty or "plataforma" not in df.columns or "url" not in df.columns:
        return px.line(title="Sin datos de 'url' para graficar tendencia temporal")

    dff = df.copy()
    dff["plataforma"] = dff["plataforma"].astype(str).fillna("Desconocido")
    if "fecha" not in dff.columns:
        return px.line(title="Sin datos de fecha para graficar tendencia temporal")

    dff["fecha"] = pd.to_datetime(dff["fecha"], errors="coerce")
    dff = dff[dff["fecha"].notna()]
    if dff.empty:
        return px.line(title="Sin fechas válidas para graficar tendencia temporal")

    key = "semana"
    dff[key] = dff["fecha"].dt.to_period("W").apply(lambda p: p.start_time.date())
    agg = dff.groupby([key, "plataforma"], dropna=False)["url"].count().reset_index(name="conteo")

    fig = px.line(
        agg,
        x=key,
        y="conteo",
        color="plataforma",
        markers=True,
        title="Tendencia temporal semanal de URLs por plataforma",
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20), legend_title_text="")
    return fig


def _get_platform_color_map(plataformas: list[str]) -> dict:
    """Devuelve un mapping de plataforma -> color representativo.
    Usa coincidencia por nombre (case-insensitive) y asigna un color por defecto
    para plataformas desconocidas.
    """
    base = {
        "instagram": "#E1306C",  # magenta
        "youtube": "#FF0000",    # rojo
        "tiktok": "#25F4EE",     # cian
        "linkedin": "#0A66C2",   # azul
        "medium": "#00AB6C",     # verde
        "dev.to": "#333333",     # gris oscuro
        "devto": "#333333",      # alias
        "telegram": "#0088cc",   # azul telegram
        "twitter": "#1DA1F2",    # azul twitter
        "x": "#000000",          # negro (X)
        "facebook": "#1877F2",   # azul facebook
    }
    default_color = "#7f7f7f"
    mapping: dict[str, str] = {}
    for p in plataformas:
        key = (p or "").strip().lower()
        color = base.get(key, default_color)
        mapping[p] = color
    return mapping