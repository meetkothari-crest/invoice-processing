# import json
# import streamlit as st
# import os
# from streamlit_pdf_reader import pdf_reader
# import yaml
# from typing import List, Dict

# def load_config():
#     """
#     Load and return the configuration from the 'config.yaml' file.
#     """
#     with open('config.yaml', 'r') as file:
#         return yaml.safe_load(file)

# CONFIG = load_config()

# def load_invoice_data(file_path: str) -> Dict[str, Dict[str, str]]:
#     """
#     Load processed invoice data from a JSON file.
    
#     Args:
#         file_path (str): Path to the JSON file containing processed invoice data.
    
#     Returns:
#         dict: Processed invoice data
#     """
#     with open(file_path, 'r') as file:
#         return json.load(file)

# def get_invoice_files(folder: str) -> List[str]:
#     """
#     Get a sorted list of PDF invoice files in the specified folder.
    
#     Args:
#         folder (str): Path to the folder containing invoice PDFs.
    
#     Returns:
#         list: Sorted list of PDF filenames
#     """
#     return sorted([f for f in os.listdir(folder) if f.endswith('.pdf')])

# def display_invoice_data(invoice_data_catalog: Dict[str, Dict[str, str]], invoice_filename: str) -> None:
#     """
#     Display the processed data for a specific invoice in the Streamlit app.
    
#     Args:
#         invoice_data_catalog (dict): Catalog of all processed invoice data
#         invoice_filename (str): Filename of the current invoice
#     """
#     try:
#         invoice_data = invoice_data_catalog[invoice_filename]
        
#         st.subheader("Summary")
#         st.write(invoice_data["summary"].replace("$", "\\$"))

#         st.subheader("Structured Data")
#         st.json(json.loads(invoice_data["structured"]))
        
#         st.subheader("Detailed Text")
#         st.text(invoice_data["full"])
#     except KeyError:
#         st.error(f"Data for {invoice_filename} not found.")
#     except Exception as e:
#         st.error(f"Error displaying data: {str(e)}")

# def main() -> None:
#     """
#     Main function to run the Streamlit app for reviewing processed invoice data.
#     """
#     st.set_page_config(layout="wide")
    
#     # Load processed invoice data and get list of invoice files
#     invoice_data = load_invoice_data(CONFIG['processing']['output_file'])
#     invoice_files = [key for key in invoice_data.keys()]
#     # checking that for each invoice with data in the output file, it has the actual invoice stored in the local download folder
#     assert all([os.path.exists(os.path.join(os.getcwd(), CONFIG['processing']['local_download_folder'], file)) for file in invoice_files])
    
#     # Initialize or use existing counter for navigation
#     if 'counter' not in st.session_state:
#         st.session_state.counter = 0
    
#     st.header("Review Invoice and Extracted Data")
    
#     # Navigation buttons
#     col1, col2 = st.columns(2)
#     with col1:
#         st.button("⬅️ Previous", 
#               disabled=st.session_state.counter == 0,  # Disable when at the first invoice
#               on_click=lambda: st.session_state.update(counter=st.session_state.counter - 1))
#     with col2:
#         st.button("Next ➡️", 
#               disabled=st.session_state.counter == len(invoice_files) - 1,  # Disable when at the last invoice
#               on_click=lambda: st.session_state.update(counter=st.session_state.counter + 1))
    
#     # Get current invoice filename and path
#     invoice_filename = invoice_files[st.session_state.counter]
#     invoice_file_path = os.path.join(CONFIG['processing']['local_download_folder'], invoice_filename)
    
#     # Display invoice PDF and extracted data side by side
#     invoice, data = st.columns([3, 2])
    
#     with invoice:
#         st.header(f"Invoice: {invoice_filename}")
#         pdf_reader(invoice_file_path, key=f"pdf_reader_{invoice_filename}")
    
#     with data:
#         st.header("Generated Data")
#         display_invoice_data(invoice_data, invoice_filename)

# if __name__ == "__main__":
#     main()



import json
import streamlit as st
import os
from streamlit_pdf_reader import pdf_reader
import yaml
from typing import List, Dict
import plotly.express as px
import pandas as pd

def load_config():
    """
    Load and return the configuration from the 'config.yaml' file.
    """
    with open('config.yaml', 'r') as file:
        return yaml.safe_load(file)

CONFIG = load_config()

def load_invoice_data(file_path: str) -> Dict[str, Dict[str, str]]:
    """
    Load processed invoice data from a JSON file.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def display_invoice_data(invoice_data_catalog: Dict[str, Dict[str, str]], invoice_filename: str) -> None:
    """
    Display the processed data for a specific invoice in the Streamlit app.
    """
    try:
        invoice_data = invoice_data_catalog[invoice_filename]
        st.subheader("📜 Summary")
        st.markdown(f"**{invoice_data['summary'].replace('$', '\\$')}**")
        
        st.subheader("📊 Structured Data")
        st.json(json.loads(invoice_data["structured"]))
        
        if "line_items" in json.loads(invoice_data["structured"]):
            df = pd.DataFrame(json.loads(invoice_data["structured"])["line_items"])
            if not df.empty:
                fig = px.bar(df, x="item", y="price", title="Invoice Breakdown")
                st.plotly_chart(fig)
        
        with st.expander("📄 Detailed Text"):
            st.text(invoice_data["full"])
    except KeyError:
        st.error(f"Data for {invoice_filename} not found.")
    except Exception as e:
        st.error(f"Error displaying data: {str(e)}")

def main() -> None:
    """
    Main function to run the Streamlit app for reviewing processed invoice data.
    """
    st.set_page_config(page_title="Invoice Review", layout="wide")
    st.title("📑 Invoice Review Dashboard")
    
    # Load processed invoice data and get list of invoice files
    invoice_data = load_invoice_data(CONFIG['processing']['output_file'])
    invoice_files = list(invoice_data.keys())
    
    # Initialize navigation counter
    if 'counter' not in st.session_state:
        st.session_state.counter = 0
    
    # Sidebar Navigation
    with st.sidebar:
        st.header("Navigation")
        if st.button("⬅️ Previous", disabled=st.session_state.counter == 0):
            st.session_state.counter -= 1
        if st.button("Next ➡️", disabled=st.session_state.counter == len(invoice_files) - 1):
            st.session_state.counter += 1
        
        st.markdown("---")
        st.write("Select an invoice to view:")
        selected_index = st.selectbox("Invoice Files", range(len(invoice_files)), format_func=lambda x: invoice_files[x])
        st.session_state.counter = selected_index
    
    # Get current invoice filename and path
    invoice_filename = invoice_files[st.session_state.counter]
    invoice_file_path = os.path.join(CONFIG['processing']['local_download_folder'], invoice_filename)
    
    # Tabs for viewing Invoice and Extracted Data
    tab1, tab2 = st.tabs(["📄 Invoice", "📊 Extracted Data"])
    
    with tab1:
        st.header(f"Invoice: {invoice_filename}")
        pdf_reader(invoice_file_path, key=f"pdf_reader_{invoice_filename}")
    
    with tab2:
        display_invoice_data(invoice_data, invoice_filename)

if __name__ == "__main__":
    main()