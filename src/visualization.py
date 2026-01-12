"""
Visualization Module for Household Structure & E-commerce Analysis

Creates:
1. India choropleth map showing online purchase penetration
2. Household size vs adoption charts
3. Category skew visualizations
4. Interactive dashboard components
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List


class IndiaMapVisualizer:
    """Create India state-level choropleth maps"""
    
    def __init__(self):
        self.india_geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        
    def create_penetration_map(self, state_data: pd.DataFrame, 
                              metric_col: str = 'Penetration_%',
                              title: str = 'Online Purchase Penetration by State') -> go.Figure:
        """
        Create India choropleth map showing penetration by state
        
        Args:
            state_data: DataFrame with 'State' and metric column
            metric_col: Column name for the metric to visualize
            title: Chart title
        """
        fig = px.choropleth(
            state_data,
            geojson=self.india_geojson_url,
            featureidkey='properties.ST_NM',
            locations='State',
            color=metric_col,
            color_continuous_scale='YlOrRd',
            hover_name='State',
            hover_data={metric_col: ':.1f'},
            title=title
        )
        
        fig.update_geos(
            visible=False,
            fitbounds="locations",
            center={"lat": 22, "lon": 79}
        )
        
        fig.update_layout(
            height=700,
            width=900,
            title_font_size=18,
            coloraxis_colorbar=dict(
                title=f"{metric_col}",
                ticksuffix="%"
            )
        )
        
        return fig


class HouseholdAdoptionVisualizer:
    """Create household size vs adoption visualizations"""
    
    @staticmethod
    def create_adoption_by_size_chart(penetration_df: pd.DataFrame,
                                     internet_split: bool = False) -> go.Figure:
        """
        Create bar chart showing online adoption by household size bucket
        
        Args:
            penetration_df: DataFrame with HH_Size_Bucket and Penetration_%
            internet_split: Whether to split by internet access
        """
        if not internet_split:
            fig = px.bar(
                penetration_df,
                x='HH_Size_Bucket',
                y='Penetration_%',
                title='Online Purchase Penetration by Household Size',
                labels={'HH_Size_Bucket': 'Household Size', 'Penetration_%': 'Penetration (%)'},
                color='Penetration_%',
                color_continuous_scale='Viridis',
                text='Penetration_%'
            )
            
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=500, width=800, showlegend=False)
            
        else:
            # Create grouped bar chart for internet access split
            fig = px.bar(
                penetration_df,
                x='HH_Size_Bucket',
                y='Penetration_%',
                color='Internet_Access',
                barmode='group',
                title='Online Purchase Penetration by Household Size and Internet Access',
                labels={'HH_Size_Bucket': 'Household Size', 'Penetration_%': 'Penetration (%)'},
                text='Penetration_%'
            )
            
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(height=500, width=900)
        
        return fig
    
    @staticmethod
    def create_scatter_with_trendline(df: pd.DataFrame) -> go.Figure:
        """
        Create scatter plot with trendline: household size vs online purchase probability
        """
        # Aggregate by household size
        agg_df = df.groupby('Household_Size').agg({
            'Online_Purchase': 'mean',
            'Household_ID': 'count'
        }).reset_index()
        
        agg_df['Penetration_%'] = agg_df['Online_Purchase'] * 100
        
        fig = px.scatter(
            agg_df,
            x='Household_Size',
            y='Penetration_%',
            size='Household_ID',
            trendline='ols',
            title='Household Size vs Online Purchase Adoption (with Trendline)',
            labels={'Household_Size': 'Household Size', 'Penetration_%': 'Online Purchase Rate (%)'},
            hover_data={'Household_ID': True}
        )
        
        fig.update_layout(height=500, width=800)
        
        return fig


class CategorySkewVisualizer:
    """Visualize category preferences across household types"""
    
    @staticmethod
    def create_category_heatmap(category_skew: Dict) -> go.Figure:
        """
        Create heatmap showing Category Skew Index
        
        Args:
            category_skew: Dict with category names as keys and {HH_Type: skew_index} as values
        """
        # Prepare data for heatmap
        categories = list(category_skew.keys())
        hh_types = list(list(category_skew.values())[0].keys())
        
        z_data = []
        for hh_type in hh_types:
            row = [category_skew[cat].get(hh_type, 1.0) for cat in categories]
            z_data.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=categories,
            y=hh_types,
            colorscale='RdYlGn',
            zmid=1.0,
            text=[[f'{val:.2f}x' for val in row] for row in z_data],
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title='Skew Index')
        ))
        
        fig.update_layout(
            title='Category Skew Index: Over/Under-indexing by Household Type',
            xaxis_title='Category',
            yaxis_title='Household Type',
            height=400,
            width=900
        )
        
        return fig
    
    @staticmethod
    def create_category_comparison_bars(category_penetration: Dict) -> go.Figure:
        """
        Create grouped bar chart comparing category penetration across household types
        """
        # Reshape data
        data_rows = []
        for category, hh_type_data in category_penetration.items():
            for hh_type, penetration in hh_type_data.items():
                data_rows.append({
                    'Category': category.replace('Online_', ''),
                    'Household_Type': hh_type,
                    'Penetration_%': penetration * 100
                })
        
        df_plot = pd.DataFrame(data_rows)
        
        fig = px.bar(
            df_plot,
            x='Category',
            y='Penetration_%',
            color='Household_Type',
            barmode='group',
            title='Category-wise Online Purchase Penetration by Household Type',
            labels={'Penetration_%': 'Penetration (%)', 'Category': 'Product Category'},
            text='Penetration_%'
        )
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500, width=900)
        
        return fig


class DashboardBuilder:
    """Build interactive dashboard with all visualizations"""
    
    def __init__(self, analysis_results: Dict):
        self.results = analysis_results
        self.map_viz = IndiaMapVisualizer()
        self.hh_viz = HouseholdAdoptionVisualizer()
        self.cat_viz = CategorySkewVisualizer()
    
    def build_full_dashboard(self) -> Dict[str, go.Figure]:
        """
        Build all dashboard components
        
        Returns:
            Dictionary of figure names to Plotly figures
        """
        figures = {}
        
        # 1. India penetration map
        if 'state_penetration' in self.results:
            figures['india_map'] = self.map_viz.create_penetration_map(
                self.results['state_penetration']
            )
        
        # 2. Household size adoption chart
        if 'household_size_penetration' in self.results:
            figures['hh_size_adoption'] = self.hh_viz.create_adoption_by_size_chart(
                self.results['household_size_penetration']
            )
        
        # 3. Category skew heatmap
        if 'h2' in self.results and 'category_skew_index' in self.results['h2']:
            figures['category_skew'] = self.cat_viz.create_category_heatmap(
                self.results['h2']['category_skew_index']
            )
        
        # 4. Category comparison bars
        if 'h2' in self.results and 'category_penetration' in self.results['h2']:
            figures['category_comparison'] = self.cat_viz.create_category_comparison_bars(
                self.results['h2']['category_penetration']
            )
        
        return figures
    
    def save_all_figures(self, output_dir: str = '../visualizations'):
        """Save all figures to HTML (PNG export disabled to prevent hanging)"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        figures = self.build_full_dashboard()
        
        for name, fig in figures.items():
            # Save as HTML (interactive) - this is the main deliverable
            html_path = f"{output_dir}/{name}.html"
            fig.write_html(html_path)
            print(f"✅ Saved {html_path}")


