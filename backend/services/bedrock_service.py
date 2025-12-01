import boto3
import json
from config import Config


class BedrockService:
    """Service for generating AI insights using AWS Bedrock"""

    def __init__(self):
        credentials = Config.get_aws_credentials()
        self.bedrock_client = boto3.client(
            "bedrock-runtime",
            aws_access_key_id=credentials["aws_access_key_id"],
            aws_secret_access_key=credentials["aws_secret_access_key"],
            region_name=credentials["region_name"],
        )

        # Using Claude 3 Haiku for cost efficiency
        self.model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        self.max_tokens = 1024
        self.temperature = 0.3  # Lower for more focused responses

    def generate_insights(self, filename, metrics, issues):
        """
        Generate AI-powered insights about data quality

        Args:
            filename: Name of the dataset
            metrics: Dictionary of data quality metrics
            issues: List of identified issues

        Returns:
            dict: Contains insights and recommendations
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(filename, metrics, issues)

            # Prepare request for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            # Call Bedrock
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id, body=json.dumps(request_body)
            )

            # Parse response
            response_body = json.loads(response["body"].read())
            ai_text = response_body["content"][0]["text"]

            # Parse the structured response
            parsed = self._parse_response(ai_text)

            return {
                "success": True,
                "assessment": parsed["assessment"],
                "recommendations": parsed["recommendations"],
                "raw_response": ai_text,
            }

        except Exception as e:
            print(f"Bedrock error: {str(e)}")
            return {
                "success": False,
                "message": f"AI insights generation failed: {str(e)}",
                "assessment": "Unable to generate AI assessment at this time.",
                "recommendations": [],
            }

    def _build_prompt(self, filename, metrics, issues):
        """Build the prompt for the LLM"""

        # Format issues list
        issues_text = (
            "\n".join(
                [
                    f"- {issue['severity'].upper()}: {issue['message']}"
                    for issue in issues
                ]
            )
            if issues
            else "No major issues detected"
        )

        # Format missing columns
        missing_cols_text = ""
        if metrics.get("missing_by_column"):
            top_missing = sorted(
                metrics["missing_by_column"].items(), key=lambda x: x[1], reverse=True
            )[:5]
            missing_cols_text = "\nColumns with missing data:\n" + "\n".join(
                [f"- {col}: {pct}% missing" for col, pct in top_missing]
            )

        prompt = f"""You are a data quality expert for machine learning. Analyze this dataset quality report and provide actionable insights.

                        Dataset: {filename}
                        Total Rows: {metrics.get("total_rows", "N/A")}
                        Total Columns: {metrics.get("total_columns", "N/A")}
                        Quality Score: {metrics.get("quality_score", "N/A")}/100

                        Data Composition:
                        - Numeric columns: {metrics.get("numeric_columns", 0)}
                        - Categorical columns: {metrics.get("categorical_columns", 0)}
                        - DateTime columns: {metrics.get("datetime_columns", 0)}

                        Data Quality Issues:
                        - Missing data: {metrics.get("missing_percentage", 0)}%
                        - Duplicate rows: {metrics.get("duplicate_rows", 0)}{missing_cols_text}

                        Detected Issues:
                        {issues_text}

                        Provide a response in this exact format:

                        ASSESSMENT:
                        [2-3 sentences overall quality assessment for ML readiness]

                        RECOMMENDATIONS:
                        1. [First specific recommendation]
                        2. [Second specific recommendation]
                        3. [Third specific recommendation]
                        4. [Fourth recommendation if needed]
                        5. [Fifth recommendation if needed]

                        Keep recommendations concrete and actionable. Focus on preprocessing steps to improve ML model performance."""

        return prompt

    def _parse_response(self, ai_text):
        """Parse the structured LLM response"""
        try:
            # Split by sections
            parts = ai_text.split("RECOMMENDATIONS:")

            assessment = ""
            recommendations = []

            if len(parts) >= 1:
                # Extract assessment
                assessment_part = parts[0].replace("ASSESSMENT:", "").strip()
                assessment = assessment_part

            if len(parts) >= 2:
                # Extract recommendations
                rec_text = parts[1].strip()
                lines = rec_text.split("\n")

                for line in lines:
                    line = line.strip()
                    # Match numbered items
                    if line and (line[0].isdigit() or line.startswith("-")):
                        # Remove number/bullet and clean
                        cleaned = line.lstrip("0123456789.-) ").strip()
                        if cleaned:
                            recommendations.append(cleaned)

            # Fallback if parsing fails
            if not assessment:
                assessment = ai_text[:500]  # First 500 chars

            if not recommendations:
                recommendations = [
                    "Review the full profiling report for detailed insights",
                    "Address missing data through imputation or removal",
                    "Remove duplicate rows to avoid training bias",
                ]

            return {
                "assessment": assessment,
                "recommendations": recommendations[:5],  # Max 5
            }

        except Exception as e:
            print(f"Parse error: {str(e)}")
            return {
                "assessment": ai_text[:500] if ai_text else "Analysis complete",
                "recommendations": [
                    "Review the detailed profiling report",
                    "Address data quality issues identified",
                ],
            }
