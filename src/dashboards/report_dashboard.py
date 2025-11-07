import argparse
import logging
import flask.cli as flask_cli
import pandas as pd
from dash import Dash, dcc, html, Input, Output
from dash import dash_table
import plotly.express as px


def build_app(df: pd.DataFrame) -> Dash:
    app = Dash(__name__)

    plataformas = (
        df["plataforma"].fillna("Desconocido").astype(str).unique().tolist()
        if "plataforma" in df.columns
        else []
    )

    app.layout = html.Div(
        [
            html.H2("Telelinker Report (Dash)"),
            html.Div(
                [
                    html.Label("Filtrar por plataforma"),
                    dcc.Dropdown(
                        id="platform-filter",
                        options=[{"label": p, "value": p} for p in sorted(plataformas)],
                        value=None,
                        placeholder="Selecciona una plataforma (opcional)",
                        clearable=True,
                    ),
                ],
                style={"maxWidth": "480px"},
            ),
            html.Hr(),
            html.H4("Vista previa de los datos (primeras 20 filas)"),
            dash_table.DataTable(
                id="data-preview",
                columns=[{"name": c, "id": c} for c in df.columns],
                data=df.head(20).to_dict("records"),
                page_size=20,
                style_table={"overflowX": "auto"},
            ),
            html.Hr(),
            html.H4("Recuento de URLs por plataforma"),
            dcc.Graph(id="platform-count-graph"),
            dcc.Store(id="data-store", data=df.to_dict("records")),
        ],
        style={"padding": "16px", "fontFamily": "Arial, sans-serif"},
    )

    @app.callback(
        Output("platform-count-graph", "figure"),
        Input("platform-filter", "value"),
        Input("data-store", "data"),
    )
    def update_graph(selected_platform, data_records):
        dff = pd.DataFrame(data_records)
        if selected_platform:
            dff = dff[dff["plataforma"].astype(str) == selected_platform]

        if "plataforma" in dff.columns and "url" in dff.columns and not dff.empty:
            counts = (
                dff.groupby("plataforma")["url"].count().reset_index(name="conteo")
            )
            fig = px.bar(
                counts,
                x="plataforma",
                y="conteo",
                title="URLs por plataforma",
                text="conteo",
            )
            fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
            fig.update_traces(textposition="outside")
            return fig
        else:
            # Gráfico vacío amigable
            return px.bar(title="Sin datos para graficar")

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

        serve(app.server, host=args.host, port=args.port)
    else:
        # Flask dev server: ocultar banner y logs de werkzeug si quiet
        flask_cli.show_server_banner = lambda *args, **kwargs: None
        if args.quiet:
            logging.getLogger("werkzeug").setLevel(logging.ERROR)
            app.server.logger.setLevel(logging.ERROR)
        app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()