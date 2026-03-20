A proof-of-concept demonstrating how local LLMs and deterministic logic can automate product master data creation within a governed MDM workflow — reducing manual data entry while maintaining human oversight and data quality at the point of data creation.

 > **Note:** This is a POC validating technical feasibility, not a production system. The governance design and standardized data architecture it builds upon were developed during a prior role as Business Analyst on an MDMS centralization initiative. Every data governance initiative must be tailored to the organization's structure, processes, and specific requirements — there is no one-size-fits-all solution.


## Why This Project Exists

---

In food manufacturing, product master data — product names, product attributes, unit measurements, storage conditions — is the foundation that every downstream departmental system depends on. Sales orders reference it, demand forecasts are built on it, production systems consume it, and financial reports aggregate it.

When this data is incomplete, inconsistent, or trapped in departmental silos, the consequences cascade: departments can't get the product information they need, forecasts run on stale attributes, financial reports reflect outdated configurations, and nobody trusts the MDM system — consequently, they maintain their own shadow versions of product master data in separate systems or manual spreadsheets.

This POC demonstrates that AI can automate the most labor-intensive parts of product master data creation — parsing unstructured product specifications into standardized fields and generating department-specific data views — while keeping humans in the loop for quality assurance before any data interfaces to downstream ERPs.

---

## The Business Problem

### Decentralized Master Data

The organization's MDM system existed but operated at roughly 20% of its potential. It stored only rudimentary data — product code, product name, and basic attributes — while 80% of product master data was maintained directly in downstream departmental systems, each with its own formats, conventions, and workflows.

![image.png](attachment:fe95d946-d1a5-4da3-b3cf-a8f79257daf4:image.png)

![image.png](attachment:8148d67e-7c9d-4cd9-af42-c0640f096b69:image.png)

## The Consequences

- **No single source of truth** — the same product had different attribute values across different departmental systems
- **Redundant manual entry** — the same field (e.g., unit of measurement. groupings) was re-entered by multiple departments in multiple systems.
- **Shadow data proliferation** — with MDM unable to serve their needs, departments resorted to maintaining their own product master data for specific purposes
- **Manual coordination overhead** — departments obtained product specifications via manual mediums (email, phone calls, and form hand-offs) from the initial master data creator rather than systematically from MDM
- **No change propagation** — when a user updated product master data, not all downstream systems were automatically notified, leading to stale and outdated data.
- **Format divergence** — with prolonged disconnects and shadow master data, departmental formats diverged, making standardization and mapping logic difficult when attempting to connect downstream data back to MDM.

## Why This Must Be Addressed

The longer product master data remains decentralized, the harder it becomes to fix since every new product created through the fragmented process adds another record that exists in multiple systems with no governed connection back to its source. As shadow master data compounds — departments build processes, reports, and workflows around their own versions, making future consolidation increasingly complex and costly.

Meanwhile, the organization's investment in downstream data infrastructure — data lakes, warehouses, catalogs, and reporting tools — delivers diminishing returns when the master data feeding those systems is incomplete or inconsistent at its origin. **No amount of downstream cleansing or cataloging can compensate for data that was flawed at the point of creation and the cost of inaction grows exponentially over time.**

---

## **Solution: Master Data Centralization**

![image.png](attachment:27691006-316b-4d08-8a88-d94b3b3fb50a:image.png)

- **Data Centralization** — migrate all downstream product master data to a single platform (MDM). Standardize fields, block create/modify in downstream systems, consume from MDM only.
- **Process Standardization** — design end-to-end workflow in MDM with clear roles, approval routes, optimized data entry sequence, and data validation at source.
- **Result:** One platform, complete data, standardized process.

---

## Methodology

**The governance initiative followed a bottom-up discovery approach:**

