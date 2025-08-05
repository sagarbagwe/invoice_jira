import os
import vertexai
import base64
import json
import sys
from pathlib import Path
from vertexai.preview import reasoning_engines

print("--- Script to Query Deployed Reasoning Engine ---")

# 1. READ CONFIGURATION FROM ENVIRONMENT VARIABLES
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
REASONING_ENGINE_ID = os.getenv("REASONING_ENGINE_ID")

if not all([PROJECT_ID, LOCATION, REASONING_ENGINE_ID]):
    print("\n❌ ERROR: Missing required environment variables.")
    print("Please run the 'export' commands from the guide before running this script.")
    sys.exit(1)

# 2. VERIFY DATA FILES EXIST
data_dir = Path("data")
invoice_path = data_dir / "invoice.pdf"
jira_path = data_dir / "jira.pdf"
master_data_path = data_dir / "master_data.xlsx"

if not all([invoice_path.exists(), jira_path.exists(), master_data_path.exists()]):
    print(f"\n❌ ERROR: One or more data files not found in the '{data_dir}' directory.")
    print("Please place your files there or run 'python main.py' once to create dummy files.")
    sys.exit(1)

try:
    # 3. INITIALIZE VERTEX AI SDK
    print(f"\n✅ Initializing Vertex AI for project '{PROJECT_ID}'...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # 4. LOAD AND BASE64 ENCODE LOCAL FILES
    print("✅ Loading and encoding local documents...")
    with open(invoice_path, "rb") as f:
        invoice_b64 = base64.b64encode(f.read()).decode('utf-8')
    with open(jira_path, "rb") as f:
        jira_b64 = base64.b64encode(f.read()).decode('utf-8')
    with open(master_data_path, "rb") as f:
        master_data_b64 = {master_data_path.name: base64.b64encode(f.read()).decode('utf-8')}
    print("   ...documents encoded successfully.")

    # 5. CONNECT TO THE DEPLOYED REASONING ENGINE
    print(f"✅ Connecting to remote agent: {REASONING_ENGINE_ID}")
    remote_agent = reasoning_engines.ReasoningEngine(REASONING_ENGINE_ID)

    # 6. CALL THE AGENT'S 'query' METHOD
    print("✅ Sending request to agent... (This may take a moment)")
    response = remote_agent.query(
        # These keyword arguments MUST match the signature of your agent's query() method
        invoice_b64=invoice_b64,
        jira_b64=jira_b64,
        master_data_b64=master_data_b64,
    )

    # 7. PRINT THE RESPONSE
    print("\n" + "="*20 + " AGENT RESPONSE " + "="*20)
    print(json.dumps(response, indent=2))
    print("="*56 + "\n")

except Exception as e:
    print(f"\n❌ An error occurred: {e}")