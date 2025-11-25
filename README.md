# ML Dataset Uploader

A web application for uploading CSV datasets to AWS S3 with metadata storage in DynamoDB. Built with Flask (backend) and React (frontend).

## Features

- 🔐 Simple authentication system (login/signup)
- 📁 CSV file upload to AWS S3
- 📊 Automatic metadata extraction (rows, columns, file size)
- 💾 Metadata storage in DynamoDB
- 📋 View uploaded datasets with detailed information
- 🎨 Modern, responsive UI with drag-and-drop support

## Project Structure

```
NoisytoNice/
├── backend/                 # Flask API
│   ├── app.py              # Main application
│   ├── config.py           # Configuration management
│   ├── requirements.txt    # Python dependencies
│   ├── aws_config.json.example  # AWS config template
│   └── services/
│       ├── auth_service.py     # Authentication
│       ├── s3_service.py       # S3 operations
│       └── dynamodb_service.py # DynamoDB operations
│
└── frontend/               # React application
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   ├── index.css
    │   ├── components/
    │   │   ├── Auth.jsx
    │   │   └── FileUpload.jsx
    │   └── services/
    │       └── api.js
    └── package.json
```

## Prerequisites

- Python 3.8+
- Node.js 16+
- AWS Account with:
  - S3 bucket
  - DynamoDB table
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

### 3. Get AWS Credentials

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

1. **Sign Up:**
   - Open `http://localhost:3000` in your browser
   - Click "Sign Up" tab
   - Enter username and password
   - Click "Sign Up" button

2. **Login:**
   - Switch to "Login" tab
   - Enter your credentials
   - Click "Login" button

3. **Upload Dataset:**
   - Drag and drop a CSV file onto the upload zone, or click to browse
   - The file will be uploaded to S3 and metadata stored in DynamoDB
   - View your uploaded files below

4. **View Files:**
   - See all your uploaded datasets with metadata
   - Click "View in S3" to open the file in AWS
   - Click "Delete" to remove the metadata (S3 file remains)

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### File Operations
- `POST /api/upload` - Upload file (requires authentication)
- `GET /api/files` - Get user's files (requires authentication)
- `DELETE /api/files/:fileId` - Delete file metadata (requires authentication)

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
- **pandas** - CSV processing

### Frontend
- **React** - UI library
- **Vite** - Build tool
- **Modern CSS** - Styling with CSS variables

### AWS Services
- **S3** - File storage
- **DynamoDB** - Metadata storage

## Troubleshooting

### Backend Issues

**ImportError or Module Not Found:**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt`

**AWS Configuration Error:**
- Verify `aws_config.json` exists and has correct credentials
- Check IAM permissions for S3 and DynamoDB

**CORS Errors:**
- Ensure Flask-CORS is installed
- Check frontend is using correct API URL

### Frontend Issues

**Cannot connect to backend:**
- Verify backend is running on port 5000
- Check `.env` file has correct `VITE_API_URL`

**npm/npx script errors on Windows:**
- Run PowerShell as Administrator
- Execute: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## License

MIT

## Contributing

Feel free to submit issues and enhancement requests!
