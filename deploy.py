import vertexai
import os
from dotenv import load_dotenv
from vertexai.preview import reasoning_engines
from multi_tool_agent.agent import SimpleInvoiceProcessor

# Load environment variables for deployment configuration
load_dotenv()

# --- Configuration ---
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

# --- Validation ---
if not all([PROJECT_ID, LOCATION, STAGING_BUCKET]):
    raise ValueError("Missing required GCP environment variables (PROJECT_ID, LOCATION, STAGING_BUCKET)")

print("🔧 Initializing Vertex AI for deployment...")
print(f"   Project: {PROJECT_ID}")
print(f"   Location: {LOCATION}")

# --- Initialize Vertex AI SDK ---
vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

# --- Deploy the Agent ---
try:
    print("\n🚀 Deploying agent with native Vertex AI authentication...")

    agent_to_deploy = SimpleInvoiceProcessor()

    # NOTE: We have REMOVED the 'engine_environment_variables' parameter.
    # It is no longer needed.
    remote_app = reasoning_engines.ReasoningEngine.create(
        reasoning_engine=agent_to_deploy,
        requirements=[
            # We no longer need google-generativeai, but we do need the vertexai library
            "google-cloud-aiplatform>=1.55.0",
            "pandas",
            "openpyxl",
            "python-dotenv" # Still useful for local testing
        ],
        extra_packages=["./multi_tool_agent"],
        display_name="Simple Invoice Processor (Native Auth)",
        description="Processes invoices using native Vertex AI IAM authentication.",
    )

    print("\n✅ Agent Engine deployed successfully!")
    print("   Agent will use service account credentials, not API keys.")
    print(f"\n📋 New Resource name: {remote_app.resource_name}")
    print(f"🌐 View in Console: https://console.cloud.google.com/vertex-ai/reasoning-engines/locations/{LOCATION}/reasoning-engines/{remote_app.resource_name.split('/')[-1]}?project={PROJECT_ID}")

except Exception as e:
    print(f"\n❌ Deployment failed: {e}")