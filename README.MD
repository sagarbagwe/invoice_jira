# AI-Powered Invoice and Document Processor

This project provides a simple yet powerful command-line application for processing procurement documents. It uses Google's Gemini Pro 1.5 model to extract structured data from a PDF invoice and a corresponding PDF Jira ticket. The extracted data is then enriched using information from a master data Excel file and outputted in both JSON and CSV formats.

The script is designed for easy setup and use, automatically creating dummy input files if they don't exist, allowing you to test the pipeline immediately.

## Features

  - **Direct Google AI Integration**: Uses the `google-generativeai` Python SDK directly, with no complex Agent Development Kit (ADK) required.
  - **Multi-Document Processing**: Simultaneously analyzes a PDF invoice and a PDF Jira ticket.
  - **Master Data Enrichment**: Cross-references a master data Excel file to look up critical information like GL Accounts, Tax Codes, and Requestor IDs.
  - **Structured Output**: Generates clean, structured output in both JSON and CSV formats, ready for downstream systems.
  - **Automatic File Generation**: Creates dummy `invoice.pdf`, `jira.pdf`, and `master_data.xlsx` files on the first run for quick and easy testing.
  - **Secure API Key Management**: Uses a `.env` file to securely manage your Google API key.

## Project Structure

```
invoice_agent_project/
├── data/
│   ├── invoice.pdf          # Your invoice PDF (or auto-generated dummy)
│   ├── jira.pdf             # Your Jira ticket PDF (or auto-generated dummy)
│   └── master_data.xlsx     # Your master data file (or auto-generated dummy)
├── multi_tool_agent/
│   ├── __init__.py          # Makes the agent a callable package
│   ├── agent.py             # Core logic for the AI agent and document processing
│   └── .env                 # Your environment variables (e.g., API Key)
├── main.py                  # Main entry point to run the application
└── requirements.txt         # List of Python dependencies
```

## Setup and Installation

Follow these steps to get the project up and running on your local machine.

### 1\. Prerequisites

  - Python 3.8 or higher
  - A Google AI Studio API Key. You can get one from [Google AI Studio](https://aistudio.google.com/).

### 2\. Clone the Repository

Clone this project to your local machine.

```bash
git clone <your-repository-url>
cd invoice_agent_project
```

### 3\. Set up a Virtual Environment (Recommended)

It's best practice to create a virtual environment to manage project dependencies.

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 4\. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5\. Configure Your Environment File

You need to provide your Google API key.

1.  Navigate to the `multi_tool_agent/` directory.
2.  Create a file named `.env`.
3.  Add your API key to the file as shown below:

**File: `multi_tool_agent/.env`**

```
GOOGLE_API_KEY=YOUR_ACTUAL_API_KEY_HERE
```

Replace `YOUR_ACTUAL_API_KEY_HERE` with the key you obtained from Google AI Studio.

## Usage

Once the setup is complete, you can run the application from the project's root directory.

### Running the Application

Execute the `main.py` script from your terminal:

```bash
python main.py
```

### What Happens on the First Run?

  - The script will check for the existence of `invoice.pdf`, `jira.pdf`, and `master_data.xlsx` in the `data/` directory.
  - If any of these files are missing, it will automatically create simple, dummy versions of them. This allows you to test the end-to-end flow without needing to provide your own files initially.

### Using Your Own Files

To process your own documents, simply replace the dummy files in the `data/` directory with your actual files, ensuring they have the same names:

  - `data/invoice.pdf`
  - `data/jira.pdf`
  - `data/master_data.xlsx`

### Expected Output

After a successful run, the script will print the following to your console:

1.  **Final JSON Data**: The structured data extracted and enriched by the AI.
2.  **Final CSV Data**: The same data formatted as a CSV string.
3.  **Raw AI Response**: The complete, unparsed text response from the Gemini model for debugging purposes.

Example Output:

````
==================== PROCESSING RESULTS ====================

--- Final JSON Data ---
{
  "Document Type": "ZNID",
  "PO Number": "PO-2025-12345",
  "Line Item Number": "10",
  ...
}

--- Final CSV Data ---
Document Type,PO Number,Line Item Number,...
ZNID,PO-2025-12345,10,...

--- Raw AI Response ---
```json
{
  "Document Type": "ZNID",
  "PO Number": "PO-2025-12345",
  "Line Item Number": "10",
  ...
}
````

\============================================================

```
```