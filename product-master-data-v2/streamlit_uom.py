import streamlit as st
import yaml
import sys
import os
import io
from datetime import datetime
import pandas as pd


# Session state initialization (Global Variables)
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None

if 'derived_data' not in st.session_state:
    st.session_state.derived_data = None

if 'packing_detail' not in st.session_state:
    st.session_state.packing_detail = None

if 'mdm_review_status' not in st.session_state:
    st.session_state.mdm_review_status = None

if 'metadata' not in st.session_state:
    st.session_state.metadata = None

if 'field_confidences' not in st.session_state:
    st.session_state.field_confidences = None

                
# Global Variables for Views
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = None

if 'production_data' not in st.session_state:
    st.session_state.production_data = None

# Find src folder
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.utility.data_persistence import DataPersistenceManager
from src.langgraph.uom_graph.uom_workflow_mdm import build_mdm_workflow
from src.langgraph.uom_graph.uom_workflow_production import build_production_workflow
from src.vlm_extractor.vlm_src.doc_extract import extract_document, load_templates

@st.cache_resource
def load_uom_config():
    """Load UOM topic config"""
    with open("config/topics/uom/topic_def.yaml", 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@st.cache_resource
def load_production_config():
    """Load Production view config"""
    with open("config/topics/uom/departmental_view/production/view_def.yaml", 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
    
@st.cache_resource
def load_doc_config():
    """Load VLM doc type config"""
    with open("vlm_docs_template/doc_config.yaml", 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

@st.cache_resource
def load_mdm_workflow():
    """Load MDM extraction workflow"""
    return build_mdm_workflow()

@st.cache_resource
def load_production_workflow():
    """Load Production transformation workflow"""
    return build_production_workflow()

# Page config
st.set_page_config(
    page_title="UOM → Production Pipeline",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("UOM Extraction + Department View Generation")
st.markdown("Extract packaging hierarchy and transform to departmental views")


# TABS
tab1, tab2, tab3, tab4, tab5 = st.tabs(["UOM Extraction (MDM)", "Production View", "Sales View", "Summary", "UOM Rag Sample pool"])

# =================================================
# TAB 1: UOM EXTRACTION (MDM)
# =================================================

with tab1:
    st.header("UOM Extraction - MDM Canonical Data")
    st.markdown("You can either choose an example from dropdown or upload test form")

    # Input Section
    examples = {
        "": "",
        "English - Simple": "2 kgs/bag x 10 bags/carton",
        "English - Decimal": "1.5 kg/bag x 12 bags/case",
        "Thai - Simple": "3 กก./ถุง 8 ถุง/ลัง",
        "Custom": "",
        "Scanned": ""
    }
    
    text, upload = st.columns([3,3], border=True)

    with text:
        selected_example = st.selectbox("Option 1: Choose an example:", list(examples.keys()))
        doc_config = load_doc_config()
        doc_type = doc_config['template']

    with upload:
        col1, col2 = st.columns([3,3])

        with col1:
            uploaded_file = st.file_uploader("Option 2: Choose a file")

        with col2:
            selected_doctype = st.selectbox("Choose VLM Scanning Config", list(doc_type.keys()))

        if uploaded_file and selected_doctype:
            # VLM Extract button
            col1, col2, col3 = st.columns([2, 1, 2])

            with col2:
                scan_button = st.button("Start VLM", use_container_width=True)

                if scan_button:
                    if selected_doctype == 'doc_type5':
                        vlm_result = extract_document(uploaded_file,doc_type,selected_doctype)
                        st.spinner("VLM Scanning In Progress")
                        st.toast('VLM Extraction Successful', icon='🔔')
                        selected_example = "Scanned"
                        st.session_state.vlm_value = vlm_result['packing_detail']

    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.header("Parsing text will be displayed below")
            
    if selected_example == "Custom":
        packing_detail = st.text_input(
            "Enter your packing detail:", 
            placeholder="e.g., BAG 20KG X 10 = CS 200KG"
        )

    elif selected_example == "Scanned":
        packing_detail = st.text_input(
            "Packing detail:",
            value=st.session_state.vlm_value
        )

    else:
        packing_detail = st.text_input(
            "Packing detail:",
            value=examples[selected_example]
        )
    
    # Extract button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        extract_button = st.button("Extract UOM", type="primary", use_container_width=True)
    
    # Extraction logic
    if extract_button:
        if not packing_detail.strip():
            st.error("Enter packing detail text first")
        else:
            st.success("Starting extraction...")
            
            col_terminal, col_results = st.columns([1, 1])
            
            with col_terminal:
                st.subheader("Live Terminal")
                terminal_display = st.empty()
            
            with col_results:
                st.subheader("Results")
                results_display = st.empty()
            
            output_buffer = io.StringIO()
            
            class StreamlitLogger:
                def write(self, text):
                    output_buffer.write(text)
                    terminal_display.text_area(
                        label="Terminal Output",
                        value=output_buffer.getvalue(),
                        height=600,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                def flush(self): pass
                def isatty(self): return False
                def fileno(self): return -1
            
            old_stdout = sys.stdout
            sys.stdout = StreamlitLogger()
            
            try:
                topic_config = load_uom_config()
                workflow = load_mdm_workflow()

                # ========================= Create State for Langgraph
                initial_state = {
                    'topic_config': topic_config,
                    'source_data': {'packing_detail': packing_detail},
                    'extracted_data': {},
                    'derived_data': {},
                    'production_view_data': {},
                    'sales_view_data': {},
                    'metadata': {}
                }
                

                # ========================= Getting Global Variable from Langgraph State
                final_state = workflow.invoke(initial_state)
                st.session_state.extracted_data = final_state['extracted_data']
                st.session_state.packing_detail = packing_detail
                st.session_state.metadata = final_state['metadata']
                st.session_state.field_confidences = final_state['field_confidences']
                
                
                with results_display.container():
                    results_table = []
                    for field, value in st.session_state.extracted_data.items():
                        confidence = st.session_state.field_confidences.get(field, None)
                        results_table.append({
                            'Field': field,
                            'Value': str(value) if value is not None else 'null',
                            'Confidence': confidence
                        })
                    st.dataframe(results_table, hide_index=True, use_container_width=True, height="content")
            
            finally:
                sys.stdout = old_stdout
            
            st.success("Extraction complete!")
    
    # Review & Edit Section
    if st.session_state.extracted_data is not None:
        st.divider()
        st.subheader("Review & Edit MDM Data")
        
        feedback_col1, feedback_col2 = st.columns([1, 3])
        
        with feedback_col1:
            st.markdown("**Review Results:**")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Correct", use_container_width=True, key="mdm_correct"):
                    st.session_state.mdm_review_status = "correct"
            with col_b:
                if st.button("Wrong", use_container_width=True, key="mdm_wrong"):
                    st.session_state.mdm_review_status = "wrong"
        
        with feedback_col2:
            if st.session_state.mdm_review_status == "wrong":
                st.info("Edit the incorrect fields below")
                
                edit_table = []
                for field, value in st.session_state.extracted_data.items():
                    edit_table.append({
                        'field': field,
                        'original': str(value) if value is not None else 'null',
                        'corrected': str(value) if value is not None else 'null'
                    })
                
                edited_df = st.data_editor(
                    edit_table,
                    use_container_width=True,
                    num_rows="fixed",
                    disabled=["field", "original"],
                    column_config={
                        "field": st.column_config.TextColumn("Field Name", disabled=True),
                        "original": st.column_config.TextColumn("AI Extraction", disabled=True),
                        "corrected": st.column_config.TextColumn("Edit Here")
                    },
                    hide_index=True
                )
                
                if st.button("Save Corrections", type="primary"):
                    # Apply corrections
                    corrected_data = {}
                    for row in edited_df:
                        field = row['field']
                        new_value = row['corrected']
                        original_value = st.session_state.extracted_data.get(field)
                        
                        if new_value == '' or new_value == 'null':
                            corrected_data[field] = None

                        elif isinstance(original_value, (int, float)):
                            try:
                                corrected_data[field] = float(new_value) if '.' in str(new_value) else int(float(new_value))
                            except:
                                corrected_data[field] = new_value

                        elif isinstance(original_value, bool):
                            if isinstance(new_value, str):
                                corrected_data[field] = str(new_value).upper() in ['TRUE', '1', 'YES']
                            else:
                                corrected_data[field] = bool(new_value)

                        else:
                            corrected_data[field] = (new_value)

                    if st.session_state.metadata:
                        metadata = st.session_state.metadata
                        metadata['human_review'] = {
                            'review_status': 'approved',
                            'review_by': 'user',
                            'review_at': datetime.now().isoformat(),
                            'correction': False
                    }

                    # Update session state with corrected data
                    st.session_state.extracted_data = corrected_data


                    topic_config = load_uom_config()
                    
                    #Save to RAG Sample
                    rag_action = DataPersistenceManager.save_to_rag_examples(topic_config=topic_config,
                                                                             input_source=st.session_state.packing_detail,
                                                                             extracted_data=corrected_data)

                    #Save to MDM Records
                    json_action = DataPersistenceManager.save_to_mdm(topic_name=topic_config['topic']['id'],
                                                                     input_source=st.session_state.packing_detail,
                                                                     extracted_data=corrected_data,
                                                                     correction_made=True,
                                                                     mdm_file = "mdm_records.json",
                                                                     metadata=st.session_state.metadata)

                    st.success("✅ Corrections saved! Now go to Production View tab.")


            elif st.session_state.mdm_review_status == "correct":

                if st.session_state.metadata:
                    metadata = st.session_state.metadata
                    metadata['human_review'] = {
                        'review_status': 'approved',
                        'review_by': 'user',
                        'review_at': datetime.now().isoformat(),
                        'correction': False
                    }
                
                topic_config = load_uom_config()
                
                rag_action = DataPersistenceManager.save_to_rag_examples(topic_config=topic_config,
                                                                         input_source=st.session_state.packing_detail,
                                                                         extracted_data=st.session_state.extracted_data)
                
                json_action = DataPersistenceManager.save_to_mdm(topic_name=topic_config['topic']['id'],
                                                                 input_source=st.session_state.packing_detail,
                                                                 extracted_data=st.session_state.extracted_data,
                                                                 correction_made=True,
                                                                 mdm_file = "mdm_records.json",
                                                                 metadata=st.session_state.metadata)
                
                st.success("✅ MDM data approved! Go to Production View tab to continue.")

        with st.expander("View Metadata Data", expanded=False):
            st.json(st.session_state.metadata)

        with st.expander("View Field Confidence Score", expanded=False):
            st.json(st.session_state.field_confidences)

# =================================================
# TAB 2: PRODUCTION VIEW
# =================================================

with tab2:
    st.header("Production View Transformation")
    
    if st.session_state.extracted_data is None:
        st.warning("Please complete UOM Extraction in Tab 1 first!")
    else:
        st.markdown("**MDM Data Ready for Transformation:**")
        mdm_summary = st.session_state.extracted_data.copy()

        with st.expander("View MDM Data", expanded=False):
            st.json(mdm_summary)

        """st.dataframe(
            [{'Field': k, 'Value': str(v)} for k, v in mdm_summary.items()],
            hide_index=True,
            height=600
        )"""
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            transform_button = st.button("🔄 Generate Production View", type="primary", use_container_width=True)
        
        if transform_button:
            st.success("🔄 Transforming to Production View...")
            
            col_terminal, col_results = st.columns([1, 1])
            
            with col_terminal:
                st.subheader("🖥️ Live Terminal")
                terminal_display = st.empty()
            
            with col_results:
                st.subheader("📊 Production View Results")
                results_display = st.empty()
            
            output_buffer = io.StringIO()
            
            class StreamlitLogger:
                def write(self, text):
                    output_buffer.write(text)
                    terminal_display.text_area(
                        label="Terminal Output",
                        value=output_buffer.getvalue(),
                        height=400,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                def flush(self): pass
                def isatty(self): return False
                def fileno(self): return -1
            
            old_stdout = sys.stdout
            sys.stdout = StreamlitLogger()
            
            try:
                workflow = load_production_workflow()
                
                # Use CURRENT extracted_data (which might be edited!)
                state = {
                    'topic_config': load_uom_config(),
                    'source_data': {'packing_detail': st.session_state.packing_detail},
                    'extracted_data': st.session_state.extracted_data,  # ← Uses edited data!
                    'derived_data': {},
                    'production_view_data': {},
                    'sales_view_data': {}
                }
                
                final_state = workflow.invoke(state)
                st.session_state.production_data = final_state['production_view_data']
                
                with results_display.container():
                    if 'data' in st.session_state.production_data:
                        results_table = []
                        for field, value in st.session_state.production_data['data'].items():
                            results_table.append({
                                'Field': field,
                                'Value': str(value)
                            })
                        st.dataframe(results_table, hide_index=True, use_container_width=True)
                        
                        st.markdown("**Metadata:**")
                        st.json(st.session_state.production_data['production_view_metadata'])
            
            finally:
                sys.stdout = old_stdout
            
            st.success("✅ Production View generated!")
        
        # Show production data if it exists
        if st.session_state.production_data:
            st.divider()
            st.subheader("Review Production View")
            st.dataframe(st.session_state.production_data['data'])
            
        if st.button("Approve Production View"):
            st.success("Production View approved!")

            if st.session_state.production_data:
                metadata = st.session_state.production_data['production_view_metadata']
                metadata['human_review'] = {
                            'review_status': 'approved',
                            'review_by': 'user',
                            'review_at': datetime.now().isoformat(),
                    }


# =================================================
# TAB 3: SALES VIEW
# =================================================

with tab3:
    st.header("Sales View Transformation")
    
    if st.session_state.production_data is None:
        st.warning("Please complete Production View in Tab 2 first!")
    else:
        st.markdown("**Production Data Ready for Sales Transformation:**")
        
        # Show what Production data we have
        with st.expander("View Production Data", expanded=False):
            st.json(st.session_state.production_data)
        
        # Also show key MDM fields that Sales might use
        with st.expander("View MDM Data (also available)", expanded=False):
            st.json(st.session_state.extracted_data)
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            transform_button = st.button("Generate Sales View", type="primary", use_container_width=True, key="sales_transform")
        
        if transform_button:
            st.success("Transforming to Sales View...")
            
            col_terminal, col_results = st.columns([1, 1])
            
            with col_terminal:
                st.subheader("Live Terminal")
                terminal_display = st.empty()
            
            with col_results:
                st.subheader("Sales View Results")
                results_display = st.empty()
            
            output_buffer = io.StringIO()
            
            class StreamlitLogger:
                def write(self, text):
                    output_buffer.write(text)
                    terminal_display.text_area(
                        label="Terminal Output",
                        value=output_buffer.getvalue(),
                        height=400,
                        disabled=True,
                        label_visibility="collapsed"
                    )
                def flush(self): pass
                def isatty(self): return False
                def fileno(self): return -1
            
            old_stdout = sys.stdout
            sys.stdout = StreamlitLogger()
            
            try:
                from src.langgraph.uom_graph.uom_workflow_sales import build_sales_workflow
                
                workflow = build_sales_workflow()
                
                # Sales needs BOTH MDM and Production data!
                state = {
                    'topic_config': load_uom_config(),
                    'source_data': {'packing_detail': st.session_state.packing_detail},
                    'extracted_data': st.session_state.extracted_data,  # MDM data
                    'derived_data': {},
                    'production_view_data': st.session_state.production_data,  # Production data
                    'sales_view_data': {}
                }
                
                final_state = workflow.invoke(state)
                st.session_state.sales_data = final_state['sales_view_data']

                with results_display.container():
                    if 'data' in st.session_state.sales_data:
                        results_table = []
                        for field, value in st.session_state.sales_data['data'].items():
                            results_table.append({
                                'Field': field,
                                'Value': str(value)
                            })
                        st.dataframe(results_table, hide_index=True, use_container_width=True)
                        
                        st.markdown("**Metadata:**")
                        st.json(st.session_state.sales_data['sales_view_metadata'])
            
            finally:
                sys.stdout = old_stdout
            
            st.success("Sales View generated!")
        
        # Show sales data if it exists
        if 'sales_data' in st.session_state and st.session_state.sales_data:
            st.divider()
            st.subheader("Review Sales View")
            st.dataframe(st.session_state.sales_data['data'])
            
            if st.button("Approve Sales View", key="approve_sales"):

                st.success("Sales View approved!")

                if st.session_state.production_data:
                    metadata = st.session_state.sales_data['sales_view_metadata']
                    metadata['human_review'] = {
                                'review_status': 'approved',
                                'review_by': 'user',
                                'review_at': datetime.now().isoformat(),
                        }


# =================================================
# TAB 4: SUMMARIZATION
# =================================================

with tab4:
    st.header("Summary")

    #Data View
    col1, col2, col3 = st.columns([3,3,3])

    with col1: 
        st.subheader("MDM Canonical Data")

        if st.session_state.extracted_data is None:
            st.warning("No data to display")
        else:
            with st.expander("Canonical Data", expanded=True ):
                st.json(st.session_state.extracted_data)
            
    with col2: 
        st.subheader("Production Data")

        if st.session_state.production_data is None:
            st.warning("No data to display")
        else:
            with st.expander("Production Data", expanded=True):
                st.json(st.session_state.production_data['data'])
            
    with col3: 
        st.subheader("Sales Data")

        if st.session_state.sales_data is None:
            st.warning("No data to display")
        else:
            with st.expander("Sales Data", expanded=True ):
                st.json(st.session_state.sales_data['data'])


    #Metadata Section
    col1, col2, col3 = st.columns([3,3,3])

    with col1: 
        st.subheader("MDM Canonical Metadata")

        if st.session_state.extracted_data is None:
            st.warning("No data to display")
        else:
            with st.expander("Metadata", expanded=True):
                st.json(st.session_state.metadata)
            
    with col2: 
        st.subheader("Production Metadata")

        if st.session_state.production_data is None:
            st.warning("No data to display")
        else:
            with st.expander("Production Metadata", expanded=True):
                st.json(st.session_state.production_data['production_view_metadata'])
            
    with col3: 
        st.subheader("Sales Metadata")

        if st.session_state.sales_data is None:
            st.warning("No data to display")
        else:
            with st.expander("Sales Metadata", expanded=True):
                st.json(st.session_state.sales_data['sales_view_metadata'])



with tab5:

    topic_config = load_uom_config()

    ref = topic_config['topic']['reference_data']

    if "rag_examples" in ref.keys():
        path = topic_config['topic']['reference_data']['rag_examples']['path']
    else:
        st.markdown("No Data") 
    
    df = pd.read_csv(path, encoding='utf-8')
    display_data = st.dataframe(df, hide_index=True, use_container_width=True, height="content")

    

   
    