1. **Business understanding** — mapped the end-to-end new product development process from ideation to commercialization, identifying which systems are used, which departments are involved, and at which stages.
2. **Pain point collection** —  engaged with departmental users across functions (Sales, Marketing, Manufacturing, Analytics) to identify what data they actually need from product master data and where current processes fail to deliver it.
3. **Data lineage mapping** — starting from data consumption issues in departmental ERPs, traced each problematic data point backwards through every document, system, and touchpoint to its initial source — identifying where data gets lost, re-entered, or corrupted along the way.
4. **Process variance analysis** — compared product creation workflows across business units (fresh/raw, processed/RTE, export) to identify inconsistencies in how master data is created, maintained, and distributed.
5. **Canonical data model design** — designed a standardized MDM schema that serves all departmental consumers, not just the initial data creator. This included defining common fields, department-specific fields, format standards, and cross-view mappings.
6. **Stakeholder consultation** — worked directly with data owners in each department to design data entry interfaces, validate field definitions, and ensure the standardized format meets their operational needs.

> **Key insight:** Starting from downstream pain points (step 2-3) rather than top-down policy ensured the governance design addressed real operational problems. **Departments adopted the solution because it solved their daily frustrations, not because a policy mandated it.**
> 

---

## **Challenges Encountered During the Centralization Initiative.**

**Centralizing product master data into MDM is the right solution** — but the implementation surfaced two critical challenges that a governance-and-process approach alone could not fully resolve:

1. **Centralizing master data means the data owner (typically the team with firsthand product knowledge) must now maintain significantly more fields in MDM:** 
    - Expanding from 5-10 basic fields to 25-30 comprehensive fields covering all departmental needs.
    - Even though this data was always their responsibility in principle, the perceived increase in workload created adoption resistance.
    - Users questioned whether the new systematic workflow would slow down product creation compared to their existing informal methods.

1. **Data Standardization and Granularity Mismatch**
    
    Designing a universal MDM data model that serves all departments revealed a fundamental tension: 
    
    - storing data too generically makes it useless for specialized departments that need precise values, while storing it too granularly overwhelms the data owner with fields they shouldn't need to manage.
    - Different departments required different levels of detail from the same source attribute — and maintaining every variation manually in a single system was not practical.
    - Different departments needed different levels of detail from the same source field:
        - **MDM stored :** `storage_type: "CHILL"`
        - **Manufacturing needed:** `"CHILL/FROZEN"` (sufficient)
        - **SCM needed:** `"FROZEN" and "-18°C ± 2°C"` (specific temperature with tolerance)
        - **Sales needed:** `"AMBIENT/CHILL/FROZEN"` (commercial classification)

### This project explores whether AI can bridge that gap:

- **For user resistance:** Can AI pre-fill expanded fields from minimal inputs, shifting the experience from data entry to data validation?
- **For standardization:** Can AI translate generic MDM data into department-specific formats using contextual reasoning?
- **For accountability:** Can this be done while keeping humans in the loop — ensuring every record is reviewed before it interfaces to any downstream system?

If feasible, AI transforms the governed MDM workflow from a burden into the **path of least resistance — the key to sustainable adoption.**

## Solution Architecture

![image.png](attachment:47d16e65-0553-43f9-ace1-d739f7d0141c:image.png)

**Design principle: Deterministic + Rules First, LLM Second**

- The majority of fields are generated through deterministic YAML-configured mapping — reliable, auditable, and zero-cost. **LLMs are only used for fields that require contextual reasoning.** This minimizes AI risk while maximizing governance auditability.

---

## Technology Context: LangGraph

