# Lab: Prompt‑Engineering and LoRA Fine‑Tuning

Welcome to this live lab!
In the previous lab session we discussed how to:

1. **Train a classification model** on a real dataset using `Scikit-learn`.
2. **Manage and track your experiments** with `MLflow`.
3. **Build CI/CD-like workflows** using `Makefile` and `nox`.
4. **Build scalable and orchestrated ML pipelines** using `Prefect`.
5. **Monitor data drift over time** and trigger retraining with `Evidently`.

In this session, you will run two Jupyter notebooks that demonstrate:

- Practical prompt‑engineering patterns in `notebook 1_LabLLM.ipynb`, the craft of writing clear, explicit instructions for an LLM.
- A LoRA fine‑tuning workflow on model T5‑small in `notebook 2_LabLLM_LoRA.ipynb`, a lightweight fine-tuning technique for transformers.

We'll leverage two big providers for this lab:

- **Google Colab**: a free, browser-based Jupyter environment hosted by Google. Colab gives you a temporary Linux VM with Python, CUDA drivers, and optional GPU/TPU. You open a .ipynb notebook, run cells just like in Jupyter, and share links with classmates—no local setup required.

- **Hugging Face**: A community and tooling hub for modern AI.  

    It offers:

    - Model Hub: 500 k-plus pre-trained models (transformers, diffusers, etc.).
    - Datasets Hub: curated datasets in one-line API.
    - Inference API / Endpoints: hosted model inference in the cloud.
    - Libraries: transformers, datasets, peft, and more.

    Creating a (free) HF account lets you:

    - Download models.
    - Push your own models/adapters/data.
    - Generate an access token that notebooks use to call hosted endpoints securely.

---

## Repository contents

| Path/Name                               | What it is and why it matters                    |
| --------------------------------------- | ---------------------------------------------- |
| `notebooks/1_LabLLM.ipynb`                        | Prompt‑engineering walkthrough (Mistral‑7B)    |
| `notebooks/2_LabLLM_LoRA.ipynb`                   | LoRA adapter training on a 250‑row support set |
| `files/customer_support_lora_dataset_250.csv` | Tiny dataset used in Notebook 2                |
| `README` (this file)                  | Quickstart and background                        |

## Prerequisites

| Tool / Account           | Why you need it                              | Sign‑up link                                                             |
| ------------------------ | -------------------------------------------- | ------------------------------------------------------------------------ |
| **Google account**       | Required to open Colab notebooks             | [https://accounts.google.com/signup](https://accounts.google.com/signup) |
| **Hugging Face account** | Lets you call hosted models & store adapters | [https://huggingface.co/join](https://huggingface.co/join)               |

### 1 Create your HF account and token

1. Go to [https://huggingface.co/join](https://huggingface.co/join) and sign up (email and password).
2. Verify your email address (check spam folder too).
3. Navigate to **Settings > Access Tokens > New Token**.
4. Name it e.g. `ai‑academy‑lab` and select **"Read"** scope (fine for this lesson).
5. Copy the token. **You will paste it into the notebook when prompted**.
6. Treat the token like a password and do **not** share or commit it to GitHub.

### 2 Recommended Colab runtime settings

- **GPU:** In Colab, go to **Runtime > Change runtime type > Hardware accelerator > GPU**.
- **RAM:** The default *Standard* tier is enough. No paid upgrade needed.

---

## Run the notebooks in Colab

### 1  Clone the Repository

To start, clone the lab repository by running the following command in the terminal:

```sh
  git clone https://github.com/kiratech/labs.git
```

### 2 Checkout the Lab Branch

After cloning the repository, checkout the `academy-ai` branch:

```sh
  git checkout academy-ai
```  

Then, navigate to the project folder:

```sh
  cd labs/Academy/AI/3-LLM
```  

This folder contains resources related to this lab.  
Open Google Colab and import, everything at root level, the content of the folders notebooks and files.  
From now you can continue on the notebooks.  

---

## Suggested readings and references

- [OpenAI Cookbook – GPT‑4 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide): a new prompting guide that lays out a practical structure for building powerful prompts, especially with GPT-4.1. It’s short, clear, and highly effective for anyone working with agents, structured outputs, tool use, or reasoning-heavy tasks.
- [Google Prompt Engineering pdf](https://drive.google.com/file/d/1AbaBYbEa_EbPelsT40-vj64L-2IwUJHy/view): whether you're technical or non-technical, this might be one of the most useful prompt engineering resources out there right now. Google just published a 68-page whitepaper focused on Prompt Engineering (focused on API users), and it goes deep on structure, formatting, config settings, and real examples.