def create_executive_summary_viz(analysis_results: Dict) -> go.Figure:
    """
    Create single-page executive summary visualization with key metrics
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Overall Penetration',
            'Top 5 States',
            'Household Size Effect',
            'Internet Access Impact'
        ),
        specs=[[{'type': 'indicator'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # 1. Overall penetration indicator
    overall_pen = analysis_results['overall_penetration']['Penetration_%'].values[0]
    fig.add_trace(
        go.Indicator(
            mode='number+gauge',
            value=overall_pen,
            title={'text': 'National Avg'},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': 'darkblue'}},
            number={'suffix': '%'}
        ),
        row=1, col=1
    )
    
    # 2. Top 5 states
    top_states = analysis_results['state_penetration'].nlargest(5, 'Penetration_%')
    fig.add_trace(
        go.Bar(x=top_states['State'], y=top_states['Penetration_%'],
               marker_color='steelblue'),
        row=1, col=2
    )
    
    # 3. Household size effect
    hh_size_data = analysis_results['household_size_penetration']
    fig.add_trace(
        go.Bar(x=hh_size_data['HH_Size_Bucket'], y=hh_size_data['Penetration_%'],
               marker_color='coral'),
        row=2, col=1
    )
    
    # 4. Internet access impact
    internet_data = analysis_results['internet_penetration']
    fig.add_trace(
        go.Bar(x=internet_data['Internet_Access'].map({0: 'No Internet', 1: 'Has Internet'}),
               y=internet_data['Penetration_%'],
               marker_color='mediumseagreen'),
        row=2, col=2
    )
    
    fig.update_layout(
        title_text="Quick-Commerce Product Discovery: Executive Summary",
        showlegend=False,
        height=800,
        width=1200
    )
    
    return fig


if __name__ == "__main__":
    print("Visualization Module initialized")
    print("Import and use with analysis results to generate charts and dashboards")
