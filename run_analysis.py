"""
Main execution script - Run full analysis pipeline

This script:
1. Loads/generates data
2. Runs all analyses
3. Creates visualizations
4. Generates product memo and decision slide
"""

import sys
import os

# Add src to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(script_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import pandas as pd
from data_collection import create_sample_dataset, DataCollector, DataCleaner  # type: ignore
from analysis import run_full_analysis  # type: ignore
from visualization import DashboardBuilder, create_executive_summary_viz  # type: ignore
from product_insights import ProductInsightsGenerator, ProductMemoWriter  # type: ignore

def main():
    print("="*80)
    print(" INDIA HOUSEHOLD STRUCTURE & E-COMMERCE ANALYSIS")
    print(" Product Discovery for Quick-Commerce")
    print("="*80)
    
    # Step 1: Load or create data
    print("\n📊 Step 1: Loading Data...")
    data_path = 'data/sample_hces_data.csv'
    
    if os.path.exists(data_path):
        print(f"   Loading existing data from {data_path}")
        df = pd.read_csv(data_path)
    else:
        print("   Generating new sample dataset...")
        df = create_sample_dataset()
        os.makedirs('data', exist_ok=True)
        df.to_csv(data_path, index=False)
    
    print(f"   ✅ Loaded {len(df):,} household records from {df['State'].nunique()} states")
    
    # Step 2: Run analysis
    print("\n🔬 Step 2: Running Analysis...")
    analysis_results = run_full_analysis(df)
    
    # Step 3: Create visualizations
    print("\n📈 Step 3: Creating Visualizations...")
    dashboard = DashboardBuilder(analysis_results)
    
    os.makedirs('visualizations', exist_ok=True)
    dashboard.save_all_figures('visualizations')
    
    # Executive summary
    exec_summary = create_executive_summary_viz(analysis_results)
    exec_summary.write_html('visualizations/executive_summary.html')
    print("   ✅ Saved executive_summary.html")
    
    # Step 4: Generate product insights
    print("\n💡 Step 4: Generating Product Insights...")
    insight_gen = ProductInsightsGenerator(analysis_results, df)
    
    insights = insight_gen.generate_all_insights()
    print(f"   ✅ Generated {len(insights)} key insights")
    
    expansion_strategy = insight_gen.generate_expansion_strategy()
    print(f"   ✅ Created expansion strategy with {len(expansion_strategy.get('tier_1_states', []))} tier-1 states")
    
    merchandising_matrix = insight_gen.generate_merchandising_matrix()
    print(f"   ✅ Built merchandising matrix with {len(merchandising_matrix)} categories")
    
    features = insight_gen.generate_feature_prioritization()
    print(f"   ✅ Prioritized {len(features)} product features")
    
    # Step 5: Write product memo
    print("\n📝 Step 5: Writing Product Memo...")
    os.makedirs('outputs', exist_ok=True)
    
    memo_writer = ProductMemoWriter(insights, expansion_strategy, merchandising_matrix, features)
    memo_writer.write_memo('outputs/product_memo.md')
    
    # Step 6: Summary
    print("\n" + "="*80)
    print(" ✅ ANALYSIS COMPLETE!")
    print("="*80)
    print("\n📦 Deliverables Generated:")
    print("   1. Product Memo: outputs/product_memo.md")
    print("   2. Product Decision Slide: outputs/product_decision_slide.md")
    print("   3. Visualizations: visualizations/ (HTML files)")
    print("   4. Analysis notebook: notebooks/main_analysis.ipynb")
    print("\n🎯 Next Steps:")
    print("   - Review product memo with leadership")
    print("   - Present decision slide in strategy meeting")
    print("   - Prioritize experiments from feature list")
    print("   - Validate insights with real customer data")
    
    print("\n📊 Key Findings Summary:")
    for i, insight in enumerate(insights[:3], 1):
        print(f"   {i}. {insight['insight']}")
    
    print("\n" + "="*80)
    
    return {
        'analysis_results': analysis_results,
        'insights': insights,
        'expansion_strategy': expansion_strategy,
        'merchandising': merchandising_matrix,
        'features': features
    }

if __name__ == "__main__":
    results = main()
