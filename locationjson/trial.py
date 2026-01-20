import os
import json
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from loader import load_document
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Prompt to extract structured plan data
extraction_prompt = PromptTemplate(
    input_variables=["content"],
    template="""
You are a construction bid data extractor.

Extract ALL plan pricing information AND location details from this document.

Document Content:
{content}

EXTRACT and return a JSON array with this EXACT format:
[
    {{
        "plan_number": "4101",
        "total_price": 9425.00,
        "system_type": "Gas",
        "tonnage": 3.5,
        "rough_po": 5655.00,
        "trim_po": 3770.00,
        "city": "Fort Worth",
        "state": "TX",
        "zip": "76118",
        "metro_area": "DFW"
    }}
]

LOCATION RULES:
- Extract city, state, and zip if address is present
- If city is Fort Worth, Irving, Dallas, Arlington, Plano, Frisco, Garland, Denton:
  set metro_area = "DFW"
- If address exists but metro area is unclear, set metro_area = null
- If no address exists, set city, state, zip, metro_area = null

GENERAL RULES:
1. Extract EVERY plan you find
2. Use numeric values for prices (no $ symbol)
3. If a field is missing, use null
4. Return ONLY the JSON array
5. Do NOT add extra commentary
6. Capture ALL plans even if there are 50+

JSON Output:
"""
)



def extract_plans_from_file(file_path):
    """Extract all plan data from a single file"""
    print(f"📄 Processing: {os.path.basename(file_path)}")
    
    # Load document
    docs = load_document(file_path)
    
    # Combine all content (for smaller files) or process in chunks
    all_content = "\n\n".join([doc.page_content for doc in docs])
    
    # If content is too large, process in parts
    max_chars = 50000  # Adjust based on model context window
    
    all_plans = []
    
    if len(all_content) > max_chars:
        # Process in chunks
        chunks = [all_content[i:i+max_chars] for i in range(0, len(all_content), max_chars)]
        for i, chunk in enumerate(chunks):
            print(f"  Processing chunk {i+1}/{len(chunks)}...")
            plans = extract_plans_from_content(chunk)
            all_plans.extend(plans)
    else:
        all_plans = extract_plans_from_content(all_content)
    
    # Remove duplicates based on plan_number
    unique_plans = {}
    for plan in all_plans:
        plan_num = plan.get("plan_number")
        if plan_num and plan_num not in unique_plans:
            unique_plans[plan_num] = plan
    
    print(f"  ✅ Extracted {len(unique_plans)} unique plans")
    return list(unique_plans.values())


def extract_plans_from_content(content):
    """Use LLM to extract plans from content"""
    try:
        prompt = extraction_prompt.format(content=content)
        response = llm.invoke(prompt)
        
        # Parse JSON response
        json_str = response.content.strip()
        
        # Clean up response if needed
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        
        plans = json.loads(json_str.strip())
        return plans if isinstance(plans, list) else []
    
    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON parse error: {e}")
        return []
    except Exception as e:
        print(f"  ⚠️ Extraction error: {e}")
        return []


def extract_all_bids(data_folder="./data"):
    """Extract plan data from all bid files"""
    all_bids = {}
    
    for file in os.listdir(data_folder):
        file_path = os.path.join(data_folder, file)
        
        if os.path.isdir(file_path):
            continue
        
        if file.endswith(('.pdf', '.xlsx', '.xls')):
            plans = extract_plans_from_file(file_path)
            all_bids[file] = plans
    
    return all_bids


def save_extracted_data(all_bids, output_path="./extracted_bads.json"):
    """Save extracted bid data to JSON"""
    with open(output_path, "w") as f:
        json.dump(all_bids, f, indent=2)
    print(f"\n💾 Saved extracted data to {output_path}")


if __name__ == "__main__":
    print("="*60)
    print("BID DATA EXTRACTION")
    print("="*60)
    
    all_bids = extract_all_bids()
    save_extracted_data(all_bids)
    
    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    for file_name, plans in all_bids.items():
        print(f"📄 {file_name}: {len(plans)} plans extracted")

