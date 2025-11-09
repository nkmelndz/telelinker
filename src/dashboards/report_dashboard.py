import argparse
import logging
import flask.cli as flask_cli
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px

from .components.general import (
    build_general_layout,
    likes_sum_figure,
    comments_sum_figure,
    url_count_figure,
    time_trend_figure,
)
from .components.platform_specific import (
    build_platform_specific_layout,
    top_authors_figure,
    top_authors_likes_figure,
    top_authors_comments_figure,
    engagement_trend_figure,
    top_posts_engagement_figure,
)


def build_app(df: pd.DataFrame) -> Dash:
    app = Dash(__name__)
    # Cache de assets estáticos para reducir carga inicial y solicitudes repetidas
    try:
        app.server.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600  # 1 hora
    except Exception:
        pass
    # Tema de gráficos consistente
    try:
        px.defaults.template = "plotly_white"
        px.defaults.color_discrete_sequence = px.colors.qualitative.Set2
    except Exception:
        pass

    # Normalizar/parsear fecha_publicacion a datetime (columna auxiliar 'fecha')
    if "fecha_publicacion" in df.columns:
        # Intento robusto de parseo a datetime
        df = df.copy()
        df["fecha"] = pd.to_datetime(df["fecha_publicacion"], errors="coerce")
    else:
        df = df.copy()
        df["fecha"] = pd.NaT

    # Rango de fechas para el DatePickerRange
    fecha_min = (
        df["fecha"].min().date() if df["fecha"].notna().any() else None
    )
    fecha_max = (
        df["fecha"].max().date() if df["fecha"].notna().any() else None
    )

    # Opciones de plataformas
    plataformas = (
        df["plataforma"].fillna("Desconocido").astype(str).unique().tolist()
        if "plataforma" in df.columns
        else []
    )

    # Layout principal: filtro de fechas debajo del subtítulo de gráficos generales y un filtro específico en la sección por plataforma
    app.layout = html.Div(
        [
            html.H2("Telelinker Report (Dash)"),
            # Sector general con filtro de fechas embebido (construido internamente)
            build_general_layout(fecha_min, fecha_max),
            html.Hr(),
            # Sector por plataforma
            build_platform_specific_layout(plataformas, fecha_min, fecha_max),
            # Almacenar datos
            dcc.Store(id="data-store", data=df.to_dict("records")),
            # Store oculto para manejar apertura de URL al hacer clic en Top publicaciones
            dcc.Store(id="top-posts-open-url"),
        ],
        className="dashboard",
    )

    @app.callback(
        Output("likes-sum-by-platform", "figure"),
        Output("comments-sum-by-platform", "figure"),
        Output("url-count-by-platform", "figure"),
        Output("time-trend-by-platform", "figure"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("data-store", "data"),
    )
    def update_general_charts(start_date, end_date, data_records):
        dff = pd.DataFrame(data_records)
        # Asegurar columna 'fecha' en datetime
        if "fecha" in dff.columns:
            dff["fecha"] = pd.to_datetime(dff["fecha"], errors="coerce")
        # Filtrado por rango de fechas si corresponde
        if start_date:
            try:
                start = pd.to_datetime(start_date)
                dff = dff[(dff["fecha"].isna()) | (dff["fecha"] >= start)]
            except Exception:
                pass
        if end_date:
            try:
                end = pd.to_datetime(end_date)
                dff = dff[(dff["fecha"].isna()) | (dff["fecha"] <= end)]
            except Exception:
                pass

        return (
            likes_sum_figure(dff),
            comments_sum_figure(dff),
            url_count_figure(dff),
            time_trend_figure(dff),
        )

    @app.callback(
        Output("top-authors-by-platform", "figure"),
        Output("top-authors-likes-by-platform", "figure"),
        Output("top-authors-comments-by-platform", "figure"),
        Output("engagement-trend-by-platform", "figure"),
        Output("top-posts-engagement-by-platform", "figure"),
        Input("platform-select", "value"),
        Input("platform-date-range", "start_date"),
        Input("platform-date-range", "end_date"),
        Input("data-store", "data"),
    )
    def update_top_authors(selected_platform, start_date, end_date, data_records):
        dff = pd.DataFrame(data_records)
        if "fecha" in dff.columns:
            dff["fecha"] = pd.to_datetime(dff["fecha"], errors="coerce")
        if start_date:
            try:
                start = pd.to_datetime(start_date)
                dff = dff[(dff["fecha"].isna()) | (dff["fecha"] >= start)]
            except Exception:
                pass
        if end_date:
            try:
                end = pd.to_datetime(end_date)
                dff = dff[(dff["fecha"].isna()) | (dff["fecha"] <= end)]
            except Exception:
                pass
        return (
            top_authors_figure(dff, selected_platform),
            top_authors_likes_figure(dff, selected_platform),
            top_authors_comments_figure(dff, selected_platform),
            engagement_trend_figure(dff, selected_platform),
            top_posts_engagement_figure(dff, selected_platform),
        )

    # Clientside callback: abrir URL en nueva pestaña al hacer clic en una barra del Top publicaciones
    app.clientside_callback(
        r"""
        function(clickData) {
            if (!clickData || !clickData.points || !clickData.points.length) {
                return window.dash_clientside.no_update;
            }
            var y = clickData.points[0].y;
            if (typeof y === 'string' && /^https?:\/\//.test(y)) {
                try { window.open(y, '_blank', 'noopener,noreferrer'); } catch (e) {}
                return y; // guardamos última URL clicada en el Store (opcional)
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("top-posts-open-url", "data"),
        Input("top-posts-engagement-by-platform", "clickData"),
    )

    return app


def main():
    parser = argparse.ArgumentParser(description="Telelinker Dash report")
    parser.add_argument("--file", required=True, help="Ruta al CSV (posts.csv)")
    parser.add_argument("--host", default="127.0.0.1", help="Host a usar")
    parser.add_argument("--port", type=int, default=8501, help="Puerto a usar")
    parser.add_argument(
        "--server",
        choices=["waitress", "dev"],
        default="waitress",
        help="Servidor WSGI: 'waitress' (prod-like) o 'dev' (Flask).",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=8,
        help="Número de threads para Waitress (mayor reduce cola de tareas)",
    )
    parser.add_argument(
        "--backlog",
        type=int,
        default=64,
        help="Backlog del socket para Waitress (cola de conexiones pendientes)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suprime logs de acceso y banners del servidor",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.file)
    app = build_app(df)
    # Servidor y logging
    if args.server == "waitress":
        # Waitress evita el banner de desarrollo; opcionalmente silenciamos sus logs
        if args.quiet:
            # Desactivar loggers de waitress (incluyendo subloggers como waitress.queue)
            class _NoWaitressLogs(logging.Filter):
                def filter(self, record):
                    return not record.name.startswith("waitress")

            root_logger = logging.getLogger()
            root_logger.addFilter(_NoWaitressLogs())

            for name in ("waitress", "waitress.queue", "waitress.server", "waitress.access", "waitress.channel"):
                lg = logging.getLogger(name)
                lg.setLevel(logging.CRITICAL)
                lg.propagate = False
                # Eliminar cualquier handler para evitar salida
                try:
                    lg.handlers.clear()
                except Exception:
                    pass
                lg.disabled = True
        from waitress import serve

        logging.getLogger(__name__).info(
            "Iniciando Waitress threads=%s backlog=%s host=%s port=%s",
            args.threads,
            args.backlog,
            args.host,
            args.port,
        )
        serve(app.server, host=args.host, port=args.port, threads=args.threads, backlog=args.backlog)
    else:
        # Flask dev server: ocultar banner y logs de werkzeug si quiet
        flask_cli.show_server_banner = lambda *args, **kwargs: None
        if args.quiet:
            logging.getLogger("werkzeug").setLevel(logging.ERROR)
            app.server.logger.setLevel(logging.ERROR)
        app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()