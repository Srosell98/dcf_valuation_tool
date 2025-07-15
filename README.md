# DCF Streamlit App

A professional, modular Streamlit web app for discounted cash flow (DCF) valuation and stock analysis. Provides interactive valuation, sensitivity analysis, fundamental scoring (including Piotroski F-score), and a technical dashboard, all using live Yahoo Finance data.

---

## Features

* DCF valuation with customizable parameters
* Historical and projected FCF charts (Plotly)
* Sensitivity tables for discount/growth scenarios
* Piotroski F-score and fundamental dashboard
* Technical indicators: SMA, RSI, MACD
* Modern UI with custom styling

## Project Structure

```
.
├── app.py               # Main entry-point (Streamlit UI logic)
├── requirements.txt     # Dependencies
├── .gitignore           # Ignore venv, logs, Streamlit cache, etc.
├── README.md            # This file
├── src/
│   ├── data.py          # Data loading, yfinance integration
│   ├── dcf.py           # DCF core, growth, sensitivity
│   ├── technicals.py    # Technical indicators
│   ├── fundamentals.py  # Fundamental analysis & scoring
│   ├── visuals.py       # Plotly chart creators
│   ├── ui.py            # Streamlit UI helpers & styling
│   ├── config.py        # App-level constants and styling
│   └── utils.py         # Generic helpers
├── breadth.py           # (External, if needed for market breadth)
```

## Setup & Installation (with Virtual Environment)

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Srosell98/dcf_valuation_tool.git
   cd <repo-folder>
   ```
2. **Create a Python virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate         # On Mac/Linux
   # OR
   .venv\Scripts\activate            # On Windows
   ```
3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```
   
**To deactivate the virtual environment:**

```bash
deactivate
```

---

## How to Run the App

```bash
streamlit run app.py
```

Go to the local URL displayed by Streamlit (usually [http://localhost:8501](http://localhost:8501))

## Dependencies

* streamlit
* yfinance
* pandas
* numpy
* plotly
* pandas\_ta
* breadth.py

## Module Structure Explained

* **src/data.py** — Handles all data acquisition (Yahoo, cleaning, extraction)
* **src/dcf.py** — All DCF, free cash flow, growth, and sensitivity calculations
* **src/technicals.py** — Adds SMA, RSI, MACD technical indicators
* **src/fundamentals.py** — Calculates Piotroski F-score and fundamental metrics
* **src/visuals.py** — Plotly chart builders for FCF, projections, and more
* **src/ui.py** — Custom CSS, metric card helpers, table formatters, etc.
* **src/config.py** — Central constants (default rates, color schemes, etc.)
* **src/utils.py** — Miscellaneous utility functions
* **breadth.py** — Not working: Market breadth data provider 

## Customization

* You can further modularize, add tests, or configure advanced Streamlit options as needed.

---

**For questions or improvements, submit issues or pull requests!**
