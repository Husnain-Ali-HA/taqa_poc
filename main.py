import streamlit as st
import requests

# Logic App URLs
excel_agent_url = "https://prod-32.eastus2.logic.azure.com:443/workflows/14f2817faaaf4c87955d8a9a105e1f7c/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=SoPqh6rpX3tGJ1Mgsj9IVl--KwbKHbujAA_Wbu13zU8"
pptx_agent_url = "https://prod-08.eastus2.logic.azure.com:443/workflows/372ad925d5d140a9a6bb319c4c10159a/triggers/When_a_HTTP_request_is_received/paths/invoke?api-version=2016-10-01&sp=%2Ftriggers%2FWhen_a_HTTP_request_is_received%2Frun&sv=1.0&sig=zBN5wU_2kWGrzUxsMhSyj_8h_S-10HQZT3gCzw9A5Lg"

# Common payload
payload = {
    "HTTP_URI": "https://example.com/api/data",
    "HTTP_request_content": "Sample content sent from Streamlit app."
}
headers = {
    "Content-Type": "application/json"
}

st.title("Run Azure Logic Apps")

if st.button("Submit"):
    st.info("Triggering Logic Apps...")

    # Call Excel Agent
    try:
        response_excel = requests.post(excel_agent_url, json=payload, headers=headers)
        if response_excel.ok:
            result_excel = response_excel.json()
            excel_link = result_excel.get("link", "No link returned from Excel Agent.")
            st.markdown(f"📄 [Excel Agent Output]({excel_link})", unsafe_allow_html=True)
        else:
            st.error(f"Excel Agent failed: {response_excel.text}")
    except Exception as e:
        st.error(f"Excel Agent error: {e}")

    # Call PPTX Agent
    try:
        response_pptx = requests.post(pptx_agent_url, json=payload, headers=headers)
        if response_pptx.ok:
            result_pptx = response_pptx.json()
            pptx_link = result_pptx.get("link", "No link returned from PPTX Agent.")
            st.markdown(f"📊 [PPTX Agent Output]({pptx_link})", unsafe_allow_html=True)
        else:
            st.error(f"PPTX Agent failed: {response_pptx.text}")
    except Exception as e:
        st.error(f"PPTX Agent error: {e}")
