# Erica AgentCore Deployment

## Overview
This repository contains the deployment configuration and code for **EricaAgent**, an AWS Bedrock AgentCore application powered by Google Gemini, Redis, and LangChain. 

## Dependencies
The agent requires the following core dependencies (managed via `EricaAgent/app/EricaAgent/pyproject.toml` using `uv` and `hatchling`):
- `langchain-google-genai` (For Google Gemini model integration)
- `langchain-core` (Core LangChain primitives)
- `redis` (For session history and memory storage via Upstash)
- `boto3` (For fetching secrets from AWS Systems Manager)
- `python-dotenv` (For local environment fallback testing)
- `aws-opentelemetry-distro` & `opentelemetry-instrumentation-langchain >= 0.59.0` (Mandatory for AWS Lambda telemetry initialization)

## Key Management & Security
To avoid hardcoding sensitive API keys in source code (such as `EricaAgent/agentcore/agentcore.json`), this project uses **AWS Systems Manager (SSM) Parameter Store**.

1. **Storage**: Keys are securely stored in AWS as `SecureString` parameters:
   - `/erica/google-api-key`
   - `/erica/redis-url`
   - `/erica/langsmith-api-key`
2. **Runtime Retrieval**: At runtime, `EricaAgent/app/EricaAgent/agent.py` uses `boto3` to fetch these parameters dynamically upon AWS Lambda initialization. 
3. **Local Fallback**: For local development, if the agent cannot connect to AWS SSM, it gracefully falls back to loading keys from the root `.env` file (which is strictly excluded from version control via `.gitignore`).
4. **Permissions**: The agent's AWS IAM Execution Role must be granted the `AmazonSSMReadOnlyAccess` policy to allow decryption of the parameters.

## Deployment Steps
The agent is deployed using the AWS AgentCore CLI.

### 1. Initialize and Store Secrets
Use the AWS CLI to store your secrets in your AWS account (only needed once):
```bash
aws ssm put-parameter --name "/erica/google-api-key" --type "SecureString" --value "YOUR_KEY"
aws ssm put-parameter --name "/erica/redis-url" --type "SecureString" --value "YOUR_URL"
aws ssm put-parameter --name "/erica/langsmith-api-key" --type "SecureString" --value "YOUR_KEY"
```

### 2. Deploy the Agent
Change directory into the AgentCore folder and run the deployment:
```powershell
cd EricaAgent
agentcore.cmd deploy --yes
```

### 3. Invoke the Agent
Once deployed, the agent can be invoked directly from the terminal to test the live AWS Lambda:
```powershell
# Set your session ID
$SESSION = "erica-class-session-000000000000000001"

# Invoke the deployed agent
agentcore.cmd invoke --runtime EricaAgent --session-id $SESSION "Hello, my name is Anshul."
```

## Troubleshooting
- **Runtime initialization time exceeded**: This AWS timeout occurs if the Lambda container crashes during cold-start. This is commonly caused by missing dependencies (`aws-opentelemetry-distro`) in the `pyproject.toml`, or invalid connection strings (like placeholder Redis URLs) crashing the module initialization.
- **Nested Git Repository Warning**: If you initialize a git repository in the root folder over an AgentCore project, ensure you remove the inner `.git` folder from the `EricaAgent` directory so that all code files are properly tracked.
