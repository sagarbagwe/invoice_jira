import argparse
import base64
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from multi_tool_agent.agent import SimpleInvoiceProcessor


def main():
    parser = argparse.ArgumentParser(description="CLI for Invoice Jira Processor")
    parser.add_argument("--invoice", type=str, default="data/invoice.pdf", help="Path to invoice PDF")
    parser.add_argument("--jira", type=str, default="data/jira.pdf", help="Path to jira PDF")
    parser.add_argument("--master-data", type=str, default="data/master_data.xlsx", help="Path to master data XLSX")
    args = parser.parse_args()

    load_dotenv()

    inv_path = Path(args.invoice)
    jira_path = Path(args.jira)
    master_path = Path(args.master_data)

    if not inv_path.exists() or not jira_path.exists() or not master_path.exists():
        print("Error: One or more input files do not exist.")
        sys.exit(1)

    with open(inv_path, "rb") as f:
        invoice_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(jira_path, "rb") as f:
        jira_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(master_path, "rb") as f:
        master_data_b64 = {master_path.name: base64.b64encode(f.read()).decode("utf-8")}

    processor = SimpleInvoiceProcessor()
    result = processor.query(
        invoice_b64=invoice_b64,
        jira_b64=jira_b64,
        master_data_b64=master_data_b64
    )
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
