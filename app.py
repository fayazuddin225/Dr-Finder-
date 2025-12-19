import streamlit as st
import sqlite3
import pandas as pd
import google.generativeai as genai
import json

# Set page configuration
st.set_page_config(
    page_title="Ent",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern premium look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Force background on the entire app container */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #020617 0%, #0f172a 100%) !important;
        color: #f8fafc !important;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0) !important;
    }

    /* Glassmorphism Card */
    .doctor-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 28px;
        margin-bottom: 24px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    .doctor-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 1px solid rgba(56, 189, 248, 0.4);
        background: rgba(30, 41, 59, 0.9);
    }

    .doc-name {
        color: #38bdf8;
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 4px;
        letter-spacing: -0.025em;
    }

    .doc-spec {
        color: #94a3b8;
        font-size: 0.95rem;
        font-weight: 500;
        margin-bottom: 16px;
        line-height: 1.4;
    }

    .doc-info {
        display: flex;
        justify-content: space-between;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }

    .info-item {
        display: flex;
        flex-direction: column;
    }

    .info-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .info-value {
        font-size: 1.15rem;
        color: #ffffff;
        font-weight: 800;
    }

    .rating-badge {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    .availability-badge {
        background: rgba(244, 63, 94, 0.15);
        color: #fb7185;
        padding: 6px 14px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        border: 1px solid rgba(244, 63, 94, 0.2);
    }

    .availability-online {
        background: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.2);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #020617 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Global text color force */
    .stMarkdown p, .stMarkdown span, .stMarkdown label, h1, h2, h3 {
        color: #f8fafc !important;
    }

    /* Target Sidebar Labels explicitly */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        margin-bottom: 5px !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
    }

    /* Sidebar Logo containment */
    .sidebar-logo-container {
        display: flex;
        justify-content: center;
        padding: 20px 0;
        margin-bottom: 20px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.1) 0%, rgba(0,0,0,0) 70%);
    }

    /* Header */
    .header-container {
        text-align: center;
        padding: 60px 0 40px 0;
    }

    .header-title {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(to right, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 16px;
        letter-spacing: -0.05em;
    }

    .header-subtitle {
        color: #94a3b8 !important;
        font-size: 1.25rem;
    }
    
    /* Search Button */
    .stButton>button {
        background: linear-gradient(90deg, #38bdf8, #818cf8) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 700 !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_doctors_data():
    try:
        conn = sqlite3.connect("doctors.db")
        query = "SELECT * FROM doctors WHERE is_active = 1"
        df = pd.read_sql_query(query, conn)
        conn.close()
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

def ask_gemini(api_key, user_query, df):
    if not api_key:
        return "Please provide a Gemini API Key in the sidebar to use the AI Assistant."
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prepare data for grounding
    # We'll send the top 15 doctors as context to keep prompt size reasonable
    doctors_context = df[['name', 'specialization', 'experience', 'rating', 'fee']].head(20).to_dict('records')
    
    prompt = f"""
    You are an expert Medical Consultant Assistant for 'ENT Doctor Finder Lahore'.
    The user is looking for a doctor. Use the following list of ENT specialists in Lahore to answer their query.
    
    Doctors Data:
    {json.dumps(doctors_context)}
    
    User Query: "{user_query}"
    
    Instructions:
    1. Recommend the 2-3 best doctors from the data provided based on the query.
    2. Mention their Name, Specialization, Rating, and Fee.
    3. Keep the tone professional, caring, and helpful.
    4. If you don't find a perfect match, suggest the most relevant ones.
    5. Format the output beautifully with markdown (bolding, lists).
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error connecting to Gemini: {str(e)}"

def main():
    st.markdown("""
        <div class="header-container">
            <h1 class="header-title">ENT Doctor Finder in lahore</h1>
            <p class="header-subtitle">Find and book the best healthcare specialists instantly</p>
        </div>
    """, unsafe_allow_html=True)

    df = get_doctors_data()

    if df.empty:
        st.warning("No data found in the database. Please run the scraper first.")
        return

    # Sidebar filters with premium logo
    st.sidebar.markdown('<div class="sidebar-logo-container">', unsafe_allow_html=True)
    st.sidebar.image("logo.png", width=180)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown("<h2 style='text-align: center; color: #38bdf8; margin-top: -20px;'>Advanced Filters</h2>", unsafe_allow_html=True)
    
    search_query = st.sidebar.text_input("🔍 Search By Name", placeholder="Enter doctor name...")
    
    specializations = ["All"] + sorted(df['specialization'].unique().tolist())
    spec_filter = st.sidebar.selectbox("🎯 Specialization", specializations)
    
    # Process budget - extracting numeric value from 'fee' column
    def extract_fee(fee_str):
        try:
            # Remove Rs, whitespace, and commas
            clean_fee = str(fee_str).replace('Rs.', '').replace(',', '').strip()
            return int(clean_fee)
        except:
            return 0

    df['fee_numeric'] = df['fee'].apply(extract_fee)
    
    min_fee = int(df['fee_numeric'].min())
    max_fee = int(df['fee_numeric'].max())
    
    if max_fee > 0:
        budget = st.sidebar.slider("💰 Max Fee (Budget)", min_fee, max_fee, max_fee)
    else:
        budget = 5000

    # Filtering logic
    filtered_df = df.copy()
    
    if search_query:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search_query, case=False)]
    
    if spec_filter != "All":
        filtered_df = filtered_df[filtered_df['specialization'] == spec_filter]
    
    if max_fee > 0:
        filtered_df = filtered_df[filtered_df['fee_numeric'] <= budget]

    st.sidebar.markdown("---")
    st.sidebar.header("🤖 AI Assistant")
    gemini_key = st.sidebar.text_input("Enter Gemini API Key", type="password", help="Get your key at https://aistudio.google.com/app/apikey")
    
    # Display results
    st.subheader(f"Showing {len(filtered_df)} Specialists")

    # AI Recommendation Section
    if gemini_key:
        with st.expander("✨ Ask AI for Recommendation", expanded=True):
            user_question = st.text_input("Describe your symptoms or what you're looking for:", placeholder="e.g. I have a sore throat and need an experienced doctor within 2500 Rs.")
            if user_question:
                with st.spinner("AI is analyzing doctors..."):
                    ai_response = ask_gemini(gemini_key, user_question, filtered_df)
                    st.markdown(f"""
                        <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 15px; padding: 20px; color: white;">
                            {ai_response}
                        </div>
                    """, unsafe_allow_html=True)
    else:
        st.sidebar.info("💡 Enter your API Key to unlock AI recommendations!")

    if filtered_df.empty:
        st.info("No doctors found matching your criteria. Try relaxing the filters.")
        
        if budget < max_fee:
            st.write("Best matches above your budget:")
            alternative_df = df[df['specialization'] == spec_filter].sort_values('fee_numeric').head(3)
            if not alternative_df.empty:
                filtered_df = alternative_df

    # Grid layout for cards
    cols = st.columns(3)
    for i, row in filtered_df.iterrows():
        with cols[i % 3]:
            # Determine availability badge class
            avail_class = "availability-badge"
            if "Available" in row['availability'] and "Not" not in row['availability']:
                avail_class += " availability-online"

            st.markdown(f"""
                <div class="doctor-card">
                    <div class="doc-name">{row['name']}</div>
                    <div class="doc-spec">{row['specialization']}</div>
                    <div style="margin-bottom: 12px;">
                        <span class="rating-badge">⭐ {row['rating']}</span>
                        <span class="{avail_class}">🕒 {row['availability']}</span>
                    </div>
                    <div class="doc-info">
                        <div class="info-item">
                            <span class="info-label">Fee</span>
                            <span class="info-value">{row['fee']}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Experience</span>
                            <span class="info-value">{row['experience']}</span>
                        </div>
                    </div>
                    <br>
                    <a href="{row['profile_url']}" target="_blank" style="text-decoration:none;">
                        <button style="width:100%; padding:14px; border-radius:12px; background: linear-gradient(90deg, #38bdf8, #818cf8); color:white; border:none; cursor:pointer; font-weight:700; font-size: 0.95rem; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(56, 189, 248, 0.3);">
                            View Professional Profile
                        </button>
                    </a>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
