# 🚀 Quick Start Guide
## India Household Structure & E-commerce Analysis

This guide will help you run the complete product discovery analysis in under 10 minutes.

---

## 📋 Prerequisites

### Required Software
- Python 3.8+ ([Download](https://www.python.org/downloads/))
- Jupyter Notebook or VS Code with Jupyter extension
- Git (for cloning)

### System Requirements
- 4GB RAM minimum
- 500MB free disk space
- Internet connection (for installing packages)

---

## ⚡ Quick Start (3 Methods)

### Method 1: Run Everything (Recommended)

```bash
# Navigate to project directory
cd c:\Users\versu\Github\india-household-structure-ecommerce

# Install dependencies
pip install -r requirements.txt

# Run full analysis pipeline
python run_analysis.py
```

**Output:** All deliverables generated in `outputs/` and `visualizations/` folders

---

### Method 2: Interactive Notebook

```bash
# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter notebook notebooks/main_analysis.ipynb
```

**Then:** Run all cells sequentially (`Cell > Run All`)

---

### Method 3: Step-by-Step Modules

```python
# In Python console or Jupyter
import sys
sys.path.append('src')

# Step 1: Generate data
from data_collection import create_sample_dataset
df = create_sample_dataset()

# Step 2: Run analysis
from analysis import run_full_analysis
results = run_full_analysis(df)

# Step 3: Generate insights
from product_insights import ProductInsightsGenerator
insight_gen = ProductInsightsGenerator(results, df)
insights = insight_gen.generate_all_insights()

# Display insights
for i, insight in enumerate(insights, 1):
    print(f"\nInsight {i}: {insight['insight']}")
    print(f"Action: {insight['product_action']}")
```

---

## 📦 What Gets Generated

After running the analysis, you'll find:

### 1. **Data Files** (`data/`)
- `sample_hces_data.csv` - Simulated HCES 2022-23 household data (~10k records)

### 2. **Analysis Outputs** (`outputs/`)
- `product_memo.md` - **2-3 page product discovery memo**
  - Problem framing
  - 5 key insights with product implications
  - Expansion strategy
  - Feature prioritization
  - Limitations and next steps

- `product_decision_slide.md` - **1-page executive decision slide**
  - Top 3 immediate actions
  - Expected business impact
  - Expansion sequencing
  - Key experiments
  - Resource allocation recommendations

### 3. **Visualizations** (`visualizations/`)
- `india_map.html` - Interactive choropleth map of online purchase penetration by state
- `hh_size_adoption.html` - Bar chart: household size vs adoption
- `category_skew.html` - Heatmap: category preferences by household type
- `category_comparison.html` - Grouped bar chart: category-wise penetration
- `executive_summary.html` - 4-panel dashboard with key metrics

### 4. **Analysis Notebook** (`notebooks/`)
- `main_analysis.ipynb` - Complete interactive analysis with all code and visualizations

---

## 🔍 Understanding the Analysis

### Core Research Questions

1. **Q1:** Do smaller households → higher online purchase adoption?
   - **Metric:** Correlation between household size and online purchase rate
   - **Test:** H1 hypothesis using chi-square and correlation analysis

2. **Q2:** Do category preferences differ by household type?
   - **Metric:** Category Skew Index (>1.0 = over-indexing)
   - **Test:** H2 hypothesis comparing single vs family households

3. **Q3:** Does internet access mediate household effects?
   - **Metric:** Adoption gap with/without internet
   - **Test:** H3 hypothesis using stratified analysis

### Key Metrics Defined

**Online Purchase Penetration (%)**
```
= (Households with ≥1 online purchase) / (Total households) × 100
```

**Category Skew Index**
```
= (Category's share in segment) / (National average)

> 1.2 = Strong over-indexing
0.8-1.2 = Neutral
< 0.8 = Under-indexing
```

---

## 📊 Interpreting Results

### Sample Output Interpretation

If you see:
```
H1 SUPPORTED: Negative correlation (-0.25, p=0.001)
Smaller households show higher online purchase adoption.
```

**This means:**
- Statistically significant relationship (p < 0.05)
- Each additional household member → ~25% lower likelihood of online purchase
- Product implication: Target bachelor/single-person neighborhoods

### Key Insights Format

Each insight follows: **Insight → Implication → Metric Impact → Action**

**Example:**
- **Insight:** Single households show 30% higher adoption
- **Implication:** Prioritize expansion in bachelor-heavy areas
- **Metric Impact:** Estimated 20-30% higher conversion rates
- **Action:** Launch "Quick Singles" category in 5 pilot neighborhoods

---

## 🎯 Using the Deliverables

### For Product Managers
1. **Read:** `product_memo.md` (15 min)
2. **Present:** `product_decision_slide.md` to leadership
3. **Prioritize:** Top 3 recommended features
4. **Experiment:** Run suggested A/B tests

### For Analysts
1. **Explore:** `main_analysis.ipynb` for detailed analysis
2. **Customize:** Modify hypothesis tests in `src/analysis.py`
3. **Extend:** Add new metrics or visualizations
4. **Validate:** Replace sample data with real HCES data

### For Executives
1. **Review:** `product_decision_slide.md` (5 min read)
2. **Decide:** Approve recommended strategic pivots
3. **Allocate:** Adjust resource distribution per recommendations
4. **Track:** Monitor suggested KPIs quarterly

---

## 🔧 Customization Guide

### Replace Sample Data with Real HCES Data

1. Download HCES 2022-23 from [MoSPI](https://mospi.gov.in/)
2. Save as `data/raw/hces_2022_23.csv`
3. Update column mappings in `src/data_collection.py`:

```python
# Adjust these to match actual HCES columns
COLUMN_MAPPING = {
    'State_Name': 'State',
    'HH_Size': 'Household_Size',
    'Internet': 'Internet_Access',
    'Online_Purchase_Flag': 'Online_Purchase'
}
```

4. Re-run analysis: `python run_analysis.py`

### Add New Hypotheses

Edit `src/analysis.py`:

```python
def test_h4_income_effect(self) -> Dict:
    """H4: Income moderates household size effect"""
    # Add your custom analysis here
    pass
```

### Customize Visualizations

Edit `src/visualization.py`:

```python
# Change color schemes
fig.update_layout(
    color_continuous_scale='Viridis'  # Try: Blues, Reds, Greens
)

# Adjust map projection
fig.update_geos(
    projection_type='natural earth'  # Try: mercator, albers usa
)
```

---

## ⚠️ Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Plotly maps not showing

**Solution:**
```bash
pip install plotly kaleido
```

### Issue: Jupyter kernel crashes

**Solution:** Reduce data size or increase memory
```python
# In notebook, sample data
df = df.sample(frac=0.5, random_state=42)
```

### Issue: "State names don't match geojson"

**Solution:** Check state name standardization in `src/data_collection.py`
```python
# Add missing state mappings
self.state_name_mapping = {
    'Your_State_Name': 'Standard_Name'
}
```

---

## 📚 Additional Resources

### Data Sources
- **MoSPI HCES:** https://mospi.gov.in/
- **Census 2011:** https://censusindia.gov.in/
- **Data.gov.in:** https://data.gov.in/

### Learning Materials
- **Product Discovery:** [Continuous Discovery Habits by Teresa Torres](https://www.producttalk.org/)
- **Data Analysis for PM:** [Lean Analytics by Alistair Croll](http://leananalyticsbook.com/)
- **Indian E-commerce:** [IBEF E-commerce Report](https://www.ibef.org/industry/ecommerce)

### Technical Documentation
- **Pandas:** https://pandas.pydata.org/docs/
- **Plotly:** https://plotly.com/python/
- **Scipy Stats:** https://docs.scipy.org/doc/scipy/reference/stats.html

---

## 🤝 Contributing

Found an issue or have a suggestion?

1. **Data Issues:** Check `data/` folder and regenerate
2. **Analysis Bugs:** Review `src/analysis.py` logic
3. **Visualization Errors:** Inspect `src/visualization.py`
4. **Feature Requests:** Document in project README

---

## 📖 Project Structure Reference

```
india-household-structure-ecommerce/
│
├── data/
│   ├── sample_hces_data.csv          # Generated sample data
│   └── raw/                           # Place real HCES data here
│
├── src/
│   ├── data_collection.py            # Data loading & cleaning
│   ├── analysis.py                   # Hypothesis testing & metrics
│   ├── visualization.py              # Charts & dashboards
│   └── product_insights.py           # Insights generation
│
├── notebooks/
│   └── main_analysis.ipynb           # Interactive analysis notebook
│
├── outputs/
│   ├── product_memo.md               # 2-3 page product memo
│   └── product_decision_slide.md     # 1-page decision slide
│
├── visualizations/
│   ├── india_map.html                # State-level penetration map
│   ├── hh_size_adoption.html         # Household size charts
│   ├── category_skew.html            # Category heatmap
│   └── executive_summary.html        # Executive dashboard
│
├── run_analysis.py                   # Main execution script
├── requirements.txt                  # Python dependencies
└── README.md                         # Project overview
```

---

## ✅ Success Checklist

Before presenting your analysis, ensure:

- [ ] All visualizations generated successfully
- [ ] Product memo reads professionally (no code artifacts)
- [ ] Decision slide fits on one page
- [ ] Top 3 insights are business-actionable (not academic)
- [ ] Expansion strategy backed by data
- [ ] Feature prioritization includes effort estimates
- [ ] Limitations section acknowledges data constraints
- [ ] Next steps are concrete with timelines

---

## 🎓 Interview Tips (If Using for PM Interviews)

### Do's ✅
- Lead with business impact, not methodology
- Translate every insight into product decisions
- Acknowledge limitations upfront
- Sequence recommendations (now/next/later)
- Tie metrics to P&L impact

### Don'ts ❌
- Don't over-explain statistical methods
- Don't claim causality from correlation
- Don't propose all-at-once rollout
- Don't ignore unit economics
- Don't forget the "so what?"

### Sample Presentation Flow (15 min)
1. **Problem** (2 min): Why household structure matters for quick-commerce
2. **Approach** (1 min): Data + 3 hypotheses
3. **Insights** (7 min): Top 5 findings with product implications
4. **Recommendations** (3 min): Decision slide walkthrough
5. **Q&A** (2 min): Limitations, next steps, trade-offs

---

**Ready to run your analysis?**

```bash
python run_analysis.py
```

Then open `outputs/product_decision_slide.md` and start making product decisions! 🚀
