import streamlit as st
import storage
import migration
import time
import json
import requests
from streamlit_lottie import st_lottie
import hashlib

# Page Configuration
st.set_page_config(
    page_title="PG Shift", 
    page_icon="⚡", 
    layout="centered"
)

# --- Authentication Configuration ---
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()  # Default: admin123

def check_password(username, password):
    """Verify username and password"""
    if username == ADMIN_USERNAME:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == ADMIN_PASSWORD_HASH
    return False

def show_login_page():
    """Display login page"""
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style='text-align: center;'>
                <h1 style='font-size: 3rem; font-weight: 900; color: #1e3a8a; margin-bottom: 10px;'>
                    🔐 PG Shift
                </h1>
                <p style='color: #64748b; margin-bottom: 2rem;'>Admin Access Required</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submit = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit:
                if check_password(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        st.markdown("""
            <div style='text-align: center; margin-top: 3rem; color: #a0aec0; font-size: 0.85rem;'>
                <p>Default credentials: admin / admin123</p>
            </div>
        """, unsafe_allow_html=True)

# Initialize authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Show login page if not authenticated
if not st.session_state.authenticated:
    show_login_page()
    st.stop()


# --- Animations ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200: return None
        return r.json()
    except: return None

# Assets
LOTTIE_ROBOT = "https://lottie.host/embed/98648b26-5b2d-4696-8888-25102573516f/9iY5M8sJ2N.json" # Placeholder URL, using valid direct JSON usually better. 
# Using a reliable public URL for a "database" or "robot" animation
LOTTIE_DB = "https://assets5.lottiefiles.com/private_files/lf30_1003_01.json" # Generic DB
LOTTIE_ROCKET = "https://assets9.lottiefiles.com/packages/lf20_uzv8jgjg.json" # Rocket

lottie_db_anim = load_lottieurl("https://assets2.lottiefiles.com/packages/lf20_w51pcehl.json") # Server/Database
lottie_success = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_lk80fpsm.json") # Success Check

# Custom CSS & Animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background-color: #ffffff;
    }

    /* Card Styling */
    .step-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.08);
        border: 1px solid rgba(191, 219, 254, 0.5); /* Subtle blue border */
        margin-bottom: 2rem;
    }
    
    /* Button Base - Blue Gradient Touch */
    .stButton>button { 
        width: 100%; 
        border-radius: 10px; 
        border: none !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white !important;
        transition: all 0.3s ease;
        font-weight: 700;
        height: 3.2rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.1);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        transform: translateY(-1px);
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.25);
        color: white !important;
    }
    
    /* Primary Action Override (Deep Blue) */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%) !important;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.3) !important;
    }
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1e3a8a 0%, #172554 100%) !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8fbff;
        border-right: 1px solid #e1eefc;
    }

    .sidebar-logo {
        padding: 1.5rem;
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border-radius: 16px;
        text-align: center;
        margin: 1rem 1rem 2rem 1rem;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.2);
    }
    .sidebar-logo h2 {
        color: white !important;
        font-weight: 800 !important;
        letter-spacing: -1px !important;
        margin-bottom: 0 !important;
        font-size: 1.6rem !important;
    }
    .sidebar-logo p {
        color: rgba(255,255,255,0.8) !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        margin-top: 4px !important;
    }

    .connection-card {
        padding: 12px 15px;
        background: white;
        border: 1px solid #e1e7f0;
        border-radius: 12px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .connection-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 8px rgba(30, 58, 138, 0.08);
        transform: translateX(4px);
    }
    .env-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 20px;
        font-size: 0.65rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    
    /* Sidebar Buttons - Blue Gradient */
    .stSidebar [data-testid="stButton"] button {
        border-radius: 10px !important;
        border: none !important;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        font-size: 0.85rem !important;
        height: 2.8rem !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
    }
    .stSidebar [data-testid="stButton"] button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 12px rgba(37, 99, 235, 0.2) !important;
    }
    
    /* Sidebar Primary (Green Gradient) */
    .stSidebar [data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2) !important;
    }
    .stSidebar [data-testid="stButton"] button[kind="primary"]:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        box-shadow: 0 6px 15px rgba(5, 150, 105, 0.3) !important;
    }

    .danger-box { 
        padding: 1.25rem; 
        background-color: #fef2f2; 
        border-left: 4px solid #ef4444; 
        color: #991b1b; 
        border-radius: 12px;
        font-size: 0.9rem;
        border: 1px solid #fee2e2;
        border-left-width: 4px;
    }
    .success-box { 
        padding: 1.25rem; 
        background-color: #f0fdf4; 
        border-left: 4px solid #22c55e; 
        color: #166534; 
        border-radius: 12px;
        font-size: 0.9rem;
        border: 1px solid #dcfce7;
        border-left-width: 4px;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
    }

    /* Checkbox Styling */
    div[data-testid="stCheckbox"] {
        background-color: #f0f7ff;
        padding: 0.8rem 1rem;
        border-radius: 12px;
        border: 1px solid #dbeafe;
        transition: all 0.3s ease;
        margin: 1rem 0;
    }
    div[data-testid="stCheckbox"]:hover {
        border-color: #3b82f6;
        background-color: #ffffff;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.05);
    }
    div[data-testid="stCheckbox"] p {
        color: #1e40af !important;
        font-weight: 600 !important;
    }
    </style>
    
    <script>
        // Auto-scroll to top helper
        var mainContent = window.parent.document.querySelector('section.main');
        if (mainContent) {
            mainContent.scrollTo(0, 0);
        }
    </script>
