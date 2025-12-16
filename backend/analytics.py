"""Quantitative analytics engine for pairs trading and statistical analysis"""
import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.tsa.stattools import adfuller
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def is_plot_safe(series: pd.Series, min_points: int = 3) -> bool:
    """
    Check if a series is safe for visualization.
    Returns False if:
    - Length < min_points
    - All values are identical
    - Contains NaN or Inf
    """
    if len(series) < min_points:
        return False
    
    # Check for NaN or Inf
    if series.isna().any() or np.isinf(series).any():
        return False
    
    # Check if all values are identical (would cause domain issues)
    if series.nunique() <= 1:
        return False
    
    return True


class QuantAnalytics:
    """Compute quantitative trading analytics"""
    
    @staticmethod
    def compute_basic_stats(prices: pd.Series) -> Dict:
        """Compute basic price statistics"""
        if len(prices) < 2:
            return {}
        
        # Compute volatility safely
        vol = prices.pct_change().std()
        volatility = float(vol * np.sqrt(252)) if not pd.isna(vol) and np.isfinite(vol) else 0.0
            
        return {
            'mean': float(prices.mean()),
            'std': float(prices.std()),
            'min': float(prices.min()),
            'max': float(prices.max()),
            'last': float(prices.iloc[-1]),
            'volatility': volatility
        }
        
    @staticmethod
    def compute_ols_hedge_ratio(prices1: pd.Series, prices2: pd.Series) -> Tuple[float, float]:
        """
        Compute OLS-based hedge ratio between two price series
        Returns: (hedge_ratio, r_squared)
        """
        if len(prices1) < 10 or len(prices2) < 10:
            return 0.0, 0.0
            
        # Align series
        df = pd.DataFrame({'y': prices1, 'x': prices2}).dropna()
        
        if len(df) < 10:
            return 0.0, 0.0
            
        x = df['x'].values
        y = df['y'].values
        
        # OLS regression: y = beta * x + alpha
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return float(slope), float(r_value ** 2)
        
    @staticmethod
    def compute_spread(prices1: pd.Series, prices2: pd.Series, hedge_ratio: float) -> pd.Series:
        """
        Compute the spread: spread = prices1 - hedge_ratio * prices2
        """
        df = pd.DataFrame({'p1': prices1, 'p2': prices2}).dropna()
        spread = df['p1'] - hedge_ratio * df['p2']
        # Sanitize: remove Inf and NaN values
        spread = spread.replace([np.inf, -np.inf], np.nan).dropna()
        return spread
        
    @staticmethod
    def compute_rolling_zscore(series: pd.Series, window: int = 20) -> pd.Series:
        """Compute rolling z-score of a series"""
        if len(series) < window:
            return pd.Series(dtype=float)
            
        rolling_mean = series.rolling(window=window).mean()
        rolling_std = series.rolling(window=window).std()
        
        # Avoid division by zero: replace zero std with NaN
        rolling_std = rolling_std.replace(0, np.nan)
        
        zscore = (series - rolling_mean) / rolling_std
        # Remove Inf and NaN values for safe frontend consumption
        zscore = zscore.replace([np.inf, -np.inf], np.nan).dropna()
        return zscore
        
    @staticmethod
    def compute_rolling_correlation(prices1: pd.Series, prices2: pd.Series, window: int = 20) -> pd.Series:
        """Compute rolling correlation between two price series"""
        df = pd.DataFrame({'p1': prices1, 'p2': prices2}).dropna()
        
        if len(df) < window:
            return pd.Series(dtype=float)
            
        correlation = df['p1'].rolling(window=window).corr(df['p2'])
        return correlation.dropna()
        
    @staticmethod
    def augmented_dickey_fuller_test(series: pd.Series) -> Dict:
        """
        Perform Augmented Dickey-Fuller test for stationarity
        Returns test statistics
        """
        if len(series) < 12:
            return {'error': 'Insufficient data for ADF test'}
            
        try:
            result = adfuller(series.dropna(), autolag='AIC')
            
            return {
                'adf_statistic': float(result[0]),
                'p_value': float(result[1]),
                'used_lag': int(result[2]),
                'n_observations': int(result[3]),
                'critical_values': {
                    '1%': float(result[4]['1%']),
                    '5%': float(result[4]['5%']),
                    '10%': float(result[4]['10%'])
                },
                'is_stationary': result[1] < 0.05  # p-value < 0.05
            }
        except Exception as e:
            logger.error(f"ADF test error: {e}")
            return {'error': str(e)}


