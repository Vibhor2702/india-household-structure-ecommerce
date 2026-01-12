"""
Analysis Module for Household Structure & E-commerce Study

Implements:
- Online Purchase Penetration calculations
- Hypothesis testing (H1, H2, H3)
- Category Skew Index
- Statistical modeling
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class PenetrationAnalyzer:
    """Calculate online purchase penetration metrics"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.weighted = 'Sample_Weight' in df.columns
    
    def calculate_penetration(self, 
                            groupby_cols: List[str] | None = None,
                            weight_col: str = 'Sample_Weight') -> pd.DataFrame:
        """
        Calculate online purchase penetration
        
        Penetration = (Households with ≥1 online purchase) / (Total households)
        """
        if groupby_cols is None:
            # Overall penetration
            if self.weighted:
                total_weight = self.df[weight_col].sum()
                online_weight = self.df[self.df['Online_Purchase'] == 1][weight_col].sum()
                penetration = online_weight / total_weight
            else:
                penetration = self.df['Online_Purchase'].mean()
            
            return pd.DataFrame({
                'Group': ['Overall'],
                'Penetration_%': [penetration * 100],
                'Sample_Size': [len(self.df)]
            })
        
        # Grouped penetration
        results = []
        for name, group in self.df.groupby(groupby_cols):
            if self.weighted:
                total_weight = group[weight_col].sum()
                online_weight = group[group['Online_Purchase'] == 1][weight_col].sum()
                penetration = online_weight / total_weight if total_weight > 0 else 0
            else:
                penetration = group['Online_Purchase'].mean()
            
            results.append({
                **dict(zip(groupby_cols, name if isinstance(name, tuple) else [name])),
                'Penetration_%': penetration * 100,
                'Sample_Size': len(group)
            })
        
        return pd.DataFrame(results)
    
    def state_level_penetration(self) -> pd.DataFrame:
        """Calculate penetration by state"""
        return self.calculate_penetration(groupby_cols=['State'])
    
    def household_size_penetration(self) -> pd.DataFrame:
        """Calculate penetration by household size bucket"""
        # Create buckets if not exists
        if 'HH_Size_Bucket' not in self.df.columns:
            self.df['HH_Size_Bucket'] = self.df['Household_Size'].apply(
                lambda x: self._bucket_hh_size(x)
            )
        
        return self.calculate_penetration(groupby_cols=['HH_Size_Bucket'])
    
    def urban_rural_penetration(self) -> pd.DataFrame:
        """Calculate penetration by urban/rural"""
        if 'Urban' not in self.df.columns:
            return pd.DataFrame()
        
        return self.calculate_penetration(groupby_cols=['Urban'])
    
    def internet_penetration(self) -> pd.DataFrame:
        """Calculate penetration by internet availability"""
        if 'Internet_Access' not in self.df.columns:
            return pd.DataFrame()
        
        return self.calculate_penetration(groupby_cols=['Internet_Access'])
    
    @staticmethod
    def _bucket_hh_size(size: int) -> str:
        """Create household size bucket"""
        if size == 1:
            return '1 (Single-person)'
        elif size in [2, 3]:
            return '2-3 (Small)'
        elif size in [4, 5]:
            return '4-5 (Medium)'
        else:
            return '6+ (Large)'


