# Quick Start Guide - ML Dataset Uploader with Data Quality Analysis

Get your ML Dataset Uploader with AI-powered insights running quickly.

## Prerequisites

- Python 3.8+
- Node.js 16+
- AWS Account with:
  - S3 bucket
  - DynamoDB table
  - Bedrock access (for AI insights)

## Step 1: AWS Setup (5-10 minutes)

### Option A: Automated (Recommended)
1. Navigate to backend: `cd backend`
2. Copy config: `copy aws_config.json.example aws_config.json`
3. Edit `aws_config.json` with your AWS credentials
4. Run setup script: `python setup_aws.py`

### Option B: Manual
```bash
# Create S3 bucket
aws s3 mb s3://your-ml-datasets-bucket --region us-east-1

# Create DynamoDB table
aws dynamodb create-table \
    --table-name FileMetadata \
    --attribute-definitions AttributeName=file_id,AttributeType=S \
    --key-schema AttributeName=file_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

### Enable AWS Bedrock (IMPORTANT!)
1. Go to AWS Console → Bedrock
2. Navigate to "Model access" in left sidebar
3. Click "Modify model access"
4. Enable **Claude 3 Haiku** (or Claude 3.5 Sonnet for better quality)
5. Wait for access to be granted (~5 minutes)

## Step 2: Backend Setup (3 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies (includes ydata-profiling)
pip install -r requirements.txt

# Configure AWS (if not done in Step 1)
copy aws_config.json.example aws_config.json
# Edit aws_config.json with your credentials

# Run server
python app.py
```

Backend runs on `http://localhost:5000`

## Step 3: Frontend Setup (2-3 minutes)

Open a **new terminal**:

```bash
cd frontend

# Install dependencies (includes react-router-dom)
npm install

# Run development server
npm run dev
```

Frontend runs on `http://localhost:3000`

## Step 4: Use the App!

1. **Sign Up/Login**
   - Open `http://localhost:3000`
   - Create an account or login

2. **Upload Dataset**
   - Drag & drop or click to upload a CSV file
   - Wait for upload to complete

3. **Analyze Data Quality** ⭐ NEW!
   - Click "📊 Analyze Quality" on any dataset
   - Wait 30-60 seconds for analysis (depends on dataset size)
   - View:
     - Quality score (0-100)
     - Missing data, duplicates, outliers
     - AI-powered insights and recommendations
     - Full YData Profiling report

4. **Review Insights**
   - Check data quality score
   - Read AI recommendations
   - Click "View Full Report" for detailed HTML report

## Features Overview

### Data Quality Analysis
- ✅ Automatic profiling with YData Profiling
- ✅ Quality score calculation
- ✅ Missing data & duplicate detection
- ✅ Column-level analysis
- ✅ AI-powered insights via AWS Bedrock (Claude Haiku)
- ✅ Actionable recommendations for ML readiness

### Analysis Metrics
- Total rows & columns
- Missing data percentage
- Duplicate row count
- Data type distribution
- Quality issues with severity levels
- AI assessment of dataset readiness

## Troubleshooting

### Bedrock Access Denied
**Error**: "You don't have access to the model"
**Solution**: Enable Claude Haiku in AWS Bedrock Console → Model Access

### Profiling Takes Too Long
**Cause**: Large datasets (>100K rows)
**Solution**: This is normal. YData Profiling is CPU-intensive. Wait or use smaller sample first.

### npm/npx Errors on Windows
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Module Not Found (Backend)
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### React Router Errors
- Make sure you ran `npm install` (react-router-dom should be in dependencies)
- Check that App.jsx has BrowserRouter

## Cost Estimate

Per Dataset Analysis:
- **YData Profiling**: Free (CPU only)
- **S3 Storage**: ~$0.023/GB/month (~$0.0001 per report)
- **DynamoDB**: ~$0.0001 per write
- **Bedrock (Claude Haiku)**: ~$0.01-0.03 per analysis

**Total: ~$0.01-0.05 per dataset analysis**

## Next Steps

1. Test with various datasets (clean & dirty)
2. Review AI recommendations
3. Compare quality scores
4. Use insights to improve your data
5. Deploy to production (see README.md)

Enjoy your AI-powered data quality insights! 🚀
