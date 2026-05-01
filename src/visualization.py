"""Entry point for the NBA passing network Dash app."""
from src.layout import app
import src.callbacks  # noqa: F401 — imported to register callbacks


def run_visualization() -> None:
    """Launch the interactive passing network visualization."""
    app.run(debug=False)