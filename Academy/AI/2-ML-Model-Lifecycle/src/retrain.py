# src/retrain.py
"""
Retrain se il drift supera soglia; esegue train.run() con parametri di default.
"""
import json, subprocess, typer, pathlib

DRIFT_PATH = pathlib.Path("artifacts/drift_report.html")

app = typer.Typer()

@app.command()
def run(threshold: float = 0.6):
    from bs4 import BeautifulSoup
    drift = 0.0
    if DRIFT_PATH.exists():
        soup = BeautifulSoup(DRIFT_PATH.read_text(), "html.parser")
        drift = float(soup.select_one("#drift_score").text)
    if drift > threshold:
        typer.echo(f"⚠️  Drift {drift:.2f} > {threshold}: retraining…")
        subprocess.run(["python", "-m", "src.train", "run"])
    else:
        typer.echo(f"👍  Drift ok ({drift:.2f} ≤ {threshold})")

if __name__ == "__main__":
    app()
