import os
import datetime
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

st.title("About the Continuous Controls Monitoring Dashboard")

st.write(
    "This dashboard is designed to provide an executive overview of continuous controls monitoring "
    "across various business units, teams, and locations."
)
st.write(
    "It allows users to filter data by business unit, team, location, and framework, providing a "
    "comprehensive view of compliance and risk management."
)
st.write(
    "The dashboard is built using Streamlit and Plotly, leveraging a database query cache for efficient data retrieval."
)
st.write(
    "For more information on how to use this dashboard, please refer to the documentation or contact the support team."
)

st.subheader("Support Information")
st.markdown(
    "- View source code and documentation: [GitHub Repository](https://github.com/mantel-group/ccm-solution-accelerator/)\n"
    "- To report issues or request features: [Create a GitHub Issue](https://github.com/mantel-group/ccm-solution-accelerator/issues/new)"
)

st.subheader("Licence")
st.markdown(
    "This software has been provided by Mantel Group to your organisation under the following terms:\n\n"
    "- ✅ You are free to run this software in any way that suits your organisation's needs\n"
    "- ✅ You may modify and extend the software to meet your specific requirements\n"
    "- ✅ You may customise configurations, add new features, or integrate with your existing systems\n"
    "- ❌ You are not permitted to share this code outside of your organisation\n"
    "- ❌ Distribution, resale, or sharing with external parties is prohibited\n"
    "- 🤝 We encourage you to contribute back to the project by submitting "
    "[pull requests](https://github.com/mantel-group/ccm-solution-accelerator/pulls) "
    "for new features, collectors, or metrics that could benefit the broader community"
)

st.subheader("Contact Us")
st.markdown(
    "- Want to extend this accelerator to suit your environment? [Contact us](https://mantelgroup.com.au/contact)\n"
    "- Visit our website: [mantelgroup.com.au](https://mantelgroup.com.au)"
)

st.subheader("Debug Info")
db_engine = "Postgres" if os.getenv("POSTGRES_ENDPOINT") else "DuckDB"
st.write(f"Database engine: **{db_engine}**")
st.write(f"Start time: **{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")

try:
    with open("build-date.txt", "rt", encoding="utf-8") as f:
        st.write(f"Build date: **{f.read().strip()}**")
except FileNotFoundError:
    pass
