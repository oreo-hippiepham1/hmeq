# HMEQ - Home Equity Loan Default Prediction System

A comprehensive machine learning system for predicting home equity loan defaults with explainable AI features and intelligent financial advice.

## 🎯 Overview

This project provides a complete solution for predicting loan default risk using multiple machine learning models, offering transparent explanations through LIME (Local Interpretable Model-agnostic Explanations), and delivering personalized financial advice through an AI agent powered by GPT-4.

### Key Features

- **Multi-Model Prediction**: Support for Random Forest, KNN, Gradient Boosting, and Decision Tree models
- **Explainable AI**: LIME explanations for model transparency and interpretability
- **AI-Powered Financial Advice**: Intelligent recommendations based on prediction results and explanations
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Containerized Deployment**: Docker support for easy deployment and scaling
- **Interactive Frontend**: React TypeScript frontend for user-friendly interactions

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   ML Models     │
│   (React TS)    │◄──►│   Backend        │◄──►│   & Pipelines   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   AI Agent       │
                       │   (LangGraph +   │
                       │    GPT-4)        │
                       └──────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.12**: Core programming language
- **Scikit-learn**: Machine learning library
- **LIME**: Model explainability
- **LangGraph**: AI agent workflow management
- **Pydantic-AI**: AI agent framework
- **OpenAI GPT-4**: Language model for financial advice

### Frontend
- **React**: UI library
- **TypeScript**: Type-safe JavaScript
- **Vite**: Build tool and development server

### Deployment
- **Docker**: Containerization
- **uvicorn**: ASGI server

## 📁 Project Structure

