import os
import pandas as pd
import google.generativeai as genai
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional
import base64
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleInvoiceProcessor:
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        
    def lookup_master_data(
        self, 
        file_key: str,
        lookup_column: str,
        lookup_value: str,
        return_column: str,
        master_data_dfs: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """Lookup data in master files."""
        try:
            if file_key not in master_data_dfs:
                return {"error": f"Master data key '{file_key}' not found. Available keys: {list(master_data_dfs.keys())}"}
            
            df = master_data_dfs[file_key]
            lookup_column, return_column = lookup_column.strip(), return_column.strip()
            
            if lookup_column not in df.columns:
                return {"error": f"Column '{lookup_column}' not found in {file_key}. Available: {list(df.columns)}"}
            if return_column not in df.columns:
                return {"error": f"Column '{return_column}' not found in {file_key}. Available: {list(df.columns)}"}
            
            result = df[df[lookup_column].astype(str).str.contains(lookup_value, case=False, na=False)]
            if not result.empty:
                return {"result": str(result.iloc[0][return_column]), "status": "success"}
            else:
                return {"error": f"Value '{lookup_value}' not found in {file_key} column '{lookup_column}'", "status": "error"}
        except Exception as e:
            return {"error": f"Error during lookup in '{file_key}': {e}", "status": "error"}

    def generate_output_csv(self, invoice_data_json: str) -> Dict[str, Any]:
        """Generate CSV from JSON data."""
        try:
            data = json.loads(invoice_data_json)
            if isinstance(data, dict):
                data = [data]
            
            df = pd.DataFrame(data)
            return {
                "csv_data": df.to_csv(index=False),
                "json_data": data,
                "message": "Successfully generated CSV",
                "status": "success"
            }
        except Exception as e:
            return {"error": f"Error generating CSV: {e}", "status": "error"}

    def load_master_data(self, master_data_bytes_dict: Dict[str, bytes]) -> Dict[str, pd.DataFrame]:
        """Load master data from bytes."""
        master_data = {}
        for file_name, file_bytes in master_data_bytes_dict.items():
            try:
                with pd.ExcelFile(file_bytes) as excel_file:
                    for sheet_name in excel_file.sheet_names:
                        df = pd.read_excel(excel_file, sheet_name=sheet_name)
                        df.columns = df.columns.str.strip()
                        key = f"{Path(file_name).stem}_{sheet_name}" if len(excel_file.sheet_names) > 1 else Path(file_name).stem
                        master_data[key] = df
            except Exception as e:
                logger.error(f"Error loading {file_name}: {e}")
        return master_data

    def process_documents(self, invoice_b64: str, jira_b64: str, master_data_b64: Dict[str, str]) -> Dict[str, Any]:
        """Process invoice and jira documents."""
        try:
            # Decode files
            invoice_bytes = base64.b64decode(invoice_b64)
            jira_bytes = base64.b64decode(jira_b64)
            master_data_bytes_dict = {name: base64.b64decode(data) for name, data in master_data_b64.items()}
            
            # Load master data
            master_data_dfs = self.load_master_data(master_data_bytes_dict)
            if not master_data_dfs:
                return {"error": "No master data could be loaded."}
            
            logger.info(f"Loaded master data keys: {list(master_data_dfs.keys())}")
            
            # Save PDFs temporarily for processing
            with tempfile.TemporaryDirectory() as temp_dir:
                invoice_path = Path(temp_dir) / "invoice.pdf"
                jira_path = Path(temp_dir) / "jira.pdf"
                invoice_path.write_bytes(invoice_bytes)
                jira_path.write_bytes(jira_bytes)
                
                # Upload files to Gemini
                invoice_file = genai.upload_file(invoice_path)
                jira_file = genai.upload_file(jira_path)
                
                # Create prompt with master data context
                master_data_context = ""
                for key, df in master_data_dfs.items():
                    master_data_context += f"\n\n**{key} Master Data:**\n"
                    master_data_context += df.head().to_string()
                
                prompt = f"""
                **ROLE & GOAL:**
                You are an AI agent specializing in procurement data processing. Your task is to extract information from the provided documents (a Tax Invoice and a Jira Ticket), and then output the final, complete data in JSON format.

                **AVAILABLE DOCUMENTS:**
                - Tax Invoice PDF and Jira Ticket PDF are attached
                - Master Data: {master_data_context}

                **CRITICAL REQUIREMENTS:**
                1. **Use VENDOR CODE, not vendor name.**
                2. **Format dates as DD.MM.YYYY.**
                3. **Use 18% GST Tax Code** (Expect 'I4').
                4. **Generate a purchase order number.**

                **INSTRUCTIONS:**
                1. **Extract Data:** Carefully read all provided documents.
                2. **Use Master Data:** Cross-reference the master data above to find GL Accounts, Tax Codes, Requestor IDs, etc.
                3. **Construct Final Data:** Assemble all data into the specified JSON schema.

                **OUTPUT JSON SCHEMA:**
                {{
                    "Document Type": "ZNID",
                    "PO Number": "",
                    "Line Item Number": "10",
                    "Vendor": "",
                    "Document Date": "",
                    "Payment Terms": "P000",
                    "Purchasing Organisation": "1001",
                    "Purchase Group": "S05",
                    "Invoice": "",
                    "SAP Database": "",
                    "Jira": "",
                    "Agreement": "",
                    "Company Code": "1001",
                    "Validity Start Date": "",
                    "Validity End Date": "",
                    "WO Header Text": "",
                    "Account Assignment": "",
                    "Item Category": "",
                    "Short Text": "",
                    "Delivery Date": "",
                    "Plant": "DS01",
                    "Requisitioner": "",
                    "Service Number": "",
                    "Service Quantity": "",
                    "Gross Price": "",
                    "Cost Center": "",
                    "WBS": "",
                    "Tax Code": "",
                    "Material Group": "",
                    "no of days": "",
                    "Requestor": "",
                    "Control Code": "",
                    "GL Account": "",
                    "UOM": "",
                    "Order Number": "",
                    "Text 1": ""
                }}

                Please provide ONLY the JSON output, no additional text.
                """
                
                # Generate response
                response = self.model.generate_content([prompt, invoice_file, jira_file])
                
                # Parse JSON response
                try:
                    # Clean the response text (remove any markdown formatting)
                    response_text = response.text.strip()
                    if response_text.startswith('```json'):
                        response_text = response_text[7:]
                    if response_text.endswith('```'):
                        response_text = response_text[:-3]
                    response_text = response_text.strip()
                    
                    json_data = json.loads(response_text)
                    csv_result = self.generate_output_csv(json.dumps(json_data))
                    
                    return {
                        "message": "Processing complete.",
                        "raw_response": response.text,
                        "json_data": json_data,
                        "csv_data": csv_result.get("csv_data"),
                        "master_data_keys": list(master_data_dfs.keys())
                    }
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing error: {e}")
                    return {
                        "message": "Processing complete but JSON parsing failed.",
                        "raw_response": response.text,
                        "error": f"Could not parse JSON from response: {e}"
                    }
                
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            return {"error": str(e)}