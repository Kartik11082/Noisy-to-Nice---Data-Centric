import pandas as pd
from ydata_profiling import ProfileReport
import io
from datetime import datetime

class ProfilingService:
    """Service for generating data quality reports using YData Profiling"""
    
    def __init__(self, s3_service):
        self.s3_service = s3_service
    
    def generate_profile(self, file_content, filename):
        """
        Generate a profiling report from CSV file content
        
        Args:
            file_content: Bytes content of the CSV file
            filename: Original filename
            
        Returns:
            dict: Contains report_url, metrics, and issues
        """
        try:
            # Read CSV into DataFrame
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Generate profile with minimal configuration for speed
            profile = ProfileReport(
                df,
                title=f"Data Quality Report: {filename}",
                minimal=True,  # Faster processing
                explorative=False  # Skip time-consuming analyses
            )
            
            # Generate HTML report
            html_report = profile.to_html()
            
            # Upload HTML report to S3
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            report_key = f"reports/{timestamp}_{filename}.html"
            
            # Convert to bytes for S3 upload
            html_bytes = html_report.encode('utf-8')
            html_file = io.BytesIO(html_bytes)
            html_file.content_type = 'text/html'
            
            # Upload report
            upload_result = self.s3_service.upload_fileobj(
                html_file,
                report_key,
                'text/html'
            )
            
            if not upload_result['success']:
                return {
                    'success': False,
                    'message': 'Failed to upload profiling report'
                }
            
            # Extract key metrics from profile
            metrics = self._extract_metrics(profile, df)
            
            # Identify issues
            issues = self._identify_issues(profile, df, metrics)
            
            return {
                'success': True,
                'report_url': upload_result['s3_url'],
                'report_key': report_key,
                'metrics': metrics,
                'issues': issues
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Profiling failed: {str(e)}'
            }
    
    def _extract_metrics(self, profile, df):
        """Extract key metrics from the profile report"""
        try:
            # Get the profile description
            desc = profile.description_set
            
            # Calculate metrics
            total_cells = df.shape[0] * df.shape[1]
            missing_cells = df.isnull().sum().sum()
            missing_percentage = (missing_cells / total_cells * 100) if total_cells > 0 else 0
            
            # Count duplicate rows
            duplicate_rows = df.duplicated().sum()
            
            # Analyze data types
            numeric_cols = len(df.select_dtypes(include=['int64', 'float64']).columns)
            categorical_cols = len(df.select_dtypes(include=['object']).columns)
            datetime_cols = len(df.select_dtypes(include=['datetime64']).columns)
            
            # Calculate quality score (0-100)
            quality_score = self._calculate_quality_score(
                missing_percentage,
                duplicate_rows,
                df.shape[0]
            )
            
            metrics = {
                'total_rows': int(df.shape[0]),
                'total_columns': int(df.shape[1]),
                'missing_percentage': round(missing_percentage, 2),
                'duplicate_rows': int(duplicate_rows),
                'numeric_columns': numeric_cols,
                'categorical_columns': categorical_cols,
                'datetime_columns': datetime_cols,
                'quality_score': quality_score,
                'memory_size': df.memory_usage(deep=True).sum()
            }
            
            # Add column-level missing data
            missing_by_column = {}
            for col in df.columns:
                missing_pct = (df[col].isnull().sum() / len(df) * 100)
                if missing_pct > 0:
                    missing_by_column[col] = round(missing_pct, 2)
            
            metrics['missing_by_column'] = missing_by_column
            
            return metrics
            
        except Exception as e:
            print(f"Error extracting metrics: {str(e)}")
            return {
                'total_rows': int(df.shape[0]),
                'total_columns': int(df.shape[1]),
                'quality_score': 50
            }
    
    def _calculate_quality_score(self, missing_pct, duplicates, total_rows):
        """
        Calculate overall quality score (0-100)
        Higher is better
        """
        score = 100
        
        # Deduct for missing data (max -40 points)
        if missing_pct > 0:
            score -= min(missing_pct * 2, 40)
        
        # Deduct for duplicates (max -30 points)
        if duplicates > 0 and total_rows > 0:
            dup_pct = (duplicates / total_rows * 100)
            score -= min(dup_pct * 3, 30)
        
        # Ensure score is between 0 and 100
        return max(0, min(100, round(score, 1)))
    
    def _identify_issues(self, profile, df, metrics):
        """Identify data quality issues"""
        issues = []
        
        # Check for high missing data
        if metrics['missing_percentage'] > 5:
            severity = 'critical' if metrics['missing_percentage'] > 20 else 'warning'
            issues.append({
                'type': 'missing_data',
                'severity': severity,
                'message': f"{metrics['missing_percentage']}% of data is missing",
                'suggestion': 'Consider imputation strategies or removing columns with high missing rates'
            })
        
        # Check for duplicates
        if metrics['duplicate_rows'] > 0:
            dup_pct = (metrics['duplicate_rows'] / metrics['total_rows'] * 100)
            severity = 'critical' if dup_pct > 10 else 'warning'
            issues.append({
                'type': 'duplicates',
                'severity': severity,
                'message': f"{metrics['duplicate_rows']} duplicate rows found ({dup_pct:.1f}%)",
                'suggestion': 'Remove duplicate rows to avoid bias in model training'
            })
        
        # Check for columns with high missing data
        high_missing_cols = [
            col for col, pct in metrics.get('missing_by_column', {}).items()
            if pct > 50
        ]
        if high_missing_cols:
            issues.append({
                'type': 'high_missing_columns',
                'severity': 'warning',
                'message': f"{len(high_missing_cols)} columns have >50% missing data",
                'suggestion': f"Consider dropping columns: {', '.join(high_missing_cols[:3])}"
            })
        
        # Check for small dataset
        if metrics['total_rows'] < 100:
            issues.append({
                'type': 'small_dataset',
                'severity': 'info',
                'message': f"Only {metrics['total_rows']} rows - small dataset",
                'suggestion': 'Collect more data for better model performance'
            })
        
        # Check for imbalanced features (all numeric or all categorical)
        if metrics['numeric_columns'] == 0 and metrics['total_columns'] > 0:
            issues.append({
                'type': 'no_numeric_features',
                'severity': 'warning',
                'message': 'No numeric features detected',
                'suggestion': 'Encode categorical variables or engineer numeric features'
            })
        
        return issues