""", unsafe_allow_html=True)

# --- Sidebar Manager ---
@st.dialog("➕ Add New Connection")
def add_connection_dialog():
    st.write("Save a new connection profile for later use.")
    with st.form("manual_add_form", border=False):
        name = st.text_input("Profile Name", placeholder="e.g. Analytics DB")
        env = st.selectbox("Environment", ["Production", "Staging", "Development", "QA", "UAT"])
        
        c1, c2 = st.columns(2)
        host = c1.text_input("Host", placeholder="localhost")
        port = c2.text_input("Port", value="5432")
        
        dbname = st.text_input("Database Name")
        
        c3, c4 = st.columns(2)
        user = c3.text_input("Username", value="postgres")
        password = c4.text_input("Password", type="password")
        
        st.write("")
        if st.form_submit_button("💾 Save Connection", use_container_width=True):
            if name and host and dbname and user:
                success, msg = storage.save_connection(name, host, port, user, password, dbname, env)
                if success:
                    st.success(f"Connection '{name}' saved!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Please fill in all required fields (Name, Host, DB, User).")

@st.dialog("⚙️ Manage Connections")
def manage_connections_dialog():
    st.write("View and remove valid connection profiles.")
    conns = storage.get_connections()
    
    if not conns:
        st.info("No connections saved.")
        return

    for c in conns:
        c1, c2 = st.columns([3, 1])
        with c1:
            env_label = c.get('environment', 'Production')
            st.markdown(f"**{c['name']}** 🏷️ _{env_label}_")
            st.caption(f"{c['user']}@{c['host']}:{c['port']}/{c['dbname']}")
        with c2:
            if st.button("🗑️", key=f"del_{c['id']}", help="Delete this connection"):
                storage.delete_connection(c['id'])
                st.rerun()
        st.divider()

with st.sidebar:
    st.markdown("""
        <div class='sidebar-logo'>
            <h2 style='color: #1e40af; font-weight: 800; margin-bottom: 0;'>PG SHIFT</h2>
            <p style='color: #64748b; font-size: 0.8rem; font-weight: 600;'>POSTGRESQL MIGRATION ENGINE</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    
    if st.button("🏠 Return to Home", use_container_width=True):
        st.session_state.step = 1
        st.session_state.logs = []
        st.session_state.current_phase = "IDLE"
        st.rerun()

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    st.header("📂 Saved Connections")
    
    # Get connections grouped by environment
    grouped_connections = storage.get_connections_by_environment()
    total_count = sum(len(conns) for conns in grouped_connections.values())
    st.caption(f"Found {total_count} profiles across {len(grouped_connections)} environments")
    
    if st.button("➕ Add New Connection", use_container_width=True, type="primary"):
        add_connection_dialog()
    
    if st.button("⚙️ Manage Saved Connections", use_container_width=True):
        manage_connections_dialog()
    
    st.write("")
    
    display_connections = storage.get_connections_by_environment()
    
    if display_connections:
        # Define environment colors
        env_colors = {
            "Production": ("#fee2e2", "#991b1b"), # Red
            "Staging": ("#ffedd5", "#9a3412"),   # Orange
            "Development": ("#dcfce7", "#166534"), # Green
            "QA": ("#e0e7ff", "#3730a3"),        # Indigo
            "UAT": ("#f3e8ff", "#6b21a8")        # Purple
        }

        for env, connections in sorted(display_connections.items()):
            bg, text_c = env_colors.get(env, ("#f1f5f9", "#475569"))
            with st.expander(f"🏷️ {env} ({len(connections)})", expanded=False):
                for conn in connections:
                    st.markdown(f"""
                        <div class='connection-card'>
                            <div class='env-tag' style='background: {bg}; color: {text_c};'>{env}</div>
                            <div style='font-weight: 700; color: #1e293b; font-size: 0.95rem; line-height: 1.2;'>{conn['name']}</div>
                            <div style='color: #64748b; font-size: 0.7rem; font-family: monospace; margin-top: 6px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;'>
                                {conn['user']}@{conn['host']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)



# --- UI Components ---


def render_stepper(current_step):
    steps = ["Start", "Source", "Target", "Execute"]
    
    # CSS for Stepper
    st.markdown("""
    <style>
    /* Keyframes for animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .hero-title {
        animation: fadeIn 1s ease-out;
    }
    .hero-subtitle {
        animation: fadeIn 1.5s ease-out;
    }
    .hero-anim-box {
        animation: float 6s ease-in-out infinite;
    }
    
    .stepper-wrapper {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
    }
    /* ... existing stepper styles ... */
    .stepper-item {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
    }
    .stepper-item::before {
        position: absolute;
        content: "";
        border-bottom: 2px solid #e0e0e0;
        width: 100%;
        top: 15px;
        left: -50%;
        z-index: 0;
    }
    .stepper-item::after {
        position: absolute;
        content: "";
        border-bottom: 2px solid #e0e0e0;
        width: 100%;
        top: 15px;
        left: 50%;
        z-index: 0;
    }
    .stepper-item:first-child::before { content: none; }
    .stepper-item:last-child::after { content: none; }
    
    .step-counter {
        position: relative;
        z-index: 1;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #fff;
        border: 2px solid #e0e0e0;
        margin-bottom: 6px;
        font-weight: bold;
        color: #aaa;
    }
    .step-name {
        color: #aaa;
        font-size: 12px;
        font-weight: 500;
    }
    
    /* Active State */
    .stepper-item.active .step-counter {
        border-color: #667eea;
        background: #667eea;
        color: #fff;
    }
    .stepper-item.active .step-name {
        color: #667eea;
        font-weight: 700;
    }
    /* Completed State */
    .stepper-item.completed .step-counter {
        border-color: #667eea;
        background: #667eea;
        color: #fff;
    }
    .stepper-item.completed::before, .stepper-item.completed::after {
        border-color: #667eea;
    }
    </style>
    """, unsafe_allow_html=True)
    
    html = '<div class="stepper-wrapper">'
    for i, step_label in enumerate(steps):
        idx = i + 1
        class_str = "stepper-item"
        if current_step == idx:
            class_str += " active"
        elif current_step > idx:
            class_str += " completed"
            
        html += f"""<div class="{class_str}">
<div class="step-counter">{idx if current_step <= idx else '✔'}</div>
<div class="step-name">{step_label}</div>
</div>"""
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# --- Session State Management ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'source_conf' not in st.session_state:
    st.session_state.source_conf = {}
if 'target_conf' not in st.session_state:
    st.session_state.target_conf = {}
if 'source_stats' not in st.session_state:
    st.session_state.source_stats = None
# Intent is always full now
st.session_state.intent = "full"

# Navigation Helpers
def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# Render scaffold
if st.session_state.step > 1: # Only show stepper after home
     render_stepper(st.session_state.step)

# --- step 1: Welcome ---
def step_1_welcome():
    # Vertical Centered Layout (Ultra Compact - Single Page)
    st.write("")
    
    # 1. Typography (Title & Tagline) - Ultra Compact
    st.markdown("""
        <div style='text-align: center; margin-top: -5px;'>
            <h1 class='hero-title' style='font-size: 2.8rem; font-weight: 900; letter-spacing: -2px; margin-bottom: 3px; color: #1e3a8a;'>
                PG Shift
            </h1>
            <p class='hero-subtitle' style='font-size: 1rem; color: #64748b; font-weight: 500; margin-top: 3px; margin-bottom: 1.2rem; font-family: sans-serif;'>
                Drop. Dump. Restore. <span style='color: #2563eb; font-weight: 800;'>Done.</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

    # 2. CTA Button (Centered)
    c_cta_1, c_cta_2, c_cta_3 = st.columns([1, 1, 1])
    with c_cta_2:
        if st.button("🚀 IGNITE MIGRATION", type="primary", use_container_width=True):
            next_step()
            st.rerun()

    st.write("")

    # 3. Features Grid (Ultra Compact)
    f1, f2, f3 = st.columns(3)
    
    css_card = "text-align: center; padding: 12px; background: #fff; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);"
    
    with f1:
        st.markdown(f"""
        <div style='{css_card}'>
            <div style='font-size: 1.6rem; margin-bottom: 6px;'>🛡️</div>
            <div style='font-weight: 700; color: #2d3748; font-size: 0.9rem;'>Safe Mode</div>
            <div style='font-size: 0.7rem; color: #a0aec0; margin-top: 3px;'>Preflight Checks</div>
        </div>
        """, unsafe_allow_html=True)
        
    with f2:
        st.markdown(f"""
        <div style='{css_card}'>
            <div style='font-size: 1.6rem; margin-bottom: 6px;'>⚡</div>
            <div style='font-weight: 700; color: #2d3748; font-size: 0.9rem;'>Live Stats</div>
            <div style='font-size: 0.7rem; color: #a0aec0; margin-top: 3px;'>Real-time Analysis</div>
        </div>
        """, unsafe_allow_html=True)
        
    with f3:
        st.markdown(f"""
        <div style='{css_card}'>
            <div style='font-size: 1.6rem; margin-bottom: 6px;'>🤖</div>
            <div style='font-weight: 700; color: #2d3748; font-size: 0.9rem;'>Agent Ready</div>
            <div style='font-size: 0.7rem; color: #a0aec0; margin-top: 3px;'>Structured Logs</div>
        </div>
        """, unsafe_allow_html=True)

# --- Step 2: Source ---
def step_2_source():
    st.markdown("### 🔒 Source Database")
    st.caption("Read-only connection. We will analyze this source first.")
    
    # Two-step selection: Environment -> Database
    st.markdown("#### 📂 Load Saved Connection")
    col_env, col_db = st.columns(2)
    
    saved_data = {}
    grouped_connections = storage.get_connections_by_environment()
    
    with col_env:
        if grouped_connections:
            env_options = ["-- Select Environment --"] + sorted(list(grouped_connections.keys()))
            selected_env = st.selectbox("1️⃣ Environment", env_options, key="src_env_select")
        else:
            st.info("No saved connections")
            selected_env = None
    
    with col_db:
        if selected_env and selected_env != "-- Select Environment --":
            conns_in_env = grouped_connections.get(selected_env, [])
            conn_options = ["-- Select Database --"] + [c['name'] for c in conns_in_env]
            selected_conn_name = st.selectbox("2️⃣ Database", conn_options, key="src_db_select")
            
            if selected_conn_name and selected_conn_name != "-- Select Database --":
                saved_data = next((c for c in conns_in_env if c['name'] == selected_conn_name), {})
                if saved_data:
                    st.success(f"✅ Loaded: {selected_conn_name} ({selected_env})")
        else:
            st.selectbox("2️⃣ Database", ["-- Select Environment First --"], disabled=True, key="src_db_select_placeholder")
    
    st.write("")
    
    # Pre-fill from session or saved
    defaults = st.session_state.source_conf if st.session_state.source_conf else saved_data
    
    # Connection Form
    st.markdown("#### 🔐 Connection Details")
    with st.container():
        c1, c2 = st.columns(2)
        host = c1.text_input("Host", value=defaults.get('host', 'localhost'), key="src_host")
        port = c2.text_input("Port", value=defaults.get('port', '5432'), key="src_port")
        dbname = st.text_input("Database", value=defaults.get('dbname', ''), key="src_db")
        c3, c4 = st.columns(2)
        user = c3.text_input("Username", value=defaults.get('user', 'postgres'), key="src_user")
        password = c4.text_input("Password", value=defaults.get('password', ''), type="password", key="src_pass")

    # Action Buttons
    col_test, col_save = st.columns([1, 1])
    
    # Test & Analyze
    if col_test.button("Test & Analyze 🔎", type="primary"):
        st.session_state.source_conf = {'host': host, 'port': port, 'dbname': dbname, 'user': user, 'password': password}
        with st.spinner("Connecting & Analyzing..."):
            ok, res = migration.test_connection(st.session_state.source_conf)
            if ok:
                st.success(f"Connected: {res.split(' ')[0]}...")
                try:
                    stats = migration.get_db_stats(st.session_state.source_conf)
                    st.session_state.source_stats = stats
                except Exception as e:
                    st.error(f"Could not get stats: {e}")
            else:
                st.error(f"Connection Failed: {res}")
                st.session_state.source_stats = None

    # Save Connection Feature
    with col_save:
        with st.popover("💾 Save Connection"):
            save_name = st.text_input("Save as:", placeholder="e.g. Prod DB", key="src_save_name")
            save_env = st.selectbox("Environment", ["Production", "Staging", "Development", "QA", "UAT"], key="src_save_env")
            if st.button("Save", key="src_save_btn"):
                if save_name:
                    success, msg = storage.save_connection(save_name, host, port, user, password, dbname, save_env)
                    if success:
                        st.toast(f"Saved '{save_name}' ({save_env}) successfully!", icon="✅")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Enter a name.")

    if st.session_state.source_stats:
        st.write("---")
        st.markdown("#### 📊 Source Analysis")
        c1, c2, c3 = st.columns(3)
        c1.metric("Schemas", st.session_state.source_stats['schemas'])
        c2.metric("Tables", st.session_state.source_stats['tables'])
        c3.metric("Est. Rows", f"{st.session_state.source_stats['rows']:,}")
        
        col_back, col_next = st.columns([1, 1])
        if col_back.button("⬅ Back"):
            prev_step()
            st.rerun()
        if col_next.button("Next: Configure Target ➡", type="primary"):
            next_step()
            st.rerun()

# --- Step 3: Target ---
def step_3_target():
    st.markdown("### ⚠️ Target Database")
    st.markdown("""
        <div class="danger-box">
            <b>WARNING: Destructive Operations</b><br>
            All public tables in the target database will be DROPPED before restore.
        </div>
    """, unsafe_allow_html=True)
    
    # Two-step selection: Environment -> Database
    st.markdown("#### 📂 Load Saved Connection")
    col_env, col_db = st.columns(2)
    
    saved_data = {}
    grouped_connections = storage.get_connections_by_environment()
    
    with col_env:
        if grouped_connections:
            env_options = ["-- Select Environment --"] + sorted(list(grouped_connections.keys()))
            selected_env = st.selectbox("1️⃣ Environment", env_options, key="tgt_env_select")
        else:
            st.info("No saved connections")
            selected_env = None
    
    with col_db:
        if selected_env and selected_env != "-- Select Environment --":
            conns_in_env = grouped_connections.get(selected_env, [])
            conn_options = ["-- Select Database --"] + [c['name'] for c in conns_in_env]
            selected_conn_name = st.selectbox("2️⃣ Database", conn_options, key="tgt_db_select")
            
            if selected_conn_name and selected_conn_name != "-- Select Database --":
                saved_data = next((c for c in conns_in_env if c['name'] == selected_conn_name), {})
                if saved_data:
                    st.success(f"✅ Loaded: {selected_conn_name} ({selected_env})")
        else:
            st.selectbox("2️⃣ Database", ["-- Select Environment First --"], disabled=True, key="tgt_db_select_placeholder")
    
    st.write("")
                
    defaults = st.session_state.target_conf if st.session_state.target_conf else saved_data

    st.markdown("#### 🔐 Connection Details")
    with st.container():
        c1, c2 = st.columns(2)
        host = c1.text_input("Host", value=defaults.get('host', 'localhost'), key="tgt_host")
        port = c2.text_input("Port", value=defaults.get('port', '5432'), key="tgt_port")
        dbname = st.text_input("Database", value=defaults.get('dbname', ''), key="tgt_db")
        c3, c4 = st.columns(2)
        user = c3.text_input("Username", value=defaults.get('user', 'postgres'), key="tgt_user")
        password = c4.text_input("Password", value=defaults.get('password', ''), type="password", key="tgt_pass")
        
    # Save Connection Feature
    with st.expander("💾 Save this connection details"):
        c_save_1, c_save_2 = st.columns([3, 1])
        save_name = c_save_1.text_input("Save as:", placeholder="e.g. Staging DB", key="tgt_save_name")
        save_env = c_save_1.selectbox("Environment", ["Production", "Staging", "Development", "QA", "UAT"], key="tgt_save_env")
        if c_save_2.button("Save", key="tgt_save_btn"):
             if save_name:
                success, msg = storage.save_connection(save_name, host, port, user, password, dbname, save_env)
                if success:
                    st.toast(f"Saved '{save_name}' ({save_env}) successfully!", icon="✅")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(msg)
    
    st.write("---")
    st.warning(f"Type the database name to confirm destructive action:")
    confirmation = st.text_input("Confirm Database Name", placeholder="e.g. staging_db")
    
    col_back, col_next = st.columns([1, 1])
    if col_back.button("⬅ Back", key="tgt_back"):
        prev_step()
        st.rerun()
        
    if col_next.button("Confirm & Proceed", type="primary", key="tgt_next"):
        st.session_state.target_conf = {'host': host, 'port': port, 'dbname': dbname, 'user': user, 'password': password}
        if confirmation == dbname and dbname != "":
            next_step()
            st.rerun()
        else:
            st.error("Confirmation failed. Database name mismatch.")


# --- Step 4: Execution ---
def step_4_execute():
    st.markdown("### 🚀 Preflight & Execute")
    
    # Preflight
    st.markdown("#### 🔍 Preflight Checks")
    with st.spinner("Running system checks..."):
        checks = migration.preflight_check(st.session_state.source_conf, st.session_state.target_conf)
    
    all_passed = True
    for check in checks:
        icon = "✅" if check['status'] == 'pass' else "❌"
        st.write(f"{icon} {check['msg']}")
        if check['status'] == 'fail':
            all_passed = False
            
    
    if all_passed:
        can_proceed = True
    else:
        st.error("Preflight checks failed.")
        can_proceed = st.checkbox("⚠️ Force / Proceed Anyway (Risky)", help="Bypass safety checks. Required if you know what you are doing (e.g. pg_dump version mismatch is acceptable).")
        
    # --- Step 4: Execution Confirmation ---
    st.markdown("#### 📋 Migration Summary")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
                <div style='padding: 15px; background: #eff6ff; border-radius: 12px; border-left: 4px solid #2563eb;'>
                    <small style='text-transform: uppercase; color: #1e40af; font-weight: 800; font-size: 0.7rem; letter-spacing: 0.5px;'>SOURCE</small><br>
                    <div style='color: #1e293b; font-weight: 700; margin-top: 4px;'>{st.session_state.source_conf.get('host')}</div>
                    <div style='color: #64748b; font-size: 0.8rem;'>Database: <b>{st.session_state.source_conf.get('dbname')}</b></div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div style='padding: 15px; background: #fff7ed; border-radius: 12px; border-left: 4px solid #f97316;'>
                    <small style='text-transform: uppercase; color: #9a3412; font-weight: 800; font-size: 0.7rem; letter-spacing: 0.5px;'>TARGET</small><br>
                    <div style='color: #1e293b; font-weight: 700; margin-top: 4px;'>{st.session_state.target_conf.get('host')}</div>
                    <div style='color: #9a3412; font-size: 0.8rem;'>Database: <b>{st.session_state.target_conf.get('dbname')}</b></div>
                </div>
            """, unsafe_allow_html=True)

    st.write("")
    
    # Final Destruction Confirmation
    st.markdown("#### 🚨 Safety Authorization")
    st.markdown("""
        <div class="danger-box">
            <b>CRITICAL WARNING:</b> All existing data in the public schema of the <u>target</u> database will be <b>destroyed</b>.
        </div>
    """, unsafe_allow_html=True)
    
    confirm_destruction = st.checkbox(
        f"I confirm that I want to drop all tables in '{st.session_state.target_conf.get('dbname')}' and restore the source data.",
        key="final_confirm_check"
    )

    if can_proceed:
        st.write("")
        if st.button("🚀 Start Migration Now", type="primary", disabled=not confirm_destruction):
            st.session_state.logs = []
            
            # Create a placeholder for live logs
            log_display = st.empty()
            
            def log_callback(msg):
                # Handle phase updates
                if msg.startswith("PHASE:"):
                    phase_info = msg.split("|")
                    phase_name = phase_info[0].replace("PHASE:", "").title()
                    phase_detail = phase_info[1] if len(phase_info) > 1 else ""
                    st.session_state.current_phase = phase_name
                    st.session_state.logs.append(f"--- {phase_name}: {phase_detail} ---")
                else:
                    st.session_state.logs.append(msg)
                
                # Update live log view
                with log_display:
                    # Show last 15 lines of logs for brevity during execution
                    visible_logs = st.session_state.logs[-15:]
                    st.code("\n".join(visible_logs))
                    
                # Structured log for Agents
                try:
                    structured = json.dumps({"timestamp": time.time(), "message": msg})
                    print(structured) 
                except: pass
                
            st.session_state.current_phase = "Initializing"
            
            with st.status("Executing Migration...", expanded=True) as status:
                # Update status label dynamically
                status.update(label=f"Migration: {st.session_state.get('current_phase', 'Starting')}...")
                
                success, msg = migration.run_migration(
                    st.session_state.source_conf, 
                    st.session_state.target_conf, 
                    log_callback,
                    schema_only=False
                )
                
                if success:
                    status.update(label="Migration Complete!", state="complete", expanded=False)
                    if lottie_success:
                        st_lottie(lottie_success, height=150, key="success_anim")
                    else:
                        st.balloons()
                        
                    st.markdown("""
                        <div class="success-box">
                            <b>Migration Successful!</b><br>
                            The source database has been successfully migrated to the target.
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Back to Home button
                    st.write("")
                    if st.button("🏠 Back to Home", type="primary", use_container_width=True):
                        st.session_state.step = 1
                        st.session_state.logs = []
                        st.rerun()
                else:
                    status.update(label="Migration Failed", state="error", expanded=True)
                    st.error(f"❌ {msg}")
                    
                    # Back to Home button for failed migrations too
                    st.write("")
                    if st.button("🏠 Back to Home", type="secondary", use_container_width=True):
                        st.session_state.step = 1
                        st.session_state.logs = []
                        st.rerun()
            
            with st.expander("View Full Migration Logs", expanded=False):
                st.code("\n".join(st.session_state.logs))
    
    if st.button("⬅ Back"):
        prev_step()
        st.rerun()

# --- Main Routing ---
if st.session_state.step == 1:
    step_1_welcome()
elif st.session_state.step == 2:
    step_2_source()
elif st.session_state.step == 3:
    step_3_target()
elif st.session_state.step == 4:
    step_4_execute()

# Footer
st.markdown("<br><br><div style='text-align: center; color: #ccc; font-size: 0.8rem;'>Made with ❤️ by <b>Lifetrenz DevOps Team</b></div>", unsafe_allow_html=True)