```
hmeq/
├── app/
│   ├── agent/
│   │   ├── lime_agent.py          # AI agent implementation
│   │   └── prompts.py             # AI agent prompts and templates
│   ├── assets/
│   │   ├── data/                  # Training and test datasets
│   │   ├── pipes/                 # Trained model pipelines
│   │   ├── feature_original_names.json
│   │   └── feature_preprocessed_names.json
│   ├── main.py                    # FastAPI application and endpoints
│   ├── ml_models.py              # ML model training and pipeline creation
│   ├── limestone.py              # LIME explanation utilities
│   ├── pipeline_utils.py         # Data preprocessing and translation utilities
│   ├── schemas.py                # Pydantic models for API validation
│   └── helpers.py                # Additional utility functions
├── frontend-hmeq/                # React frontend (separate directory)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container configuration
├── .dockerignore                # Docker build exclusions
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Docker (optional, for containerized deployment)
- OpenAI API key (for AI agent functionality)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hmeq
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env

4. **Download the data (cleaned and processed versions)** (tba)

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/

### Docker Deployment

1. **Build and run with Docker**
   ```bash
   # Build the image
   docker build -t hmeq-backend .

   # Run the container
   docker run -p 8000:8000 --env-file .env hmeq-backend
   ```

2. **Access the application**
   - API: http://localhost:8000

## 📊 ML Models (`ml_models.py`)

The `ml_models.py` file contains the core machine learning pipeline and model definitions. Here's what it includes:

### Features and Preprocessing

- **Categorical Features**: `REASON`, `JOB`
  - Imputed with "Other" for missing values
  - One-hot encoded with categorical dropping

- **Numerical Features (Log + Iterative Imputation)**: `LOAN`, `VALUE`, `MORTDUE`, `YOJ`, `CLAGE`, `DEBTINC`
  - Iterative imputation for missing values
  - Log transformation (log1p) for right-skewed distributions
  - Standard scaling

- **Numerical Features (Mode Imputation)**: `DELINQ`, `DEROG`, `NINQ`, `CLNO`
  - Mode imputation for missing values
  - Standard scaling

### Available Models

1. **Random Forest Classifier**
   - `criterion='entropy'`
   - `n_estimators=200`
   - `class_weight='balanced'`

2. **K-Nearest Neighbors**
   - `n_neighbors=1`
   - `algorithm='ball_tree'`
   - `p=1` (Manhattan distance)

3. **Gradient Boosting Classifier**
   - `n_estimators=600`
   - `max_depth=6`
   - `learning_rate=0.1`

4. **Decision Tree Classifier**
   - `max_depth=10`
   - `class_weight='balanced'`
   - `criterion='gini'`

### Pipeline Structure

Each model follows this pipeline structure:
```
Raw Data → Preprocessing Pipeline → Trained Model → Prediction
```

The preprocessing pipeline handles:
- Missing value imputation
- Feature transformation (log, scaling)
- Categorical encoding
- Feature naming consistency

### Training Process

To train new models, run:
```bash
python app/ml_models.py
```

This will:
1. Load training data from `app/assets/data/cleaned/`
2. Apply preprocessing transformations
3. Train all models on resampled data
4. Save trained pipelines to `app/assets/pipes/`

## 🔌 API Endpoints

### Core Endpoints

#### `GET /`
Health check endpoint
- **Response**: `{"message": "Hello World"}`

#### `POST /predict/{pipeline_name}`
Predict loan default probability
- **Parameters**: `pipeline_name` (rf, knn, gb, dt)
- **Body**: `LoanApplicationRequest`
- **Response**: `{"probability_of_default": float}`

#### `POST /explain_custom_instance/{pipeline_name}`
Get LIME explanation for custom input
- **Parameters**: `pipeline_name` (rf, knn, gb, dt)
- **Body**: `LoanApplicationRequest`
- **Response**:
  ```json
  {
    "pipeline_name": "string",
    "input_data": {...},
    "lime_explanation": [["condition", weight], ...]
  }
  ```

#### `GET /explain/{pipeline_name}/{instance_index}`
Get LIME explanation for test set instance
- **Parameters**:
  - `pipeline_name` (rf, knn, gb, dt)
  - `instance_index` (integer)
- **Response**: Similar to custom explanation

#### `POST /agent/advice`
Get AI-powered financial advice
- **Body**: `AgentAdviceRequest`
  ```json
  {
    "default_probability": 0.75,
    "lime_explanations": [["condition", weight], ...]
  }
  ```
- **Response**:
  ```json
  {
    "agent_interpretation": "string",
    "financial_advice": "string"
  }
  ```

### Data Models

#### `LoanApplicationRequest`
```json
{
  "LOAN": 10000.0,
  "MORTDUE": 25000.0,
  "VALUE": 70000.0,
  "REASON": "HomeImp",
  "JOB": "Office",
  "YOJ": 5.0,
  "DEROG": 0.0,
  "DELINQ": 0.0,
  "CLAGE": 120.0,
  "NINQ": 1.0,
  "CLNO": 10.0,
  "DEBTINC": 35.0
}
```

#### Field Descriptions
- `LOAN`: Loan amount requested
- `MORTDUE`: Amount due on existing mortgage
- `VALUE`: Current property value
- `REASON`: Loan purpose (HomeImp, DebtCon, Other)
- `JOB`: Applicant's job category (ProfExe, Mgr, Office, Sales, Self, Other)
- `YOJ`: Years on current job
- `DEROG`: Number of derogatory reports
- `DELINQ`: Number of delinquent credit lines
- `CLAGE`: Age of oldest credit line (months)
- `NINQ`: Number of recent credit inquiries
- `CLNO`: Number of credit lines
- `DEBTINC`: Debt-to-income ratio (%)

## 🤖 AI Agent

The AI agent (`app/agent/lime_agent.py`) provides intelligent financial advice by:

1. **Analyzing Predictions**: Interpreting the default probability in context
2. **Processing LIME Explanations**: Understanding feature contributions
3. **Generating Advice**: Providing actionable financial recommendations
4. **Risk Assessment**: Explaining risk factors and mitigation strategies

The agent uses LangGraph for workflow management and GPT-4 for natural language generation.

## 🔍 LIME Explanations

LIME (Local Interpretable Model-agnostic Explanations) provides transparency by:

- Explaining individual predictions
- Identifying important features for each decision
- Translating technical conditions into human-readable format
- Supporting model debugging and validation

Example LIME explanation:
```
[
  ("DEBTINC > 35.5", 0.3),
  ("JOB is not Office", 0.2),
  ("CLAGE <= 109.41", 0.15)
]
```

## 🌐 Usage Examples

### 1. Basic Prediction
```bash
curl -X POST "http://localhost:8000/predict/rf" \
  -H "Content-Type: application/json" \
  -d '{
    "LOAN": 10000,
    "MORTDUE": 25000,
    "VALUE": 70000,
    "REASON": "HomeImp",
    "JOB": "Office",
    "YOJ": 5.0,
    "DEROG": 0.0,
    "DELINQ": 0.0,
    "CLAGE": 120.0,
    "NINQ": 1.0,
    "CLNO": 10.0,
    "DEBTINC": 35.0
  }'
```

### 2. Get Explanation
```bash
curl -X POST "http://localhost:8000/explain_custom_instance/rf" \
  -H "Content-Type: application/json" \
  -d '{...same data as above...}'
```

### 3. Get AI Advice
```bash
curl -X POST "http://localhost:8000/agent/advice" \
  -H "Content-Type: application/json" \
  -d '{
    "default_probability": 0.75,
    "lime_explanations": [
      ["DEBTINC > 35.5", 0.3],
      ["JOB is not Office", 0.2]
    ]
  }'
```

## 🚀 Deployment

### AWS Deployment Options

1. **AWS App Runner** (Recommended for simplicity)
2. **ECS with Fargate** (Serverless containers)
3. **EC2 with Docker** (Traditional deployment)
4. **Lambda** (Requires modifications for serverless)

### Environment Variables

Required environment variables for production:
```bash
OPENAI_API_KEY=your_openai_api_key
```

## 🔧 Development

### Adding New Models

1. Define model in `ml_models.py`
2. Add to training pipeline
3. Update `PIPELINES` dictionary in `main.py`
4. Test with API endpoints

### Extending AI Agent

1. Modify prompts in `app/agent/prompts.py`
2. Update agent logic in `app/agent/lime_agent.py`
3. Test with `/agent/advice` endpoint


**Note**: This system is designed for educational and research purposes. Ensure proper validation and testing before using in production financial applications.
