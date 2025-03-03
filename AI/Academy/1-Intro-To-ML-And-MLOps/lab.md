# Lab: Modello ML di base con Dataset Meteo + Integrazione MLflow

In questo laboratorio, affrontiamo un percorso step-by-step:

1. **Caricare e preparare un dataset meteo** (con dati di temperatura e umidità) per prevedere se pioverà o meno.
2. **Addestrare un modello di Machine Learning** con Scikit-learn.
3. **Valutare il modello** e comprendere i risultati.
4. **Estendere il progetto** integrando **MLflow** per tracciare metriche, parametri e versioni del modello.

La prima parte si concentra su Scikit-learn e il dataset meteo. La seconda parte estende il codice esistente con MLflow.

---

## Parte 1: Dai dati al modello ML (Supervised Learning con Scikit-learn)

### Obiettivo
- Creare un semplice **modello di classificazione** per predire la pioggia basandoci su dati di temperatura e umidità.

### 1. Preparazione del Dataset

Per semplicità, qui useremo un dataset di esempio:
[Weather Test Data](https://raw.githubusercontent.com/boradpreet/Weather_dataset/refs/heads/master/Weather%20Test%20Data.csv)

```python
import pandas as pd

# URL del dataset (sostituiscilo con il tuo link)
url = "https://raw.githubusercontent.com/boradpreet/Weather_dataset/refs/heads/master/Weather%20Test%20Data.csv"

# Carica il dataset
df = pd.read_csv(url)

# Mostra le prime righe
print(df.head())
```

---

###  2. Esplorazione e pulizia dei Dati
1. Controlliamo se ci sono valori mancanti
2. Trasformiamo la colonna `Label` in una variabile numerica (0 = NoRain, 1 = Rain)
3. Selezione delle feature 


```python
# 1. Rimozione dei valori mancanti
df = df.dropna()

# 2. Conversione della colonna 'RainToday' in valori numerici
df['RainToday'] = df['RainToday'].apply(lambda x: 1 if x == 'Yes' else 0)

# 3. Selezione delle feature 
features = ['MinTemp', 'MaxTemp', 'Humidity3pm', 'Humidity9am']

X = df[features]
y = df['RainToday']
```
---
### 3. Suddivisione del Dataset in Training e Test

Prima di addestrare il modello, dividiamo il dataset in:
- **X** (features) → Temperatura, Umidità
- **y** (target) → Label (Rain/NoRain)

```python
from sklearn.model_selection import train_test_split

# Suddivisione dei dati (80% training, 20% testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

```

---
###  4. Creazione e Addestramento del Modello

Utilizziamo un classificatore semplice, ad esempio **RandomForestClassifier**.

```python
from sklearn.ensemble import RandomForestClassifier

# Creazione e addestramento del modello
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

```

---

### 5. Valutazione del Modello

Calcoliamo l’accuratezza e visualizziamo la matrice di confusione.

```python
from sklearn.metrics import accuracy_score, classification_report

# Predizioni sul set di test
y_pred = model.predict(X_test)

# Calcolo dell'accuratezza
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuratezza del modello: {accuracy:.2f}")

# Report di classificazione
print(classification_report(y_test, y_pred))
```

---

### Conclusione (Parte 1)
In questa prima parte, abbiamo:
1. Caricato un dataset relativo alle condizioni meteo
2. Pulito i dati e trasformato la variabile target
3. Suddiviso il dataset in training e test
4. Creato un modello di classificazione con RandomForest
5. Valutato le prestazioni con accuratezza e matrice di confusione

---
## Tech: Installazione e Configurazione di MLflow in Locale con Docker

###  Obiettivo
- Configurare un'istanza MLflow in locale per registrare esperimenti.

###  1. Avviare MLflow con Docker

Esegui il seguente comando per avviare un'istanza locale di MLflow:

```bash
docker pull ghcr.io/mlflow/mlflow

docker run -p 5001:5000 --name mlflow-server \
  -v $(pwd)/mlruns:/mlruns \
  ghcr.io/mlflow/mlflow:latest server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root /mlruns \
  --host 0.0.0.0
```

- **`-p 5001:5000`**: Espone MLflow sulla porta 5001
- **`-v $(pwd)/mlruns:/mlruns`**: Monta la cartella locale per salvare gli esperimenti
- **`--backend-store-uri sqlite:///mlflow.db`**: Utilizza un database SQLite per il tracking

Una volta avviato, MLflow sarà disponibile all’indirizzo:

```
http://127.0.0.1:5001
```

Ora possiamo passare alla terza parte e integrare MLflow nel nostro codice!

---
## Parte 2: Integrazione con MLflow

Adesso, estendiamo il codice esistente per **tracciare i nostri esperimenti** con **MLflow**. Questo ci permetterà di:
- Loggare i nostri parametri (es. `n_estimators`)
- Salvare l’accuratezza e altre metriche
- Salvare il modello e ricaricarlo facilmente

### Obiettivo
- Integrare MLflow nel codice esistente per versionare e tracciare le metriche del modello.

### 1. Installazione e Setup MLflow

Installa MLflow:

```bash
pip install mlflow
```

```python
import mlflow
import mlflow.sklearn

# Impostiamo un nome per l'esperimento
mlflow.set_tracking_uri("http://127.0.0.1:5001")
mlflow.set_experiment("weather_classification_experiment")
```

---

### 2. Logging dei Parametri e Metriche

Possiamo loggare:
- Parametri → `n_estimators` e altre impostazioni
- Metriche → accuratezza
- Modello → versione del modello addestrato


```python
# Usando il modello creato nella Parte 1
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

n_estimators = 100

# Creiamo una nuova run MLflow
with mlflow.start_run():
    # Log Param
    mlflow.log_param("n_estimators", n_estimators)

    # Creazione del modello
    rf_model = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    rf_model.fit(X_train, y_train)

    # Calcolo metriche
    y_pred = rf_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    mlflow.log_metric("accuracy", accuracy)

    # Salviamo il modello
    mlflow.sklearn.log_model(rf_model, "random_forest_model")

    print(f"Esperimento concluso. Accuratezza registrata: {accuracy:.2f}")
```

---

###  3. Visualizzare e Confrontare i Risultati

MLflow fornisce un’interfaccia web per esplorare tutte le run ed esperimenti.

```bash
http://127.0.0.1:5001
```

Accedi all’URL indicato nel terminale. Nella sezione **Experiments** potrai vedere:
- Parametri loggati
- Metriche
- Modelli salvati

### 4. Caricare un Modello Salvato con MLflow

Possiamo anche recuperare un modello da MLflow per fare previsioni future.

```python
import mlflow.sklearn
from sklearn.metrics import accuracy_score

# Inserisci un run_id reale che trovi nell'interfaccia MLflow
RUN_ID = "<run_id_della_tua_run>"

loaded_model = mlflow.sklearn.load_model(f"runs:/{RUN_ID}/random_forest_model")

# Verifichiamo l'accuratezza
y_loaded_pred = loaded_model.predict(X_test)
acc_loaded = accuracy_score(y_test, y_loaded_pred)
print(f"Accuratezza del modello caricato: {acc_loaded:.2f}")
```

## Conclusioni
In questo laboratorio abbiamo:
1. **Creato un modello di classificazione con Scikit-learn** su un dataset meteo.
2. **Aggiunto MLflow** per tracciare parametri, metriche e gestire le versioni del modello.
3. **Visualizzato i risultati** con l’interfaccia MLflow UI e ricaricato il modello salvato.

 **Prossimi Passi**
- Provare iperparametri diversi (`n_estimators`, `max_depth`, ecc.) e confrontare i risultati su MLflow.
- Integrare un sistema di **continuous integration/continuous deployment (CI/CD)** per distribuire automaticamente il modello.
- Monitorare in produzione il drift del modello (eventuali cali di accuratezza).
