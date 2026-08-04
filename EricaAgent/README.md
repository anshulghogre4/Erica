# AgentCore Project: EricaAgent

This project was created with the [AgentCore CLI](https://github.com/aws/agentcore-cli) and is configured to run on **AWS Bedrock AgentCore**.

## 🚀 Custom Deployment & AWS Configuration

### Dependencies
The agent requires the following core dependencies (managed via `pyproject.toml` using `uv` and `hatchling`):
- `langchain-google-genai` (For Google Gemini model integration)
- `langchain-core` (Core LangChain primitives)
- `redis` (For session history and memory storage via Upstash)
- `boto3` (For fetching secrets from AWS Systems Manager)
- `python-dotenv` (For local environment fallback testing)
- `aws-opentelemetry-distro` & `opentelemetry-instrumentation-langchain >= 0.59.0` (Mandatory for AWS Lambda telemetry initialization)

### Key Management & Security (AWS SSM)
To avoid hardcoding sensitive API keys in source code (such as `agentcore.json`), this project uses **AWS Systems Manager (SSM) Parameter Store**.

1. **Storage**: Keys are securely stored in AWS as `SecureString` parameters:
   - `/erica/google-api-key`
   - `/erica/redis-url`
   - `/erica/langsmith-api-key`
2. **Runtime Retrieval**: At runtime, `agent.py` uses `boto3` to fetch these parameters dynamically upon AWS Lambda initialization. 
3. **Local Fallback**: For local development, if the agent cannot connect to AWS SSM, it gracefully falls back to loading keys from a root `.env` file (which is strictly excluded from version control via `.gitignore`).
4. **Permissions**: The agent's AWS IAM Execution Role is granted the `AmazonSSMReadOnlyAccess` policy to allow decryption of the parameters.

### Deployment Steps
To manually configure and deploy this agent to AWS:

1. **Initialize Secrets in AWS:**
   ```bash
   aws ssm put-parameter --name "/erica/google-api-key" --type "SecureString" --value "YOUR_KEY"
   aws ssm put-parameter --name "/erica/redis-url" --type "SecureString" --value "YOUR_URL"
   aws ssm put-parameter --name "/erica/langsmith-api-key" --type "SecureString" --value "YOUR_KEY"
   ```

2. **Deploy the Agent:**
   ```powershell
   agentcore.cmd deploy --yes
   ```

3. **Test the Live Agent:**
   ```powershell
   $SESSION = "erica-class-session-000000000000000001"
   agentcore.cmd invoke --runtime EricaAgent --session-id $SESSION "Hello, my name is Anshul."
   ```

---

## Default AgentCore Project Structure

```
my-project/
├── AGENTS.md               # AI coding assistant context
├── agentcore/
│   ├── agentcore.json      # Project config (agents, memories, credentials, gateways, evaluators)
│   ├── aws-targets.json    # Deployment targets (account + region)
│   ├── .env.local          # Secrets — API keys (gitignored)
│   ├── .llm-context/       # TypeScript type definitions for AI assistants
│   │   ├── agentcore.ts    # AgentCoreProjectSpec types
│   │   ├── aws-targets.ts  # Deployment target types
│   │   └── mcp.ts          # Gateway and MCP tool types
│   └── cdk/                # CDK infrastructure (@aws/agentcore-cdk)
├── app/                    # Agent application code
└── evaluators/             # Custom evaluator code (if any)
```

## Getting Started

### Prerequisites

- **Node.js** 20.x or later
- **Python 3.10+** and **uv** for Python agents ([install uv](https://docs.astral.sh/uv/getting-started/installation/))
- **AWS credentials** configured (`aws configure` or environment variables)
- **Docker** (only for Container build agents)

### Development

Run your agent locally:

```bash
agentcore dev
```

### Deployment

Deploy to AWS:

```bash
agentcore deploy
```

## Commands

| Command | Description |
| --- | --- |
| `agentcore create` | Create a new AgentCore project |
| `agentcore add` | Add resources (agent, memory, credential, gateway, evaluator, policy) |
| `agentcore remove` | Remove resources |
| `agentcore dev` | Run agent locally with hot-reload |
| `agentcore deploy` | Deploy to AWS via CDK |
| `agentcore status` | Show deployment status |
| `agentcore invoke` | Invoke agent (local or deployed) |
| `agentcore logs` | View agent logs |
| `agentcore traces` | View agent traces |
| `agentcore eval` | Run evaluations |
| `agentcore package` | Package agent artifacts |
| `agentcore validate` | Validate configuration |
| `agentcore pause` | Pause a deployed agent |
| `agentcore resume` | Resume a paused agent |
| `agentcore fetch` | Fetch remote resource definitions |
| `agentcore import` | Import existing resources |
| `agentcore update` | Check for CLI updates |

## Configuration

Edit the JSON files in `agentcore/` to configure your project. See `agentcore/.llm-context/` for type definitions and validation constraints.

The project uses a **flat resource model** — agents, memories, credentials, gateways, evaluators, and policies are top-level arrays in `agentcore.json`. Resources are independent; agents discover memories and credentials at runtime via environment variables or SDK calls.

## Resources

| Resource | Purpose |
| --- | --- |
| Agent (runtime) | HTTP, MCP, or A2A agent deployed to AgentCore Runtime |
| Memory | Persistent context storage with configurable strategies |
| Credential | API key or OAuth credential providers |
| Gateway | MCP gateway that routes tool calls to targets |
| Gateway Target | Tool implementation (Lambda, MCP server, OpenAPI, Smithy, API Gateway) |
| Evaluator | Custom LLM-as-a-Judge or code-based evaluation |
| Online Eval Config | Continuous evaluation pipeline for deployed agents |
| Policy | Cedar authorization policies for gateway tools |

### Agent Types

- **Template agents**: Created from framework templates (Strands, LangChain/LangGraph, GoogleADK, OpenAI Agents, Autogen)
- **BYO agents**: Bring your own code with `agentcore add agent --type byo`
- **Import agents**: Import existing Bedrock agents with `agentcore import`

### Build Types

- **CodeZip**: Python source packaged as a zip and deployed directly to AgentCore Runtime
- **Container**: Docker image built via CodeBuild (ARM64), pushed to ECR, and deployed to AgentCore Runtime

## Documentation

- [AgentCore CLI](https://github.com/aws/agentcore-cli)
- [AgentCore CDK Constructs](https://github.com/aws/agentcore-l3-cdk-constructs)
- [Amazon Bedrock AgentCore](https://aws.amazon.com/bedrock/agentcore/)