class PairAnalysis:
    """High-level pair analysis combining multiple analytics"""
    
    def __init__(self, analytics: QuantAnalytics):
        self.analytics = analytics
        
    def analyze_pair(
        self, 
        symbol1: str,
        symbol2: str,
        prices1: pd.Series, 
        prices2: pd.Series, 
        window: int = 20
    ) -> Dict:
        """
        Perform comprehensive pair analysis with proper time series alignment.
        
        This method ensures:
        1. Time series are aligned before any computation
        2. All analytics are computed on aligned data only
        3. Safety gates prevent invalid data from reaching the frontend
        """
        # STEP 1: ALIGN TIME SERIES FIRST
        # Create DataFrame with both price series to ensure timestamp alignment
        df_aligned = pd.DataFrame({
            'p1': prices1,
            'p2': prices2
        })
        
        # Drop rows where either price is missing
        df_aligned = df_aligned.dropna()
        
        # Check if we have sufficient aligned data
        min_required = max(5, window)
        if len(df_aligned) < min_required:
            logger.warning(f"Insufficient aligned data: {len(df_aligned)} < {min_required}")
            return {
                'error': f'Insufficient aligned data: {len(df_aligned)} points, need at least {min_required}'
            }
        
        # Extract aligned prices
        aligned_prices1 = df_aligned['p1']
        aligned_prices2 = df_aligned['p2']
        
        logger.info(f"Aligned data: {len(df_aligned)} points from {len(prices1)} and {len(prices2)}")
        
        # STEP 2: COMPUTE ALL ANALYTICS ONLY ON ALIGNED DATA
        
        # Compute hedge ratio using OLS on aligned data
        if len(aligned_prices1) < 10:
            logger.warning("Not enough points for OLS hedge ratio")
            hedge_ratio = 1.0
            r_squared = 0.0
        else:
            x = aligned_prices2.values
            y = aligned_prices1.values
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            hedge_ratio = float(slope)
            r_squared = float(r_value ** 2)
        
        # Compute spread on aligned data
        spread = aligned_prices1 - hedge_ratio * aligned_prices2
        spread = spread.replace([np.inf, -np.inf], np.nan).dropna()
        
        # Compute rolling z-score on spread
        if len(spread) >= window:
            rolling_mean = spread.rolling(window=window).mean()
            rolling_std = spread.rolling(window=window).std()
            rolling_std = rolling_std.replace(0, np.nan)  # Avoid division by zero
            zscore = (spread - rolling_mean) / rolling_std
            zscore = zscore.replace([np.inf, -np.inf], np.nan).dropna()
        else:
            zscore = pd.Series(dtype=float)
        
        # Compute rolling correlation on aligned data
        if len(df_aligned) >= window:
            correlation = aligned_prices1.rolling(window=window).corr(aligned_prices2)
            correlation = correlation.dropna()
        else:
            correlation = pd.Series(dtype=float)
        
        # Compute basic stats on aligned data
        stats1 = self.analytics.compute_basic_stats(aligned_prices1)
        stats2 = self.analytics.compute_basic_stats(aligned_prices2)
        spread_stats = self.analytics.compute_basic_stats(spread)
        
        # ADF test on spread
        adf_result = self.analytics.augmented_dickey_fuller_test(spread)
        
        # STEP 3: APPLY SAFETY GATES FOR VISUALIZATION
        
        def series_to_list_safe(s: pd.Series) -> list:
            """
            Convert pandas Series to list of [timestamp, value] pairs.
            Returns EMPTY LIST if series is not plot-safe.
            """
            # Check if series is safe for plotting
            if not is_plot_safe(s, min_points=3):
                logger.warning(f"Series not plot-safe: len={len(s)}, unique={s.nunique() if len(s) > 0 else 0}")
                return []
            
            result = []
            for ts, v in s.items():
                # Double-check: skip NaN, inf values (should not happen after is_plot_safe)
                if pd.isna(v) or np.isinf(v):
                    continue
                timestamp_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
                result.append([timestamp_str, float(v)])
            
            # Final safety check: ensure we have valid data
            if len(result) < 2:
                return []
            
            return result
        
        def sanitize_value(v):
            """Convert numpy/pandas types to native Python types, handling NaN/Inf"""
            if v is None:
                return None
            if isinstance(v, (float, np.floating)):
                if pd.isna(v) or np.isinf(v):
                    return None
                return float(v)
            if isinstance(v, (np.integer, np.int64, np.int32)):
                return int(v)
            if isinstance(v, (bool, np.bool_)):
                return bool(v)
            return v
        
        def sanitize_dict(d):
            """Recursively sanitize all values in a dictionary"""
            if not isinstance(d, dict):
                return sanitize_value(d)
            return {k: sanitize_dict(v) if isinstance(v, dict) else sanitize_value(v) 
                    for k, v in d.items()}
        
        # Build result with safety-checked series
        result = {
            'symbol1': symbol1,
            'symbol2': symbol2,
            'hedge_ratio': sanitize_value(hedge_ratio),
            'r_squared': sanitize_value(r_squared),
            'current_spread': sanitize_value(spread.iloc[-1] if len(spread) > 0 else None),
            'current_zscore': sanitize_value(zscore.iloc[-1] if len(zscore) > 0 else None),
            'current_correlation': sanitize_value(correlation.iloc[-1] if len(correlation) > 0 else None),
            'stats': {
                symbol1: sanitize_dict(stats1),
                symbol2: sanitize_dict(stats2),
                'spread': sanitize_dict(spread_stats)
            },
            'adf_test': sanitize_dict(adf_result),
            'series': {
                'spread': series_to_list_safe(spread),
                'zscore': series_to_list_safe(zscore),
                'correlation': series_to_list_safe(correlation)
            }
        }
        
        logger.info(f"Analysis complete: spread={len(result['series']['spread'])} pts, "
                   f"zscore={len(result['series']['zscore'])} pts, "
                   f"corr={len(result['series']['correlation'])} pts")
        
        return result
