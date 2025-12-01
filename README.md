# Noisy to Nice - ML Dataset Quality Analyzer

A comprehensive web application for uploading, analyzing, and improving CSV datasets for machine learning. Upload your datasets, get instant quality assessments powered by YData Profiling, and receive AI-driven recommendations from AWS Bedrock to prepare your data for ML training.

## ✨ Features

### Core Features
- 🔐 **Authentication** - Secure login and signup system with JWT tokens
- 📁 **File Upload** - Drag-and-drop CSV upload to AWS S3
- 💾 **Metadata Storage** - Automatic extraction and storage in DynamoDB

### Data Analysis Features ⭐
- 📊 **YData Profiling** - Comprehensive data quality reports with statistics, distributions, and correlations
- 🤖 **AI-Powered Insights** - AWS Bedrock (Claude 3 Haiku) provides actionable recommendations
- 🎯 **Quality Scoring** - Automated 0-100 quality score based on missing data, duplicates, and more
- 🔍 **Issue Detection** - Identifies missing data, duplicates, small datasets, and feature imbalances
- 📈 **Detailed Metrics** - Row/column counts, data types, missing percentages by column
- 💡 **ML Readiness Assessment** - Get specific preprocessing steps to improve model performance

### UI/UX
- 🎨 **Modern Interface** - Beautiful, responsive design with animations
- 📱 **Mobile Friendly** - Works seamlessly on all devices
- ⚡ **Fast & Efficient** - Optimized profiling with background processing

## Project Structure

```
NoisytoNice/
├── backend/                 # Flask API
│   ├── app.py              # Main application with analysis endpoints
│   ├── config.py           # Configuration management
│   ├── requirements.txt    # Python dependencies
│   ├── aws_config.json.example  # AWS config template
│   └── services/
│       ├── auth_service.py        # JWT authentication
│       ├── s3_service.py          # S3 file operations
│       ├── dynamodb_service.py    # DynamoDB metadata storage
│       ├── profiling_service.py   # YData Profiling integration
│       └── bedrock_service.py     # AWS Bedrock AI insights
│
└── frontend/               # React application
    ├── src/
    │   ├── App.jsx         # Main app with routing
    │   ├── main.jsx
    │   ├── index.css       # Global styles
    │   ├── components/
    │   │   ├── Auth.jsx           # Login/signup forms
    │   │   ├── FileUpload.jsx     # File upload & list
    │   │   └── DataQuality.jsx    # Analysis dashboard
    │   └── services/
    │       └── api.js      # API integration
    └── package.json
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- AWS Account with:
  - S3 bucket
  - DynamoDB table
  - **AWS Bedrock access** (Claude 3 Haiku enabled)
  - IAM credentials with appropriate permissions

## AWS Setup

### 1. Create S3 Bucket

```bash
aws s3 mb s3://your-ml-datasets-bucket --region us-east-1
```

Or via AWS Console:
- Go to S3 → Create bucket
- Name: `your-ml-datasets-bucket`
- Region: `us-east-1` (or your preferred region)
- Keep default settings

### 2. Create DynamoDB Table

```bash
aws dynamodb create-table \
    --table-name FileMetadata \
    --attribute-definitions AttributeName=file_id,AttributeType=S \
    --key-schema AttributeName=file_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

Or via AWS Console:
- Go to DynamoDB → Create table
- Table name: `FileMetadata`
- Partition key: `file_id` (String)
- Use default settings (on-demand capacity)

### 3. Enable AWS Bedrock (IMPORTANT!)

**Required for AI-powered insights:**

1. Go to AWS Console → Bedrock service
2. Navigate to "Model access" in the left sidebar
3. Click "Modify model access"
4. Enable **Claude 3 Haiku** (recommended) or Claude 3.5 Sonnet
5. Submit and wait for access to be granted (~2-5 minutes)
6. Verify status shows "Access granted"

### 4. Get AWS Credentials

- Go to IAM → Users → Your user → Security credentials
- Create access key
- Save the Access Key ID and Secret Access Key

## Installation & Setup

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure AWS credentials:**
   ```bash
   copy aws_config.json.example aws_config.json
   ```
   
   Edit `aws_config.json` with your AWS credentials:
   ```json
   {
     "aws_access_key_id": "YOUR_ACCESS_KEY",
     "aws_secret_access_key": "YOUR_SECRET_KEY",
     "region": "us-east-1",
     "s3_bucket_name": "your-ml-datasets-bucket",
     "dynamodb_table_name": "FileMetadata"
   }
   ```

6. **Run the Flask server:**
   ```bash
   python app.py
   ```
   
   The API will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment (optional):**
   The `.env` file is already created with the default backend URL. If your backend runs on a different port, edit `.env`:
   ```
   VITE_API_URL=http://localhost:5000
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:3000`

## Usage

### 1. Sign Up
- Open `http://localhost:3000` (or your frontend URL) in your browser
- Click "Sign Up" tab
- Enter username and password
- Click "Sign Up" button

### 2. Login
- Switch to "Login" tab
- Enter your credentials
- Click "Login" button

### 3. Upload Dataset
- Drag and drop a CSV file onto the upload zone, or click to browse
- The file will be uploaded to S3 and metadata stored in DynamoDB
- View your uploaded files below with details (rows, columns, size)

### 4. Analyze Data Quality ⭐
- Click the **"📊 Analyze Quality"** button on any uploaded dataset
- Wait 30-60 seconds for analysis (time varies by dataset size)
- View comprehensive results:
  - **Quality Score** (0-100) with visual indicator
  - **Key Metrics**: Rows, columns, missing data %, duplicates
  - **Issues Found**: Detailed list with severity levels
  - **AI Insights**: Assessment and recommendations from AWS Bedrock
  - **Full Report**: Click "View Full Report" for detailed YData Profiling HTML

