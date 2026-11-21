# Sales Insight — Interactive Sales Analytics

**Turn spreadsheet exports into actionable commercial insights in minutes.**

Sales Insight is an interactive web application built with Python, Streamlit, Pandas, and Plotly. It enables sales managers to upload transaction-level CSV or Excel files, explore performance with dynamic filters, and download filtered results—without writing code.

## Business problem

Sales teams often work with static spreadsheet reports that are difficult to segment by region, sales representative, or time period. Preparing a new report for every business question consumes analyst time and delays decisions.

## Solution and business value

Sales Insight turns a standard sales export into an on-demand dashboard. Managers can quickly identify revenue trends, compare regions and team members, inspect transaction details, and reuse filtered data for follow-up analysis.

## Features

- Upload `.csv` or `.xlsx` files; the first Excel worksheet is read.
- Try the app instantly with bundled fictional demo data.
- Filter by **region**, **sales representative**, and **date range**.
- Track four KPIs: **total revenue**, **transactions**, **average transaction value**, and **units sold**.
- Explore interactive monthly revenue, regional revenue, and salesperson performance charts.
- Review individual transactions and export the filtered view as CSV.
- Validate required columns and notify users when invalid records are excluded.

## Technology stack

| Technology | Purpose |
| --- | --- |
| Python | Application logic |
| Streamlit | Interactive web interface |
| Pandas | Data cleaning, validation, and aggregation |
| Plotly | Interactive visualizations |
| openpyxl | Excel `.xlsx` file reading |
| GitHub | Source control and project portfolio |

## Required input format

Each row represents **one sales transaction**. The application expects the following headers (spelled exactly as shown):

| Column | Meaning | Example |
| --- | --- | --- |
| `Fecha` | Transaction date, `YYYY-MM-DD` | `2026-01-03` |
| `Region` | Commercial region | `Central` |
| `Vendedor` | Sales representative | `Ana López` |
| `Producto` | Product name | `Laptop` |
| `Cantidad` | Units sold, greater than zero | `2` |
| `Precio_Unitario` | Unit price in USD, zero or greater | `750.00` |

The app derives the revenue of each transaction as `Cantidad × Precio_Unitario`. Use comma-delimited UTF-8 CSV files or `.xlsx` spreadsheets. Dates should be unambiguous ISO dates, and numeric fields should not include currency symbols or thousands separators.

## Run locally

**Requirements:** Python 3.11+ and Git.

```bash
git clone https://github.com/YOUR-USERNAME/sales-insight-dataapp.git
cd sales-insight-dataapp
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Install dependencies and start the app:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`). The dashboard loads fictional demonstration data automatically. To analyze your own file, use the uploader in the sidebar.

> Replace `YOUR-USERNAME` in the clone URL with your own GitHub username after publishing the repository.

## Project structure

```text
sales-insight-dataapp/
├── app.py                 # Streamlit app and analytics logic
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── .gitignore             # Files excluded from version control
└── data/
    └── ventas_demo.csv    # Fictional sample transactions
```

## Data handling and limitations

Uploaded data is processed to render the dashboard and is not written to an external database by this implementation. Streamlit may keep cached data in the running application process; do not upload confidential client data to an untrusted public deployment. This is a portfolio-ready MVP, not an authenticated multi-tenant SaaS platform.

The MVP uses USD as its reporting currency, assumes one row per transaction, reads the first Excel worksheet, and excludes invalid rows with a visible warning. Revenue totals do not account for taxes, refunds, discounts, or currency conversion unless these are already reflected in the input unit prices.

## Roadmap

- Support configurable column mapping for client-specific exports.
- Add product-level performance and period-over-period comparisons.
- Add automated tests and data-quality reports.
- Support multiple currencies, localization, and authentication.
- Deploy a live demo with Streamlit Community Cloud.

## Portfolio use case

**Service demonstrated:** custom sales dashboards and spreadsheet-to-web-app automation for small and medium-sized businesses.

**Ideal client:** a sales manager who receives recurring spreadsheet exports and needs a self-service dashboard without investing in a full business intelligence platform.

**Project status:** functional MVP for local use; cloud deployment is a planned next step.