class HypothesisTester:
    """Test the three main hypotheses"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def test_h1_household_size_adoption(self) -> Dict:
        """
        H1: Smaller household sizes correlate with higher online purchase adoption
        
        Tests:
        1. Correlation between household size and online purchase
        2. Chi-square test for independence
        3. Trend analysis across size buckets
        """
        # Correlation
        if 'Household_Size' in self.df.columns and 'Online_Purchase' in self.df.columns:
            correlation = self.df[['Household_Size', 'Online_Purchase']].corr().iloc[0, 1]
            
            # Statistical significance
            n = len(self.df)
            corr_val = float(correlation)  # type: ignore
            t_stat = corr_val * np.sqrt(n - 2) / np.sqrt(1 - corr_val**2)
            p_value = float(2 * (1 - stats.t.cdf(abs(t_stat), n - 2)))
        else:
            correlation, p_value = np.nan, np.nan
        
        # Penetration by size bucket
        analyzer = PenetrationAnalyzer(self.df)
        penetration_by_size = analyzer.household_size_penetration()
        
        # Chi-square test
        if 'Household_Size' in self.df.columns and 'Online_Purchase' in self.df.columns:
            contingency = pd.crosstab(self.df['Household_Size'], self.df['Online_Purchase'])
            chi2, chi_p, _, _ = stats.chi2_contingency(contingency)
        else:
            chi2, chi_p = np.nan, np.nan
        
        # Prepare return values
        corr_val = float(correlation) if not pd.isna(correlation) else np.nan  # type: ignore
        p_val = float(p_value) if not pd.isna(p_value) else np.nan  # type: ignore
        
        return {
            'correlation': corr_val,
            'correlation_p_value': p_val,
            'chi_square': float(chi2) if not pd.isna(chi2) else np.nan,  # type: ignore
            'chi_square_p_value': float(chi_p) if not pd.isna(chi_p) else np.nan,  # type: ignore
            'penetration_by_size': penetration_by_size,
            'conclusion': self._interpret_h1(corr_val, p_val, penetration_by_size)
        }
    
    def test_h2_category_differences(self) -> Dict:
        """
        H2: Family-heavy regions over-index on essentials/bulk,
            Single-heavy regions over-index on convenience
        """
        category_cols = [col for col in self.df.columns if col.startswith('Online_')]
        if not category_cols or 'Household_Size' not in self.df.columns:
            return {'error': 'Category data not available'}
        
        # Define household type
        self.df['HH_Type'] = self.df['Household_Size'].apply(
            lambda x: 'Single/Small' if x <= 2 else 'Family'
        )
        
        # Calculate category penetration by household type
        category_penetration = {}
        for cat in category_cols:
            if cat != 'Online_Purchase':
                cat_penetration = self.df[self.df[cat] == 1].groupby('HH_Type').size() / self.df.groupby('HH_Type').size()
                category_penetration[cat] = cat_penetration.to_dict()
        
        # Calculate Category Skew Index
        skew_indices = self._calculate_category_skew(category_penetration)
        
        return {
            'category_penetration': category_penetration,
            'category_skew_index': skew_indices,
            'conclusion': self._interpret_h2(skew_indices)
        }
    
    def test_h3_internet_mediation(self) -> Dict:
        """
        H3: Household structure impacts e-commerce adoption primarily when
            internet access is present
        """
        if 'Internet_Access' not in self.df.columns:
            return {'error': 'Internet access data not available'}
        
        # Analyze household size effect WITH and WITHOUT internet
        with_internet = self.df[self.df['Internet_Access'] == 1]
        without_internet = self.df[self.df['Internet_Access'] == 0]
        
        # Correlation for each group
        corr_with = with_internet[['Household_Size', 'Online_Purchase']].corr().iloc[0, 1] if len(with_internet) > 0 else np.nan
        corr_without = without_internet[['Household_Size', 'Online_Purchase']].corr().iloc[0, 1] if len(without_internet) > 0 else np.nan
        
        # Convert to float
        corr_with_val = float(corr_with) if not pd.isna(corr_with) else np.nan  # type: ignore
        corr_without_val = float(corr_without) if not pd.isna(corr_without) else np.nan  # type: ignore
        
        # Penetration by size for each internet group
        results_with = []
        results_without = []
        
        for size_bucket in ['1 (Single-person)', '2-3 (Small)', '4-5 (Medium)', '6+ (Large)']:
            # With internet
            subset_with = with_internet[with_internet['Household_Size'].apply(
                lambda x: PenetrationAnalyzer._bucket_hh_size(x)) == size_bucket]
            if len(subset_with) > 0:
                pen_with = subset_with['Online_Purchase'].mean() * 100
                results_with.append({'HH_Size': size_bucket, 'Penetration': pen_with})
            
            # Without internet
            subset_without = without_internet[without_internet['Household_Size'].apply(
                lambda x: PenetrationAnalyzer._bucket_hh_size(x)) == size_bucket]
            if len(subset_without) > 0:
                pen_without = subset_without['Online_Purchase'].mean() * 100
                results_without.append({'HH_Size': size_bucket, 'Penetration': pen_without})
        
        return {
            'correlation_with_internet': corr_with_val,
            'correlation_without_internet': corr_without_val,
            'penetration_with_internet': pd.DataFrame(results_with),
            'penetration_without_internet': pd.DataFrame(results_without),
            'conclusion': self._interpret_h3(corr_with_val, corr_without_val)
        }
    
    def _calculate_category_skew(self, category_penetration: Dict) -> Dict:
        """
        Category Skew Index = (Category share in group) / (National average)
        > 1.0 = over-indexing
        < 1.0 = under-indexing
        """
        skew_indices = {}
        for category, group_data in category_penetration.items():
            national_avg = np.mean(list(group_data.values()))
            skew_indices[category] = {
                group: (rate / national_avg if national_avg > 0 else 1.0)
                for group, rate in group_data.items()
            }
        return skew_indices
    
    def _interpret_h1(self, correlation: float, p_value: float, 
                     penetration_df: pd.DataFrame) -> str:
        """Generate interpretation for H1"""
        if pd.isna(correlation):
            return "Insufficient data to test H1"
        
        if p_value < 0.05:
            if correlation < -0.1:
                return f"✅ H1 SUPPORTED: Negative correlation ({correlation:.3f}, p={p_value:.4f}). Smaller households show higher online purchase adoption."
            elif correlation > 0.1:
                return f"❌ H1 REJECTED: Positive correlation ({correlation:.3f}, p={p_value:.4f}). Larger households show higher adoption."
            else:
                return f"⚠️ H1 WEAK: Correlation exists ({correlation:.3f}, p={p_value:.4f}) but effect size is small."
        else:
            return f"❌ H1 NOT SUPPORTED: No significant correlation ({correlation:.3f}, p={p_value:.4f})."
    
    def _interpret_h2(self, skew_indices: Dict) -> str:
        """Generate interpretation for H2"""
        if not skew_indices:
            return "Insufficient category data to test H2"
        
        interpretations = []
        for category, indices in skew_indices.items():
            single_skew = indices.get('Single/Small', 1.0)
            family_skew = indices.get('Family', 1.0)
            
            if 'Consumables' in category or 'Grocery' in category:
                if family_skew > 1.1:
                    interpretations.append(f"✅ {category}: Family over-indexes ({family_skew:.2f}x)")
            elif 'Food' in category and 'Ready' not in category:
                if single_skew > 1.1:
                    interpretations.append(f"✅ {category}: Single/Small over-indexes ({single_skew:.2f}x)")
        
        return "\n".join(interpretations) if interpretations else "⚠️ H2: Mixed results"
    
    def _interpret_h3(self, corr_with: float, corr_without: float) -> str:
        """Generate interpretation for H3"""
        if pd.isna(corr_with) or pd.isna(corr_without):
            return "Insufficient data to test H3"
        
        if abs(corr_with) > abs(corr_without) * 1.5:
            return f"✅ H3 SUPPORTED: Household size effect stronger with internet (r={corr_with:.3f}) vs without (r={corr_without:.3f})"
        elif abs(corr_without) > abs(corr_with):
            return f"❌ H3 NOT SUPPORTED: Effect not mediated by internet access"
        else:
            return f"⚠️ H3 INCONCLUSIVE: Similar effects with (r={corr_with:.3f}) and without (r={corr_without:.3f}) internet"


class StatisticalModeler:
    """Optional logistic regression for deeper insights"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
    
    def fit_logistic_model(self) -> Dict:
        """
        Fit logistic regression: P(Online Purchase) ~ household_size + internet + urban + state
        
        Focus: Interpretability over prediction
        """
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
        
        # Prepare features
        feature_cols = []
        if 'Household_Size' in self.df.columns:
            feature_cols.append('Household_Size')
        if 'Internet_Access' in self.df.columns:
            feature_cols.append('Internet_Access')
        if 'Urban' in self.df.columns:
            feature_cols.append('Urban')
        
        if not feature_cols or 'Online_Purchase' not in self.df.columns:
            return {'error': 'Insufficient features for modeling'}
        
        # Remove NaN
        model_df = self.df[feature_cols + ['Online_Purchase']].dropna()
        
        X = model_df[feature_cols]
        y = model_df['Online_Purchase']
        
        # Standardize for interpretability
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Fit model
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_scaled, y)
        
        # Extract coefficients
        coefficients = dict(zip(feature_cols, model.coef_[0]))
        
        # Calculate odds ratios (more interpretable)
        odds_ratios = {feat: np.exp(coef) for feat, coef in coefficients.items()}
        
        # Model performance
        accuracy = model.score(X_scaled, y)
        
        return {
            'coefficients': coefficients,
            'odds_ratios': odds_ratios,
            'accuracy': accuracy,
            'n_samples': len(model_df),
            'interpretation': self._interpret_model(odds_ratios, feature_cols)
        }
    
    def _interpret_model(self, odds_ratios: Dict, features: List[str]) -> str:
        """Generate plain English interpretation"""
        interpretations = []
        
        for feat, or_value in odds_ratios.items():
            if feat == 'Household_Size':
                if or_value < 1:
                    change = (1 - or_value) * 100
                    interpretations.append(
                        f"Each additional household member → {change:.1f}% lower odds of online purchase"
                    )
                else:
                    change = (or_value - 1) * 100
                    interpretations.append(
                        f"Each additional household member → {change:.1f}% higher odds of online purchase"
                    )
            
            elif feat == 'Internet_Access':
                if or_value > 1:
                    change = (or_value - 1) * 100
                    interpretations.append(
                        f"Internet access → {change:.1f}% higher odds of online purchase"
                    )
            
            elif feat == 'Urban':
                if or_value > 1:
                    change = (or_value - 1) * 100
                    interpretations.append(
                        f"Urban location → {change:.1f}% higher odds of online purchase"
                    )
        
        return "\n".join(interpretations)


