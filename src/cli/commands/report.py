import os


def configure_streamlit():
    """
    Ensure Streamlit configuration is set to disable telemetry and remove the Deploy button.
    """
    config_dir = os.path.expanduser("~/.streamlit")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.toml")
    with open(config_path, "w") as config_file:
        config_file.write(
            "[browser]\n"
            "gatherUsageStats = false\n"
            "[server]\n"
            "enableXsrfProtection = true\n"
            "enableCORS = false\n"
        )


# Ensure Streamlit is configured before running the dashboard
configure_streamlit()


def run(args):
    """
    Launch the Streamlit dashboard and pass the --file argument.

    Args:
        args: Parsed arguments from the CLI, including the '--file' argument.
    """
    file_path = args.file

    if not os.path.exists(file_path):
        print(f"Error: El archivo '{file_path}' no existe.")
        return

    # Launch Streamlit with the provided file
    os.system(f"streamlit run src/dashboards/report_dashboard.py -- --file {file_path}")