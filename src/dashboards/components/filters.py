from dash import dcc
from datetime import date


def build_date_filter(min_date: date | None, max_date: date | None) -> dcc.DatePickerRange:
    """Crea un selector de rango de fechas.
    Usa el id 'date-range'. Permite establecer límites mínimos y máximos.
    """
    return dcc.DatePickerRange(
        id="date-range",
        min_date_allowed=min_date,
        max_date_allowed=max_date,
        start_date=min_date,
        end_date=max_date,
        display_format="YYYY-MM-DD",
        clearable=True,
    )