def run_full_analysis(df: pd.DataFrame) -> Dict:
    """Run all analyses and return comprehensive results"""
    
    print("🔬 Running Comprehensive Analysis...")
    print("=" * 60)
    
    results = {}
    
    # 1. Penetration Analysis
    print("\n📊 1. Calculating Penetration Metrics...")
    analyzer = PenetrationAnalyzer(df)
    results['overall_penetration'] = analyzer.calculate_penetration()
    results['state_penetration'] = analyzer.state_level_penetration()
    results['household_size_penetration'] = analyzer.household_size_penetration()
    results['urban_rural_penetration'] = analyzer.urban_rural_penetration()
    results['internet_penetration'] = analyzer.internet_penetration()
    
    print(f"   ✓ Overall penetration: {results['overall_penetration']['Penetration_%'].values[0]:.1f}%")
    
    # 2. Hypothesis Testing
    print("\n🧪 2. Testing Hypotheses...")
    tester = HypothesisTester(df)
    
    print("   Testing H1: Household Size vs Adoption...")
    results['h1'] = tester.test_h1_household_size_adoption()
    print(f"   {results['h1']['conclusion']}")
    
    print("   Testing H2: Category Differences...")
    results['h2'] = tester.test_h2_category_differences()
    if 'conclusion' in results['h2']:
        print(f"   {results['h2']['conclusion']}")
    
    print("   Testing H3: Internet Mediation...")
    results['h3'] = tester.test_h3_internet_mediation()
    if 'conclusion' in results['h3']:
        print(f"   {results['h3']['conclusion']}")
    
    # 3. Statistical Modeling
    print("\n📈 3. Fitting Logistic Model...")
    modeler = StatisticalModeler(df)
    results['model'] = modeler.fit_logistic_model()
    if 'interpretation' in results['model']:
        print(f"   Model Accuracy: {results['model']['accuracy']:.1%}")
        print(f"   {results['model']['interpretation']}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis Complete!")
    
    return results


if __name__ == "__main__":
    print("Analysis Module initialized")
    print("Import this module and use run_full_analysis(df) to execute all analyses")