This project uses [LangGraph](https://github.com/langchain-ai/langgraph) as its orchestration framework — a library for building stateful, multi-step workflows as directed graphs with conditional routing. It was chosen because the master data workflow requires conditional branching (product type determines which views to create), sequential dependencies (Sales can't proceed until Production is done), and mixed processing (some nodes use LLM, others are deterministic).

### Composable Architecture

| Level | Location | What It Does |
| --- | --- | --- |
| **Master Graph** | `master_workflow.py` | Orchestrates the full pipeline — mirrors the to-be master data workflow |
| **View Subgraphs** | `agent_src/<dept>_agent/` | Each department's self-contained parsing, transformation, and field generation logic |
| **Department Configs** | `agent_config/<dept>_config/` | Department-tailored mapping rules, field definitions, and LLM context |

Each level is independently editable. Adding a new departmental view means creating a new subgraph and config — existing components are untouched.

> **Design mirror:** This composable architecture reflects the real governance model — each department owns its data domain independently, while the master graph centrally orchestrates the workflow and encodes organizational dependencies.
> 

---

## Technical Components

> **Scope:** The components below represent the AI processing layers developed in this POC (green boxes in the architecture diagram). Human review interfaces and ERP integration are systems implementation concerns outside this project's scope.
> 

## Document Extraction (VLM)

**Location:** `vlm_extractor/doc_extract.py`

1. **What it does:** Extracts structured data from PDF/scanned product specification documents containing product attributes locked in visual layouts — tables, headers, specification blocks — that simple text parsing (OCR) would have difficulty handling.
2. **Output:** Raw input CSV with extracted fields ready for pipeline processing.
3. **How it works:**
    1. Per-business-unit YAML templates define bounding box regions on specification documents( **Location:** `vlm_extractor/vlm_doc_template.yaml`
    2. Local VLM (Qwen3-VL via Ollama) processes each cropped document region with zone-specific prompts
    3. `field_mapping` configuration flattens region outputs into standardized fields
    4. Exports to CSV as structured columns from previously unstructured data

```yaml
# yaml. template  
  doc_type5:
    doc_info_business_unit: chicken
    page_width: 2858 #Total Width and Height of the document
    page_height: 4169

    field_mapping: #Output values
      product_name: [product_desc, product_name]
      customer: [product_desc, customer]
      spec_no: [product_desc, spec_no]
      Channel: [product_desc,channel]

    regions: #Regions for VLM to focus on
      product_desc: 
        bbox: [70, 251, 2839, 1030] #Cropped area of the document
        prompt: | 
          Extract the following informati
            1. Product Name: <string>
            2. Customer Name: <string>
            3. Spec/Sample No: <string>
            4. Channel: <if have multiple channel compile a list>
        fields: [product_name, customer, spec, channel]

      packaging: 
        bbox: [55, 251, 2844, 1025]
        prompt: | 
          Extract the packaging detail text
        fields: [packing_detail]
```

**Snippet of function to extract document regions:**

```python
def extract_region(b64, prompt, fields):
    field_template = {f: None for f in fields}
    prompt = f"""{prompt}
Return ONLY valid JSON with exactly these keys: {list(fields)}
If a value is not found, use null.
No explanation, no markdown fences.

Example format: {json.dumps(field_template, ensure_ascii=False)}"""
    
    response = ollama.chat(model='qwen3-vl:8b',messages= [{
        'role':'user',
        'content': prompt,
        'images': [b64]
        }])
    result = response['message']['content']
    return json.loads(result)
```

**Sample Output:**

```sql
{'_template': 'doc_type5',
 '_source': 'npd-master-data-poc\\vlm_extractor\\vlm_docs_samples\\test5.png',
  'product_name': 'SUPERWING CHICKEN BONELESS WINGS',
   'customer': 'SuperWing',
    'spec_no': '111SPP2FR',
      'packing_detail': '1 kgs/bag x 10 bags/carton (NW 10 kgs/carton)',
        'channel': ['Food Service', 'OEM']}
```

## Data Processing Pipeline

## Processing Within Each Subgraph

Each view subgraph uses the same three-tier processing model, but the specific rules and context are tailored per department:

- **Tier A — Deterministic Mapping (majority of fields):** Direct value lookup from the department's YAML config section. Same input always produces same output. Zero AI.
- **Tier B — Rule-Based Transformation (some fields):** Conditional logic, unit conversions, format transformations defined in config. Deterministic but with business rules.
- **Tier C — LLM-Assisted Contextual Generation (few fields only):** For fields where the output requires interpreting data through the department's specific context. The LLM is loaded with that department's context from the YAML config to generate appropriate values. These fields are flagged for human review.

**Design principle**

- LLMs are only invoked for fields that cannot be resolved by mapping or rules. Most fields in every subgraph are Tier A or B — deterministic, auditable, and zero-cost. This keeps AI risk contained to the genuinely ambiguous cases.

## AI Layer 1: Basic Data Processing

**Subgraph Name:**  Basic View

**Location:** `vlm_extractor/basic_parsers`

Takes raw extracted data and parses it into standardized basic product master data — the core record all departmental views build upon. Demonstrates all three processing tiers:

- **Tier A (Deterministic):** Shelf life extraction
- **Tier B (Rule-Based):** Plant name resolution
- **Tier C (LLM-Assisted):** Packing text parsing, product attribute classification

**Output:** Pre-populated basic fields, ready for human review.

### Developed Parsers

**1. Shelf Life Parser** (`shelflife_parse.py`) — **Tier A**

Simple extraction of numeric value and time unit. No LLM needed.

```python
Input:  "18 months"
Output: { shelf_life_day: 540 }

Input:  "270 days"
Output: { shelf_life_day: 270 }
```

**2. Plant Matcher** (`plant_parse.py`) — **Tier B**

Uses Thai province/district lookup to narrow candidates, then fuzzy matching for final resolution.

```python
Input =   "Bkk Factory 1"
#Step 1: Province lookup → narrows to Bangkok region plants
#Step 2: Fuzzy match → resolves to plant code
Output: { plant_code: "1001", plant_name: "Bangkok Plant 1" }
```

**3. Unit Measurement Parser** (`llm_um_parse.py`) — **Tier C**

Packing formats vary too widely for rules. Stores curated examples of existing formats with correct field mappings; LLM adjusts parsing by learning from reference rather than rigid rules.

```python
Input =  `"1kg per pack and 12 pack in 1 carton"`
Output: {
  packing_unit: "pack"
  packing_weight: "1kg"
  inner_pack_qty: 12
  outer_container: "carton"
```

**4. Attribute Processing** (three-stage pipeline) — **Tier C**

Classifies 6 product attribute fields (PG1-PG6) using progressive narrowing:

- **This uses a combined approach:**
    - Curated samples of existing product master data are retrieved from the based on embedding similarity between the new product name and an existing sample pool.
    - The top similar products serve as reference context.
    - LLM reads through this context to determine whether any attributes should differ from the reference

```python
Input: {
    product_name: "SUPERWING CHICKEN BONELESS WINGS",
    business_unit: "chicken",
    product_type: "chicken further",
    temp: "FROZEN"
}

# Stage 1 — Hard filter: narrow by business_unit + product_type
Candidates: 2,847 → 312 

# Stage 2 — Embedding match: find most similar product names
Top matches: [
    "CHICKEN BONELESS WING SPICY"    (score: 0.91),
    "CHICKEN BONELESS NUGGET"            (score: 0.84),
    "CHICKEN BREAST STRIP GRILLED"       (score: 0.72)
]

# Stage 3 — LLM reranking: read basic view of top matches, determine final classification
LLM Output: {
    pg1: "WHOLE S",
    pg2: "WING",
    pg3: "MAIN PRODUCT",
    pg4: "BAG",
    pg5: "FROZEN",
    pg6: "CHICKEN FURTHER"
}
```

---

### Human Review Gate 1

Data owner reviews/adjust AI-generated basic data before departmental views are generated. 

Basic data is the foundation all downstream views build upon — an uncorrected error here propagates everywhere. **Approve → proceeds to departmental view generation.**

---

## AI Layer 2: Departmental View Generation

Takes approved basic data (and dependent view outputs) to generate pre-filled departmental views. Each department's config defines its specific field requirements, mapping rules, and LLM context.

**Output:** Pre-populated departmental views (Production, Sales, SCM), ready for department user review.

## **Developed SubGraph Example**: Sales View

**Source:** `agent_src/sales_agent/`

**Config:** `agent_config/sales_config/`

**The Sales view demonstrates all three processing tiers within a single subgraph:**

| **File** | **Purpose** |
| --- | --- |
| sales_state.py | `SalesState` TypedDict — defines input (basic MDM data) and output fields (POS name, unit measurements, shelf life, tax type) | |
| sales_nodes.py | Node functions — each handles one field or field group |
| sales_workflow.py | Graph construction — node sequence, conditional edges based on product characteristics |
| sales_util.py | Utilities — loads YAML configs, unit conversion lookups, LLM prompt construction |

**The Sales view subgraph shows the full spectrum of the three-tier approach in a single, real workflow:**

| Node | Tier | Method | Why This Tier |
| --- | --- | --- | --- |
| Shelf Life | A — Deterministic | Direct copy from basic data | Value already exists, no transformation needed |
| Unit Measurement | B — Rule-Based | Conditional logic + YAML mapping | Complex but predictable rules based on product type |
| POS Name | C — LLM-Assisted | LLM with config-defined constraints | Requires contextual compression judgment |

**Tier A — Deterministic:** Shelf Life

- The simplest case — directly copies a value from the approved basic data with no transformation:

```python
def get_shelf_life_day(state:SalesState):
    mdm = state['mdm_data'] #Basic Data as dictionary 
    shelf_life_day = mdm.get('shelf_life_day', None)
    return {"shelf_life_day": shelf_life_day}
```

**Tier B — Rule-Based:** Unit Measurement Calculation

- This is where the Sales view does the heavy lifting. Unit measurements are the exact problem identified during the governance initiative — Sales needs picking units, sales units, purchasing units, and equivalents, all derived from the basic packing data through business rules.
- The `sales_workflow.py` conditionally routes based on whether the product is sold by weight or by standard units.

```python
#Example of routing 
def agent_routing_isweight(state: SalesState):
    mdm = state['mdm_data']
    is_weight = mdm.get('is_weighted', None)
    if is_weight is True:
        return "node_fg_weight_unit"
    else:
        return "node_fg_std_unit"
```

- For standard products, the node applies deterministic mapping logic — reading unit codes from basic data and converting them via YAML config lookup in :

```python
def load_reference_data(filename:str):
    filepath = os.path.join('agent_config','sales_config', filename)
    try: 
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            #print(f'{filename} loaded') #Checkpoints
        return data
    except Exception as e:
        print(e)
        return None
    
def get_reference():
    return {
        'sales_mapping' : load_reference_data('mapping_config.yaml'),
        'pos_name_config': load_reference_data('abbv.yaml')
    }
    
def unit_conversion(unit: str):
    um_mapping = get_reference()['sales_mapping']['um_sap_to_local']
    if unit in um_mapping:
        return um_mapping.get(unit)
    else:
        return f"No mapping for SAP Unit: {unit}"
```

```python
#yaml file
um_sap_to_local:
  PAC: "001-pack"
  KG: "002-kilogram"
  BOX: "003-box"
  EA: "004-each"
  BAG: "005-bag"
  CS: "006-case"

```

The node then populates all Sales unit fields through business rules 

```python
# Standard FG with master carton
result['pack_um'] = unit_conversion(mdm.get('inner_container_um'))
result['sales_um'] = unit_conversion(mdm.get('master_container_um'))
result['pack_equi'] = mdm.get('inner_weight_max')
result['sales_equi'] = mdm.get('inner_per_master_qty')

output = {'pack_um': "001-pack", 'sales_um': "001-box", 'pack_equi': 1,'pack_um': 12 }
# 12 pack/box
```

For weighted products (e.g., raw meat sold by kg), an entirely different rule set applies — including a special case for whole animal products sold by each (EA).

**Tier C — LLM-Assisted: POS Register Name Generation**

This is the one field in the Sales view that requires LLM reasoning. POS register names must be compressed versions of the full product name, fitting within strict character limits (20 characters for Thai, 20 for English) while preserving the most important identifying information.

This can't be done deterministically because the compression decisions are contextual — which words to abbreviate, which to drop, which must be preserved depends on the specific product and what distinguishes it from similar products.

The approach uses a YAML-configured abbreviation dictionary and compression priority rules, which are loaded and passed to the LLM as structured context:

```yaml
# abbv.yaml
pos_name_limit:
  char_limit_th: 20
  char_limit_en: 20

abbv_en:
  Chicken: "Chkn"
  Breast: "Brst"
  Grilled: "Grl"
  Frozen: "Frz"

abbv_th:
  กรัม: "ก."
  กิโลกรัม: "กก."
  แช่แข็ง: "Frz"

compress_priority:
  always_keep: ["core_protein", "differentiation"]
  keep_if_space: ["cooking_method", "grade"]
  drop_first: ["weight", "filler_words"]
  
```

```python
Input:
  material_desc_eng: "Grilled Chicken Breast Teriyaki Flavor 200g"
  material_desc_local: "อกไก่ย่างรสเทอริยากิ 200 กรัม"
  brand: "GoldenFresh
```

Then prompt is made for the LLM to receives the full product description, approved abbreviation dictionaries, and compression priority rules — then generates a compressed POS name that fits the character limit while following the defined priorities:

```python
def build_pos_name_prompt(basic_data):

    config =  get_reference()['pos_name_config']
    rules = config.get('pos_name_limit')
    abbrev_en = config.get('abbv_en', {})
    abbrev_th = config.get('abbv_th', {})
    priority = config.get('compress_priority', {})

    char_limit_en = rules.get('char_limit_en', 24)
    char_limit_th = rules.get('char_limit_th', 20)

    desc_en = basic_data.get('material_desc_eng', '')
    desc_th = basic_data.get('material_desc_local', '')
    brand = basic_data.get('brand', '')

    prompt = """prompt engineering with {variables} goes here"""
    return prompt
```

```python
Output:
  pos_name_en: "Grl Chkn Brst Teri"    (within 20 chars)
  pos_name_th: "อกไก่ย.เทอริยากิ"       (within 20 chars)
```

**Why LLM is necessary here:** The abbreviation dictionary and priority rules provide constraints, but the actual compression decision — which specific words to abbreviate, which to drop entirely, and how to ensure the result still makes sense as a product identifier — requires contextual judgment that rule-based logic can't replicate across the full variety of product descriptions.

---

### Human Review Gate 2

Each department's user reviews their pre-filled view before it interfaces to their ERP. **Approve → data interfaces to downstream system.**

---

### ERP Interface

| View | Target System |
| --- | --- |
| Production | Manufacturing ERPs |
| Sales | Sales/POS Systems |
| SCM | Supply/Demand Planning & Forecasting |

> ERP interface is outside POC scope. The POC validates that AI can generate accurate, reviewable departmental views. Actual integration would use existing middleware (e.g., Kafka).
> 

---

## Known Limitations

### Data Constraints

- **Synthetic reference data:** All reference data (product master records, classification hierarchies, plant codes) is reconstructed from domain experience, not extracted from production systems. AI accuracy — particularly for attribute matching and similarity scoring — would improve significantly with access to real historical product databases. Results should be interpreted as feasibility indicators, not production-accuracy benchmarks.
- **Limited sample variety:** The POC is validated against a limited set of product types and business units. Edge cases that would surface with broader product coverage (e.g., unusual packing formats, rare plant designations, multi-language specifications) have not been exhaustively tested.

### Model Constraints

- **Local LLM capability:** This POC uses small open-source models (Llama 3.1 8B, Qwen2-VL 8B) running locally via Ollama. These are sufficient for structured parsing and classification tasks in a POC context, but production deployment may benefit from larger models — either commercial APIs for superior reasoning accuracy, or an organization's own locally hosted enterprise-grade models. The architecture is model-agnostic: swapping the underlying LLM requires changing only the model name or API endpoint, not redesigning the pipeline.
- **Thai language capability:** 8B parameter models have limited capability for complex Thai-language specifications. Larger models or Thai-specialized models would improve extraction and parsing accuracy, particularly for abbreviations, regional dialect variations, and mixed Thai-English text.

### Scope Constraints

- **POC, not production:** Components are validated individually with sample data. Full end-to-end integration testing, error recovery, authentication, and rate limiting are not implemented.
- **Human review interfaces not built:** The two human review gates are part of the governance design but are not implemented as UI in this POC. The POC validates that AI can generate reviewable output — the review interface itself is a systems implementation concern.
- **ERP interface out of scope:** The POC stops at generating departmental views. Actual integration to downstream ERPs via middleware (e.g., Kafka) is outside the project boundary.

### What Would Change in Production

| Area | POC State | Production Consideration |
| --- | --- | --- |
| Reference data | Synthetic, from domain experience | Real historical product database (20,000+ products) |
| LLM models | Local 8B models (Ollama) | Larger local models, commercial APIs, or organization's own AI infrastructure |
| Thai language | Basic capability | Thai-specialized or larger multilingual models |
| Pipeline | Individual component validation | End-to-end orchestration with error handling and retry logic |
| Human review | Conceptual (output is reviewable) | Built into MDM system UI with approval workflows |
| ERP integration | Out of scope | Middleware-based distribution (Kafka or equivalent) |
| Scale | Single-product processing | Batch processing with throughput optimization |
