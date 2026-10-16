EATI ADMIN V3 NAVIGATION UPDATE

1. Copy app.py, home.py, admin_auth.py, admin_setup.sql, and v3/admin/* into EATI.
2. Keep your existing database.py, user_database.py, pages/1..4, and Streamlit secrets.
3. Run admin_setup.sql in Supabase SQL Editor.
4. python3 -m streamlit run app.py
5. Admin URL: http://localhost:8501/v3-admin
6. Vendor Job Form: click the button on the Admin Dashboard.

Streamlit st.navigation supports flat route paths. Exact /v3/admin requires an external router/proxy or a different framework. The Google login callback is configured separately in existing Streamlit secrets.
AI extraction and publishing are NOT implemented in this update.
