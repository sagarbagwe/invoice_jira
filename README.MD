
# AI-Powered Invoice Processor on Google Cloud

This project demonstrates an end-to-end workflow for building, deploying, and interacting with a custom AI agent on Google Cloud. The agent is designed to process procurement documents (PDF invoices and Jira tickets), extract structured data using a Gemini model, enrich it with master data from an Excel file, and return the final result in JSON and CSV formats.

The core of the project is a Python class deployed as a **Vertex AI Reasoning Engine**, which is then linked as a tool to a conversational **Vertex AI Agent Builder** application.

## Project Workflow

1.  **Local Development:** A Python class (`SimpleInvoiceProcessor`) encapsulates all the logic for file processing and calling the Gemini model.
2.  **Local Testing:** A `main.py` script allows for rapid local testing of the agent's logic before deployment.
3.  **Deployment:** A `deploy.py` script packages the Python code and deploys it as a secure, scalable Reasoning Engine on Vertex AI.
4.  **Integration:** A `cURL` command links the deployed Reasoning Engine as a custom tool to a conversational app in Agent Builder.
5.  **Interaction:** A final `interact_with_assistant.py` script shows how to call the fully integrated system, passing file data and receiving the processed output.

## Project Structure

```
invoice_agent_project/
├── data/
│   ├── invoice.pdf
│   ├── jira.pdf
│   └── master_data.xlsx
├── multi_tool_agent/
│   ├── __init__.py
│   └── agent.py
├── .env
├── .gitignore
├── deploy.py
├── main.py
├── query_agent.py
├
└── requirements.txt
```

-----

## 1\. Local Setup and Testing

Before deploying, test the agent's logic on your local machine.

### Prerequisites

  * Python 3.9+
  * A Google Cloud Project
  * Authenticated `gcloud` CLI (`gcloud auth application-default login`)

### Setup Steps

1.  **Clone the Repository** and navigate into the project directory.

2.  **Create and Activate a Virtual Environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows: .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Create Environment File for Local Testing:**
    Create a file named `.env` in the project root. The `main.py` script uses this to load your API key for local tests.

    ```
    # .env
    GOOGLE_API_KEY="your-google-ai-studio-api-key"
    ```

5.  **Run the Local Test:**
    Execute the `main.py` script. It will create dummy files in the `data/` folder if they don't exist and run the full processing logic locally.

    ```bash
    python main.py
    ```

    If this runs successfully, your agent's code is correct.

-----

## 2\. Deployment to Vertex AI Reasoning Engine

Deploy the agent to a secure, scalable environment.

### Cloud Prerequisites

1.  **Enable APIs:**
    ```bash
    gcloud services enable aiplatform.googleapis.com discoveryengine.googleapis.com
    ```
2.  **Create a Cloud Storage Bucket:** This is used for staging deployment files.
    ```bash
    # Replace with your own unique bucket name
    gsutil mb -p your-gcp-project-id -l us-central1 gs://your-unique-staging-bucket
    ```

### Deployment Steps

1.  **Update Your `.env` file:**
    Add your Google Cloud project details to the `.env` file. The `deploy.py` script needs these.

    ```
    # .env
    GOOGLE_API_KEY="your-google-ai-studio-api-key"
    GOOGLE_CLOUD_PROJECT="sadproject2025"
    GOOGLE_CLOUD_LOCATION="us-central1"
    STAGING_BUCKET="gs://your-unique-staging-bucket"
    ```

2.  **Run the Deployment Script:**
    This script packages your `multi_tool_agent` code and deploys it. It uses native IAM authentication, so no API key is needed on the server.

    ```bash
    python deploy.py
    ```

3.  **Save the Resource Name:**
    Upon successful completion, the script will print the full resource name of your deployed agent. **Copy this name.** You will need it for the next step.
    `📋 New Resource name: projects/113207776071/locations/us-central1/reasoningEngines/5553140650687332352`

-----

## 3\. Connecting to Agent Builder

Link your deployed backend engine to a conversational frontend app.

### Setup Steps

1.  **Create an Agent Builder App:**

      * Navigate to **Vertex AI -\> Agent Builder** in the Google Cloud Console.
      * Click **"+ Create a new app"** and choose the **Chat** type.
      * Give it a name (e.g., "Invoice Assistant") and complete the setup.

2.  **Find Your App ID:**

      * From the Agent Builder "Apps" page, find your newly created app in the list.
      * Copy the value from the **ID** column. This is your App ID (e.g., `invoice-data-extraction-se_1754424308927`).

3.  **Grant IAM Permissions:**
    The Agent Builder service needs permission to call your Reasoning Engine.

      * Navigate to the **IAM & Admin** page in the Cloud Console.
      * Click **+ GRANT ACCESS**.
      * In "New principals", add the service account: `service-<YOUR_PROJECT_NUMBER>@gcp-sa-discoveryengine.iam.gserviceaccount.com`.
      * Assign the **`Vertex AI User`** role.
      * Click **SAVE**.

4.  **Link the Services with `cURL`:**
    Run the following command in your terminal. Replace `PASTE_YOUR_APP_ID_HERE` with the ID you copied.

    ```bash
    curl -X POST \
         -H "Authorization: Bearer $(gcloud auth print-access-token)" \
         -H "Content-Type: application/json" \
         -H "X-Goog-User-Project: sadproject2025" \
         "https://discoveryengine.googleapis.com/v1alpha/projects/sadproject2025/locations/global/collections/default_collection/engines/PASTE_YOUR_APP_ID_HERE/assistants/default_assistant/agents" \
         -d '{
              "displayName": "Invoice and Jira Processor",
              "description": "An agent that processes invoice and Jira PDFs using master data via a Reasoning Engine.",
              "adk_agent_definition": {
                "provisioned_reasoning_engine": {
                  "reasoning_engine": "projects/113207776071/locations/us-central1/reasoningEngines/5553140650687332352"
                }
              }
            }'
    ```

    A successful response will show `"state": "ENABLED"`.

-----

