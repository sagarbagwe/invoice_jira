import os
import base64
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import logging

# Import the class from your agent module
from multi_tool_agent.agent import SimpleInvoiceProcessor

# --- Helper functions to create dummy files for a first-time run ---
def create_dummy_master_data():
    """Creates a dummy master_data.xlsx file if it doesn't exist."""
    master_file = Path("data/master_data.xlsx")
    if not master_file.exists():
        print("Creating dummy master_data.xlsx file...")
        master_file.parent.mkdir(exist_ok=True)
        data = {
            "Service Description": ["Cloud Computing Services", "Professional Consulting"],
            "GL Account": ["651001", "652005"],
            "Tax Code": ["I4", "I4"],
            "Vendor Name": ["Cloud Corp", "Consulting LLC"],
            "Vendor Code": ["V1001", "V1002"]
        }
        pd.DataFrame(data).to_excel(master_file, index=False)
        print(f"Dummy file created at {master_file}")

def create_dummy_pdfs():
    """Create dummy PDF files if they don't exist."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    if not (data_dir / "invoice.pdf").exists():
        print("Creating dummy invoice.pdf...")
        # A minimal dummy PDF content
        (data_dir / "invoice.pdf").write_text("Dummy Invoice for Cloud Corp. Total: $1000")
    if not (data_dir / "jira.pdf").exists():
        print("Creating dummy jira.pdf...")
        (data_dir / "jira.pdf").write_text("Dummy Jira Ticket. Approved by AJohnson.")

# --- Main Local Test Function ---
def main():
    """Main function to run a local test of the SimpleInvoiceProcessor."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Load environment variables from the root .env file
    load_dotenv()

    # Ensure dummy/real files exist for the test
    create_dummy_master_data()
    create_dummy_pdfs()
    
    # Critical check for the API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("\n❌ ERROR: GOOGLE_API_KEY not found.")
        print("Please ensure you have a .env file in the project root with your key.")
        return
    
    try:
        # 1. Load and Base64 encode the files, as the agent expects
        logging.info("Loading and encoding local files for testing...")
        with open("data/invoice.pdf", "rb") as f:
            invoice_b64 = base64.b64encode(f.read()).decode('utf-8')
        with open("data/jira.pdf", "rb") as f:
            jira_b64 = base64.b64encode(f.read()).decode('utf-8')
        with open("data/master_data.xlsx", "rb") as f:
            master_data_b64 = {"master_data.xlsx": base64.b64encode(f.read()).decode('utf-8')}
        
        # 2. Initialize the processor directly
        logging.info("Initializing SimpleInvoiceProcessor...")
        processor = SimpleInvoiceProcessor()
        
        # 3. Call the 'query' method with the encoded data
        logging.info("Calling the processor's .query() method...")
        result = processor.query(
            invoice_b64=invoice_b64,
            jira_b64=jira_b64,
            master_data_b64=master_data_b64
        )
        logging.info("Local processing finished.")
        
        # 4. Print the results for inspection
        print("\n" + "="*20 + " LOCAL TEST RESULTS " + "="*20)
        if "error" in result:
            print(f"An error occurred during processing: {result['error']}")
            if result.get('raw_response'):
                print(f"Raw Response: {result['raw_response']}")
        else:
            print("\n--- Final JSON Data ---")
            print(json.dumps(result.get("json_data", "No JSON data returned."), indent=2))

            print("\n--- Final CSV Data ---")
            print(result.get("csv_data", "No CSV data returned."))
            
        print("\n" + "="*62)

    except Exception as e:
        logging.error(f"A critical error occurred in main.py: {e}", exc_info=True)

if __name__ == "__main__":
    main()