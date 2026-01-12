# India Household Structure & E-commerce Analysis
## Product Discovery Project for Quick-Commerce

### 🎯 Objective
Analyze whether household composition correlates with online purchasing behavior across Indian states/UTs, and translate findings into actionable product-level insights for quick-commerce expansion.

### 📊 Data Sources
- **Primary**: MoSPI Household Consumption Expenditure Survey (HCES 2022-23)
- **Supporting**: Census 2011 data for household size proxies

### 🧪 Hypotheses
1. **H1**: Smaller household sizes correlate with higher online purchase adoption
2. **H2**: Family-heavy regions over-index on essentials/bulk; single-heavy on convenience
3. **H3**: Household structure impacts ecommerce adoption primarily with internet access

### 📁 Project Structure
```
├── data/               # Raw and processed datasets
├── notebooks/          # Jupyter notebooks for analysis
├── src/                # Python scripts for data processing
├── visualizations/     # Charts, maps, and dashboard
├── outputs/            # Product memo and decision slides
└── README.md
```

### 🚀 Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Download HCES data to `data/raw/`
3. Run analysis notebooks in sequence
4. Generate dashboard and outputs

### 📦 Deliverables
- Interactive dashboard (India map, charts)
- Product memo (2-3 pages)
- Product decision slide (1 page)

### ⚠️ Key Assumptions
- Household size used as proxy for bachelor/single vs family households
- Analysis focuses on correlation, not causality
- Uses only publicly available government data
