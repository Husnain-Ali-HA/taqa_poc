import streamlit as st
import requests

# Logic App URLs
excel_agent_url = "https://prod-32.eastus2.logic.azure.com:443/workflows/14f2817faaaf4c87955d8a9a105e1f7c/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=SoPqh6rpX3tGJ1Mgsj9IVl--KwbKHbujAA_Wbu13zU8"
pptx_agent_url = "https://prod-08.eastus2.logic.azure.com:443/workflows/372ad925d5d140a9a6bb319c4c10159a/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=zBN5wU_2kWGrzUxsMhSyj_8h_S-10HQZT3gCzw9A5Lg"

# Payload
payload = {
    "HTTP_URI": "https://example.com/api/data",
    "HTTP_request_content": "Sample content sent from Streamlit app.",
}
headers = {"Content-Type": "application/json"}

# UI

# st.set_page_config(
#     page_title="Taqa Electric Grid Reports",
#     page_icon="📄",
#     layout="centered",
#     initial_sidebar_state="auto",
#     menu_items={"Get Help": None, "Report a Bug": None, "About": None},
# )
st.set_page_config(page_title="Taqa Electric Grid Reports",page_icon="📄", menu_items={'Get Help': None, 'About': None})
st.markdown(
    """
    <style>
        /* Hide the Streamlit menu */
        #MainMenu {visibility: hidden; display: none;} 
        
        /* Hide the footer */
        footer {visibility: hidden; display: none;} 
        
        /* Hide the header (contains the GitHub icon in some cases) */
        header {visibility: hidden; display: none;}

        .css-1kyxreq {visibility: hidden; display: none;} /* Manage App icon */
    </style>
    """,
    unsafe_allow_html=True
)


st.markdown("# 🔌 Taqa Electric Grid")
st.markdown("### ⚙️ Automated Report Generation via Agentic Workflow")
st.markdown(
    """
    This interface allows triggering two Azure Logic Apps to generate Excel and PowerPoint reports automatically.  
    Once completed successfully, a download link to the generated report will be provided below.
    """
)

# if st.button("🚀 If  Previously Generate Report Check This Link"):
#     pptx_link = "https://digifloat.sharepoint.com/:f:/s/Taqa-electric-grid/EqoRV3ozKIxMnrvWPSzORVUB54SEOuAvZKnaGb-WKr395g?e=TOTvJ9"
#     st.markdown("---")
#     st.markdown(
#     f'<a href="{pptx_link}" target="_blank">📥 <strong>Click here to view the generated report</strong></a>',
#     unsafe_allow_html=True,
#     )
    


if st.button("🚀 Generate Report"):
    st.info("Triggering Logic Apps...")

    # Run Excel Agent
    response_excel = requests.post(excel_agent_url, json=payload, headers=headers)
    if response_excel.status_code == 200:
        st.success("✅ Excel Agent ran successfully.")
    else:
        st.error("❌ Excel Agent failed.")

    # Run PPTX Agent
    response_pptx = requests.post(pptx_agent_url, json=payload, headers=headers)
    if response_pptx.status_code == 200:
        st.success("✅ PPTX Agent ran successfully.")
    else:
        st.error("❌ PPTX Agent failed.")

    # Show report link if both succeed
    if response_excel.status_code == 200 and response_pptx.status_code == 200:
        pptx_link = "https://digifloat.sharepoint.com/:f:/s/Taqa-electric-grid/EqoRV3ozKIxMnrvWPSzORVUB54SEOuAvZKnaGb-WKr395g?e=TOTvJ9"
        st.markdown("---")
        st.markdown(
            f'<a href="{pptx_link}" target="_blank">📥 <strong>Click here to view the generated report</strong></a>',
            unsafe_allow_html=True,
        )
