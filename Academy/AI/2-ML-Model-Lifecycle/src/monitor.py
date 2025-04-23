# src/monitor.py
"""
Lettura delle predizioni servite, verifica di drift su Evidently
e scrittura di un report HTML.
Richiamabile via cron o manualmente: python monitor.py run
"""
import typer, pandas as pd
from evidently import Report
from evidently.metrics import DataDriftPreset

app = typer.Typer()

@app.command()
def run(ref_csv: str = "data/reference.csv",
        cur_csv: str = "data/current.csv"):
    ref, cur = pd.read_csv(ref_csv), pd.read_csv(cur_csv)
    report = Report(metrics=[DataDriftPreset()])
    report.run(ref, cur)
    report.save_html("artifacts/drift_report.html")
    typer.echo("✅  Drift report scritto in artifacts/drift_report.html")

if __name__ == "__main__":
    app()
