"""
Data Collection Module for HCES 2022-23 Analysis

This module provides utilities for:
1. Downloading HCES data from MoSPI
2. Cleaning and standardizing state names
3. Creating household size buckets
4. Validating data quality
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class DataCollector:
    """Handles data collection and initial processing for HCES analysis"""
    
    def __init__(self):
        self.state_name_mapping = self._get_state_name_mapping()
        
    def _get_state_name_mapping(self) -> Dict[str, str]:
        """Standardize state/UT names across datasets"""
        return {
            'Andaman & Nicobar Islands': 'Andaman and Nicobar Islands',
            'Andaman and Nicobar': 'Andaman and Nicobar Islands',
            'A & N Islands': 'Andaman and Nicobar Islands',
            'Dadra & Nagar Haveli and Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'D & N Haveli and Daman & Diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'Jammu & Kashmir': 'Jammu and Kashmir',
            'Delhi': 'NCT of Delhi',
            'Orissa': 'Odisha',
            'Pondicherry': 'Puducherry'
        }
    
    def standardize_state_name(self, state: str) -> str:
        """Standardize state/UT name"""
        if pd.isna(state):
            return state
        state_clean = state.strip()
        return self.state_name_mapping.get(state_clean, state_clean)
    
    def create_household_size_bucket(self, size: int) -> str:
        """Create household size buckets for analysis"""
        if pd.isna(size):
            return 'Unknown'
        if size == 1:
            return '1 (Single-person)'
        elif size in [2, 3]:
            return '2-3 (Small)'
        elif size in [4, 5]:
            return '4-5 (Medium)'
        else:
            return '6+ (Large)'
    
    def load_hces_data(self, filepath: str) -> pd.DataFrame:
        """
        Load HCES 2022-23 data
        
        Note: Since HCES 2022-23 data format may vary, this provides a template.
        Adjust column names based on actual data structure.
        """
        try:
            # Try multiple file formats
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath, encoding='utf-8')
            elif filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
            else:
                raise ValueError("Unsupported file format. Use CSV or Excel.")
            
            print(f"Loaded {len(df)} records from {filepath}")
            return df
        
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def get_hces_data_instructions(self) -> str:
        """Provide instructions for downloading HCES data"""
        instructions = """
        📥 DATA COLLECTION INSTRUCTIONS
        
        1. Visit MoSPI (Ministry of Statistics and Programme Implementation):
           URL: https://mospi.gov.in/ or https://www.mospi.gov.in/web/mospi/reports-publications
        
        2. Search for "Household Consumption Expenditure Survey 2022-23" or latest available
        
        3. Look for:
           - Unit Level Data (if available)
           - Summary Tables containing:
             * State/UT wise distribution
             * Household size information
             * Internet availability
             * Online purchase indicators
             * Category-wise expenditure
        
        4. Alternative sources:
           - Data.gov.in: https://data.gov.in/
           - NSSO (National Sample Survey Office) reports
           - State-wise fact sheets
        
        5. Required columns (exact names may vary):
           - State/UT identifier
           - Sector (Urban/Rural)
           - Household_Size or Family_Size
           - Internet_Access or similar
           - Online_Purchase indicator (binary or categorical)
           - Category-wise purchase flags (Food, Medicine, Consumables, etc.)
           - Sample_Weight or Multiplier (for representative estimates)
        
        6. Save data in: data/raw/hces_2022_23.csv or .xlsx
        
        📊 Expected Data Structure:
        - Each row = one household or aggregated statistics
        - Minimum 5000+ household records (survey sample)
        - State-level coverage for all 28 states + 8 UTs
        
        ⚠️ Data Availability Notes:
        - Full HCES 2022-23 unit-level data may have restricted access
        - Use published summary statistics if unit-level unavailable
        - Supplement with HCES 2011-12 if 2022-23 not fully released
        """
        return instructions


class DataCleaner:
    """Clean and validate HCES data"""
    
    def __init__(self, collector: DataCollector):
        self.collector = collector
    
    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all cleaning steps to raw data"""
        df_clean = df.copy()
        
        # Standardize state names
        if 'State' in df_clean.columns:
            df_clean['State_Standardized'] = df_clean['State'].apply(
                self.collector.standardize_state_name
            )
        
        # Create household size buckets
        if 'Household_Size' in df_clean.columns:
            df_clean['HH_Size_Bucket'] = df_clean['Household_Size'].apply(
                self.collector.create_household_size_bucket
            )
        
        # Standardize binary indicators
        binary_cols = ['Internet_Access', 'Online_Purchase', 'Urban']
        for col in binary_cols:
            if col in df_clean.columns:
                df_clean[col] = self._standardize_binary(df_clean[col])
        
        # Remove invalid records
        df_clean = self._remove_invalid_records(df_clean)
        
        print(f"Cleaned data: {len(df_clean)} records")
        return df_clean
    
    def _standardize_binary(self, series: pd.Series) -> pd.Series:
        """Convert various binary representations to 1/0"""
        mapping = {
            'Yes': 1, 'No': 0,
            'Y': 1, 'N': 0,
            'TRUE': 1, 'FALSE': 0,
            'True': 1, 'False': 0,
            1: 1, 0: 0
        }
        return series.map(mapping)
    
    def _remove_invalid_records(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove records with critical missing values"""
        critical_cols = ['State', 'Household_Size']
        available_critical = [col for col in critical_cols if col in df.columns]
        
        if available_critical:
            df_valid = df.dropna(subset=available_critical)
            print(f"Removed {len(df) - len(df_valid)} invalid records")
            return df_valid
        
        return df
    
    def generate_data_quality_report(self, df: pd.DataFrame) -> Dict:
        """Generate data quality metrics"""
        report = {
            'total_records': len(df),
            'missing_values': df.isnull().sum().to_dict(),
            'unique_states': df['State'].nunique() if 'State' in df.columns else 0,
            'date_range': 'HCES 2022-23',
            'key_columns_present': [col for col in [
                'State', 'Household_Size', 'Internet_Access', 'Online_Purchase'
            ] if col in df.columns]
        }
        return report


def create_sample_dataset() -> pd.DataFrame:
    """
    Create a realistic sample dataset for demonstration purposes
    
    This mimics HCES 2022-23 structure based on known patterns:
    - Higher online penetration in urban areas
    - Correlation between internet access and online purchases
    - Regional variations in household size
    """
    np.random.seed(42)
    
    states = [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
        'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand',
        'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur',
        'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
        'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura',
        'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
        'NCT of Delhi', 'Puducherry', 'Chandigarh', 'Goa',
        'Andaman and Nicobar Islands', 'Dadra and Nagar Haveli and Daman and Diu',
        'Jammu and Kashmir', 'Ladakh'
    ]
    
    # Regional development indicators (higher = more developed)
    state_development_index = {
        'Kerala': 0.9, 'Goa': 0.85, 'NCT of Delhi': 0.9, 'Chandigarh': 0.85,
        'Tamil Nadu': 0.8, 'Karnataka': 0.8, 'Maharashtra': 0.8, 'Telangana': 0.75,
        'Gujarat': 0.75, 'Haryana': 0.75, 'Punjab': 0.7, 'Himachal Pradesh': 0.7,
        'Uttarakhand': 0.65, 'Andhra Pradesh': 0.65, 'Sikkim': 0.65,
        'West Bengal': 0.6, 'Rajasthan': 0.55, 'Madhya Pradesh': 0.5,
        'Uttar Pradesh': 0.5, 'Bihar': 0.45, 'Jharkhand': 0.45, 'Odisha': 0.5,
        'Chhattisgarh': 0.5, 'Assam': 0.5, 'Manipur': 0.55, 'Meghalaya': 0.5,
        'Tripura': 0.5, 'Mizoram': 0.6, 'Nagaland': 0.5, 'Arunachal Pradesh': 0.45,
        'Puducherry': 0.75, 'Andaman and Nicobar Islands': 0.65,
        'Dadra and Nagar Haveli and Daman and Diu': 0.6,
        'Jammu and Kashmir': 0.55, 'Ladakh': 0.5
    }
    
    records = []
    household_id = 1
    
    for state in states[:28]:  # Use major states for sample
        dev_index = state_development_index.get(state, 0.5)
        
        # Generate households per state (proportional to population roughly)
        n_households = np.random.randint(200, 500)
        
        for _ in range(n_households):
            # Urban probability based on development
            is_urban = np.random.random() < (0.3 + dev_index * 0.3)
            
            # Household size: smaller in urban, developed areas
            if is_urban:
                hh_size = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8], 
                                          p=[0.15, 0.20, 0.25, 0.20, 0.12, 0.05, 0.02, 0.01])
            else:
                hh_size = np.random.choice([1, 2, 3, 4, 5, 6, 7, 8],
                                          p=[0.05, 0.10, 0.20, 0.25, 0.20, 0.12, 0.05, 0.03])
            
            # Internet access: higher in urban + developed
            internet_prob = 0.3 + (0.4 if is_urban else 0) + dev_index * 0.2
            has_internet = np.random.random() < internet_prob
            
            # Online purchase: depends heavily on internet + household size
            if has_internet:
                # Smaller households more likely to purchase online
                online_prob = 0.4 + (0.3 if hh_size <= 2 else 0) + dev_index * 0.2
            else:
                online_prob = 0.05  # Very low without internet
            
            made_online_purchase = np.random.random() < online_prob
            
            # Category-wise purchases (if made any online purchase)
            if made_online_purchase:
                # Single/small HH over-index on convenience
                food_online = np.random.random() < (0.7 if hh_size <= 2 else 0.5)
                medicine_online = np.random.random() < 0.4
                consumables_online = np.random.random() < (0.5 if hh_size >= 4 else 0.3)
                electronics_online = np.random.random() < 0.3
            else:
                food_online = medicine_online = consumables_online = electronics_online = False
            
            records.append({
                'Household_ID': household_id,
                'State': state,
                'Urban': 1 if is_urban else 0,
                'Household_Size': hh_size,
                'Internet_Access': 1 if has_internet else 0,
                'Online_Purchase': 1 if made_online_purchase else 0,
                'Online_Food': 1 if food_online else 0,
                'Online_Medicine': 1 if medicine_online else 0,
                'Online_Consumables': 1 if consumables_online else 0,
                'Online_Electronics': 1 if electronics_online else 0,
                'Sample_Weight': np.random.uniform(50, 200)  # Survey weight
            })
            
            household_id += 1
    
    df = pd.DataFrame(records)
    print(f"\n✅ Created sample dataset with {len(df)} household records")
    print(f"   States covered: {df['State'].nunique()}")
    print(f"   Online purchase rate: {df['Online_Purchase'].mean():.1%}")
    
    return df


if __name__ == "__main__":
    print("Data Collection Module initialized")
    print("\n" + "="*60)
    
    collector = DataCollector()
    print(collector.get_hces_data_instructions())
    
    print("\n" + "="*60)
    print("\n📊 Creating sample dataset for demonstration...")
    
    # Create and save sample data
    sample_df = create_sample_dataset()
    output_path = "../data/sample_hces_data.csv"
    sample_df.to_csv(output_path, index=False)
    print(f"\n💾 Sample data saved to: {output_path}")
