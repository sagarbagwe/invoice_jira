import os
import base64
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import logging

# Import the simple processor
from multi_tool_agent import SimpleInvoiceProcessor

def create_dummy_master_data():
    """Creates a dummy master_data.xlsx file if it doesn't exist."""
    master_file = Path("data/master_data.xlsx")
    if not master_file.exists():
        print("Creating dummy master_data.xlsx file...")
        master_file.parent.mkdir(exist_ok=True)  # Create data directory if it doesn't exist
        data = {
            "Service Description": ["Cloud Computing Services", "Professional Consulting", "Software Licensing"],
            "GL Account": ["651001", "652005", "651002"],
            "GST Rate": ["18%", "18%", "18%"],
            "Tax Code": ["I4", "I4", "I4"],
            "Requestor Name": ["Alice Johnson", "Bob Williams", "Charlie Davis"],
            "Requestor ID": ["AJohnson", "BWilliams", "CDavis"]
        }
        pd.DataFrame(data).to_excel(master_file, index=False)
        print(f"Dummy file created at {master_file}")

def create_dummy_pdfs():
    """Create dummy PDF files if they don't exist."""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Create dummy invoice PDF
    invoice_file = data_dir / "invoice.pdf"
    if not invoice_file.exists():
        print("Creating dummy invoice.pdf...")
        # Create a minimal PDF content
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Dummy Invoice) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
300
%%EOF"""
        invoice_file.write_bytes(pdf_content)
        print(f"Dummy invoice.pdf created at {invoice_file}")
    
    # Create dummy jira PDF
    jira_file = data_dir / "jira.pdf"
    if not jira_file.exists():
        print("Creating dummy jira.pdf...")
        pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 42 >>
stream
BT
/F1 12 Tf
100 700 Td
(Dummy Jira Ticket) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
305
%%EOF"""
        jira_file.write_bytes(pdf_content)
        print(f"Dummy jira.pdf created at {jira_file}")

def main():
    """Main function to run the Invoice Processor Agent."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Load environment variables
    dotenv_path = Path('multi_tool_agent/.env')
    load_dotenv(dotenv_path=dotenv_path)

    # Create dummy files if needed
    create_dummy_master_data()
    create_dummy_pdfs()
    
    # Check if API key is set
    if not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY not found in environment variables.")
        print("Please set your API key in multi_tool_agent/.env file")
        return
    
    try:
        # Load and encode files
        logging.info("Loading and encoding files...")
        with open("data/invoice.pdf", "rb") as f:
            invoice_b64 = base64.b64encode(f.read()).decode('utf-8')
        with open("data/jira.pdf", "rb") as f:
            jira_b64 = base64.b64encode(f.read()).decode('utf-8')
        with open("data/master_data.xlsx", "rb") as f:
            master_data_b64 = {"master_data.xlsx": base64.b64encode(f.read()).decode('utf-8')}
        
        # Initialize processor
        processor = SimpleInvoiceProcessor()
        
        # Process documents
        logging.info("Processing documents...")
        result = processor.process_documents(invoice_b64, jira_b64, master_data_b64)
        
        # Print results
        print("\n" + "="*20 + " PROCESSING RESULTS " + "="*20)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("\n--- Final JSON Data ---")
            if result.get("json_data"):
                print(json.dumps(result.get("json_data"), indent=2))
            else:
                print("No JSON data generated")
            
            print("\n--- Final CSV Data ---")
            if result.get("csv_data"):
                print(result.get("csv_data"))
            else:
                print("No CSV data generated")
                
            print("\n--- Raw AI Response ---")
            print(result.get("raw_response", "No response"))
            
        print("\n" + "="*60)

    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()