# Lab: Modello ML di base con Dataset Meteo + Integrazione MLflow

Benvenuto in questo laboratorio! Qui imparerai a:

1. **Caricare e preparare un dataset meteo**, con dati di temperatura e umidità.
2. **Addestrare un modello di Machine Learning** con Scikit-learn per prevedere la pioggia.
3. **Valutare il modello** e comprendere i risultati.
4. **Integrare MLflow** per tracciare metriche, parametri e versioni del modello.

Seguiremo un approccio guidato, con spiegazioni dettagliate ad ogni passaggio.  
La prima parte si concentra su Scikit-learn e il dataset meteo. La seconda parte estende il codice esistente con MLflow.

---

## Parte 0: Setup dell'Environment per Python

Prima di iniziare, dobbiamo assicurarci di avere tutto il necessario per eseguire correttamente il laboratorio.  

#### **Requisiti**

Questo laboratorio assume che **Python** e **miniconda** siano già installati, la repository [kiratech/labs](https://github.com/kiratech/labs.git) sia accessibile e che Git sia configurato correttamente sul computer locale.

### 1. Clonare la Repository
Per iniziare, clona la repository del laboratorio eseguendo il seguente comando nel terminale:
```sh
  git clone https://github.com/kiratech/labs.git
```

### 2. Fare il Checkout del Branch Lab

Dopo aver clonato la repository, entra nella cartella del progetto:

```sh
  cd labs
```

Quindi, fai il checkout del branch `lab`:

```sh
  git checkout academy-ai
```
In questa cartella sono presenti le risorse relative ai laboratori con tema AI.

### 3. Spostarsi nella Cartella 1-Intro-To-ML-And-MLOps

Naviga nella cartella del primo laboratorio:

```sh
  cd AI/Academy/1-Intro-To-ML-And-MLOps
```

### 4. Apri il progetto in VSCode

A questo punto apri VSCode dall'explorer oppure lanciando il comando:
```sh
  code .
```

### 5. Creare un Virtual Environment

Un ambiente virtuale permette di isolare le dipendenze del progetto da quelle di sistema.

Tramite il terminale di **VSCode**, crea un ambiente virtuale:

```sh
  conda create --name lab_env python=3.12 pip -y
```

Attiva l'Ambiente Virtuale
```sh
  conda activate lab_env
```

Dovresti vedere il prefisso `(lab_env)` nel terminale, indicando che l'ambiente virtuale è attivo.

### 6. Installare i Pacchetti Necessari

Oltre ai pacchetti presenti di default nell'environment, è possibile che servano librerie aggiuntive per il laboratorio.  
Prima di installarle, è sempre buona pratica aggiornare `pip` per evitare problemi di compatibilità:
```sh
  pip install --upgrade pip
```  

Ora installiamo alcuni pacchetti fondamentali per l'analisi dei dati e il machine learning:
```sh
  pip install scikit-learn pandas seaborn mlflow ipykernel
```  
- [**scikit-learn**](https://scikit-learn.org/stable/index.html): Libreria per il machine learning con strumenti di modellazione e valutazione.
- [**pandas**](https://pandas.pydata.org/): Framework per la manipolazione e l'analisi dei dati in Python.
- [**seaborn**](https://seaborn.pydata.org/): Libreria per la visualizzazione di dati basata su Matplotlib.
- [**mlflow**](https://mlflow.org/): Strumento per il tracciamento e la gestione di esperimenti di machine learning.  

Verifica che i pacchetti siano stati installati correttamente con:  
```sh
  conda list
```  

A questo punto si può continuare sul file `lab.ipynb`.