# IMC2024-CookielessBrowsing
This repository contains web crawling and analysis code for the IMC 2024 paper "Browsing without Third-Party Cookies: What Do You See?".

## Setup
Only Ubuntu 20.04 LTS is officially supported.

To create the `cookie` [conda](https://docs.conda.io/en/latest/miniconda.html) environment, execute:

```bash
conda env create -f environment.yml
```

Activate the environment with:
```bash
conda activate cookie
```

## Usage
To start a crawl, execute:
```bash
python3 sbatch_main.py --jobs <number of slurm jobs>
```
If you do not have Slurm, you can start a single job using `main.py`.

After crawling, use `extract_differences.py` to compute differences in extracted features.

To analyze the differences, use `classification_algo.ipynb`.