### 5. Review Insights
- Read AI-powered recommendations for preprocessing
- Check data quality score to assess ML readiness
- View full YData Profiling report for detailed analysis
- Use suggestions to clean and improve your dataset

### 6. Manage Files
- **View in S3**: Open file directly in AWS S3 console
- **Delete**: Remove metadata from DynamoDB

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### File Operations
- `POST /api/upload` - Upload file (requires authentication)
- `GET /api/files` - Get user's files (requires authentication)
- `DELETE /api/files/:fileId` - Delete file metadata (requires authentication)

### Data Analysis ⭐
- `POST /api/analyze/:fileId` - Trigger data quality analysis (requires authentication)
  - Generates YData Profiling report
  - Calls AWS Bedrock for AI insights
  - Returns quality score, metrics, issues, and recommendations
- `GET /api/analysis/:fileId` - Get analysis results (requires authentication)
  - Returns cached analysis from DynamoDB

### Health Check
- `GET /api/health` - Check API status

## Deployment

### Backend Deployment Options

1. **AWS Lambda** (Recommended for AWS)
   - Use Zappa or AWS SAM
   - Integrates well with S3 and DynamoDB

2. **Railway / Render / Heroku**
   - Simple deployment with Git push
   - Add AWS credentials as environment variables

3. **AWS EC2**
   - Traditional hosting
   - More control over environment

### Frontend Deployment (Vercel)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import your repository
   - Set root directory to `frontend`
   - Add environment variable: `VITE_API_URL=YOUR_BACKEND_URL`
   - Deploy

## Security Notes

⚠️ **Important Security Considerations:**

- Never commit `aws_config.json` to version control
- Use environment variables for production credentials
- Consider using AWS IAM roles instead of access keys
- Implement rate limiting for production
- Add file size limits for uploads
- Validate and sanitize all user inputs
- Use HTTPS in production

## Technology Stack

### Backend
- **Flask** - Web framework
- **boto3** - AWS SDK for Python
- **PyJWT** - JWT authentication
- **pandas** - Data processing and CSV handling
- **numpy** - Numerical computing (type conversions)
- **ydata-profiling** - Comprehensive data quality reports

### Frontend
- **React 18** - UI library
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Modern CSS** - Styling with CSS variables and animations

### AWS Services
- **S3** - File and report storage
- **DynamoDB** - Metadata and analysis results storage
- **Bedrock** - AI-powered insights (Claude 3 Haiku)

## Troubleshooting

### Backend Issues

**ImportError or Module Not Found:**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

**AWS Configuration Error:**
- Verify `aws_config.json` exists and has correct credentials
- Check IAM permissions for S3, DynamoDB, and Bedrock

**CORS Errors:**
- Ensure Flask-CORS is installed
- Check frontend is using correct API URL

### Data Analysis Issues ⭐

**"Analysis failed: Bedrock access denied" or "You don't have access to the model":**
- Go to AWS Console → Bedrock → Model Access
- Enable Claude 3 Haiku (or Claude 3.5 Sonnet)
- Wait 2-5 minutes for access to be granted
- Verify region in `aws_config.json` matches your Bedrock region

**"Analysis failed: Float types are not supported":**
- This has been fixed in the code
- If you still see this, restart your Flask backend to reload changes
- The app automatically converts numpy/float types to DynamoDB-compatible types

**Analysis takes too long (>5 minutes):**
- Large datasets (>100K rows) require more processing time
- YData Profiling is CPU-intensive - this is normal
- Consider using a smaller sample for initial testing
- The minimal=True setting is already optimized for speed

**AI insights are generic or missing:**
- Check backend logs for Bedrock errors
- Verify AWS Bedrock access is enabled
- If Bedrock fails, you still get YData report + quality score
- Generic fallback recommendations are provided if AI fails

**"Profiling failed: validation error":**
- Ensure you're using ydata-profiling 4.6.0 (check requirements.txt)
- Some parameters may not be supported in your version
- The code has been updated to remove unsupported parameters

### Frontend Issues

**Cannot connect to backend:**
- Verify backend is running on port 5000
- Check `.env` file has correct `VITE_API_URL`
- Look for CORS errors in browser console

**Analysis page blank or "No Analysis Available" stuck:**
- Check that analysis completed successfully in backend
- Refresh the page
- Check browser console for JavaScript errors
- Verify file was uploaded successfully

**npm/npx script errors on Windows:**
- Run PowerShell as Administrator  
- Execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## Sample Datasets

Three sample CSV files are included in the project root for testing:

1. **sample_data_clean.csv** - High quality dataset (~98/100 score)
   - 15 rows, 8 columns
   - No missing data or duplicates
   - Perfect for testing successful analysis

2. **sample_data_medium.csv** - Medium quality dataset (~80/100 score)
   - 20 rows, 9 columns  
   - ~5% missing data
   - Good for testing imputation recommendations

3. **sample_data_messy.csv** - Low quality dataset (~45/100 score)
   - 20 rows with ~20% missing data
   - Contains duplicate rows
   - Great for testing issue detection and AI recommendations

## Cost Estimate

Per dataset analysis:
- **YData Profiling**: Free (CPU only)
- **S3 Storage**: ~$0.023/GB/month
  - CSV storage: ~$0.0001 per file
  - HTML reports: ~$0.0001 per report
- **DynamoDB**: ~$0.0001 per write/read
- **Bedrock (Claude Haiku)**: ~$0.01-0.03 per analysis

**Total cost per analysis: ~$0.01-0.05**

For 100 datasets analyzed:
- Total: ~$1-5
- Most cost is from Bedrock API calls
- Reports stored in S3 incur minimal ongoing storage costs

## License

MIT

## Contributing

Feel free to submit issues and enhancement requests!
