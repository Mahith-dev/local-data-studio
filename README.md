# Local Data Studio ⚡

An on-device, privacy-first desktop platform for automated tabular data diagnostics, exploratory feature engineering, and interactive machine learning.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi)
![Scikit--Learn](https://img.shields.io/badge/Scikit--Learn-1.4%2B-F7931E?logo=scikit-learn)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-38B2AC?logo=tailwind-css)
![Plotly](https://img.shields.io/badge/Plotly.js-2.32-3F4F75?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Overview

Most modern automated machine learning platforms force users to transmit proprietary, private datasets to external cloud infrastructure. **Local Data Studio** bypasses the cloud entirely by executing all ingestion, mathematical auditing, and machine learning pipelines locally on native client hardware.

Built with a high-performance decoupled architecture, it leverages a Python backend for multithreaded matrix calculations and a hardware-accelerated native webview interface for fluid visual analytics.

---

## Key Features

- **Privacy-First On-Device Execution:** Zero telemetry or cloud egress. Data remains strictly in local memory and storage.
- **Adaptive Multi-File Ingestion:** Automatically detects CSV/TSV delimiters (comma, semicolon, tab), filters documentation metadata (such as `.names`), and auto-merges multi-file datasets sharing identical schemas.
- **Deterministic Auto-Advisor:**
  - **Multicollinearity Screening:** Flags cross-feature correlations ($\vert{}r\vert{} > 0.70$) to prevent variance inflation.
  - **Outlier Density Scanning:** Calculates interquartile boundaries ($1.5 \times \text{IQR}$) across numeric vectors.
  - **Missing Value Forensics:** Categorizes null densities and suggests specific imputation paths.
- **Dimensionality Reduction Studio (PCA):**
  - Instant feature normalization via `StandardScaler`.
  - Interactive **2D Principal Component Projection** powered by Plotly.js with dynamic cluster grouping and zoom/pan capabilities.
  - Full **Scree Plot** rendering individual and cumulative variance explained up to the 90% threshold.

---

## Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                  Native Desktop Container                   │
│                                                             │
│   ┌──────────────────────────┐    IPC     ┌──────────────┐  │
│   │   Webview Interface      │ ◄────────► │ Local Engine │  │
│   │   - Tailwind CSS         │ (HTTP/REST)│ - FastAPI    │  │
│   │   - Plotly.js Canvas     │            │ - Pandas     │  │
│   │   - Reactive DOM Engine  │            │ - Scikit-ML  │  │
│   └──────────────────────────┘            └──────────────┘  │
│                                                   │         │
│                                            Native CPU / RAM │
└─────────────────────────────────────────────────────────────┘
