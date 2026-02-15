# Lab: Basic ML Model with Weather Dataset + MLflow Integration

Welcome to this lab! Here you will learn how to:

1. **Load and prepare a weather dataset**, with temperature and humidity data.
2. **Train a Machine Learning model** using Scikit-learn, a powerful tool for Machine Learning in Python, to predict rain.
3. **Evaluate the model** computing metrics to determine how well it makes predictions on new data.
4. **Integrate MLflow**, one of the most used tool to track metrics, parameters, and model versions.

We will follow a guided approach with detailed explanations at each step.  
The first part focuses on Scikit-learn and the weather dataset. The second part extends the existing code with MLflow.

---

## Part 0: Setting Up the Python Environment

Before we begin, we need to ensure we have everything required to run the lab properly.  

### **Requirements**

This lab assumes that **Python** and **miniconda** are already installed, the repository [kiratech/labs](https://github.com/kiratech/labs.git) is accessible, and **Git** is properly configured on your local machine. Furthermore, **VSCode** or an IDE able to run Jupyter Notebooks, must be installed as well.  
In order to execute this laboratory, you will be asked to install a set of tools common in Machine Learning field:

- [**scikit-learn**](https://scikit-learn.org/stable/index.html): Machine learning library with modeling and evaluation tools.
- [**pandas**](https://pandas.pydata.org/): Framework for data manipulation and analysis in Python.
- [**seaborn**](https://seaborn.pydata.org/): Data visualization library based on Matplotlib.
- [**mlflow**](https://mlflow.org/): Tool for tracking and managing machine learning experiments.  

### 1. Clone the Repository

To start, clone the lab repository by running the following command in the terminal:

```sh
  git clone https://github.com/kiratech/labs.git
```

### 2. Checkout the Lab Branch

After cloning the repository, navigate to the project folder:

```sh
  cd labs
```

Then, checkout the `lab` branch:

```sh
  git checkout academy-ai
```

This folder contains resources related to AI-themed labs.

### 3. Navigate to the 1-Intro-To-ML-And-MLOps Folder

Go to the folder of the first lab:

```sh
  cd Academy/AI/1-Intro-To-ML-And-MLOps
```

### 4. Create a Virtual Environment

A virtual environment allows you to isolate the project's dependencies from the system-wide ones.

Using the **VSCode** terminal, create a virtual environment:

```sh
  conda create --name lab_env python=3.12 pip -y
```

Activate the Virtual Environment:

```sh
  conda activate lab_env
```

You should see the `(lab_env)` prefix in the terminal, indicating that the virtual environment is active.

### 5. Install Required Packages

Besides the default packages in the environment, additional libraries may be needed for the lab.  
Before installing them, it's always a good practice to update `pip` to avoid compatibility issues:

```sh
  pip install --upgrade pip
```  

Now, install some essential packages for data analysis and machine learning:

```sh
  pip install scikit-learn pandas seaborn mlflow ipykernel
```  

Verify that the packages were installed correctly with:  

```sh
  conda list
```  

At this point, you can proceed with the `lab.ipynb` file.

### 6. Open the Project in VSCode

At this point, open VSCode from the file explorer or by running the command:

```sh
  code .
```
