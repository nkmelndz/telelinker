import streamlit as st
import pandas as pd
import sys

def main():
    st.title("Telelinker Dashboard")

    # Get the file path from the command-line arguments
    file_path = None
    if len(sys.argv) > 2 and sys.argv[1] == "--file":
        file_path = sys.argv[2]

    if file_path:
        try:
            # Load the CSV file
            data = pd.read_csv(file_path)

            # Display the data
            st.write("### Vista previa de los datos:")
            st.dataframe(data.head())

            # Count URLs by platform and plot a bar chart
            if "plataforma" in data.columns and "url" in data.columns:
                platform_counts = data.groupby("plataforma")["url"].count()
                st.write("### Gráfico de barras: Recuento de URLs por plataforma")
                st.bar_chart(platform_counts)
            else:
                st.warning("Las columnas 'plataforma' y/o 'url' no están presentes en el archivo.")
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
    else:
        st.info("No se proporcionó un archivo CSV. Usa el argumento --file para especificar uno.")

if __name__ == "__main__":
    main()