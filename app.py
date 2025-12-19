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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Button Gradients */
    .stButton>button { 
        width: 100%; 
        border-radius: 8px; 
        border: none;
        transition: transform 0.2s, box-shadow 0.2s;
        font-weight: 600;
        height: 3rem;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Primary Action */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    /* Secondary Action */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="secondary"] {
        background: white;
        border: 1px solid #e2e8f0;
        color: #2d3748;
    }

    /* Cards */
    .step-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
        border: 1px solid #edf2f7;
    }
    
    .danger-box { padding: 15px; background-color: #fff5f5; border-left: 5px solid #e53e3e; color: #c53030; border-radius: 4px; }
    .success-box { padding: 15px; background-color: #f0fff4; border-left: 5px solid #38a169; color: #2f855a; border-radius: 4px; }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Manager ---
@st.dialog("Manage Connections")
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
    if lottie_db_anim:
        st_lottie(lottie_db_anim, height=150, key="sidebar_anim")
    st.header("📂 Saved Connections")
    
    # Get connections grouped by environment
    grouped_connections = storage.get_connections_by_environment()
    total_count = sum(len(conns) for conns in grouped_connections.values())
    st.caption(f"Found {total_count} profiles across {len(grouped_connections)} environments")
    
    if st.button("Manage / Delete Connections", use_container_width=True):
        manage_connections_dialog()
    
    st.write("")
    
    # Display connections grouped by environment
    if grouped_connections:
        for env, connections in sorted(grouped_connections.items()):
            with st.expander(f"🏷️ {env} ({len(connections)})", expanded=True):
                for conn in connections:
                    st.markdown(f"""
                        <div style='padding: 8px; background: #f8f9fa; border-radius: 6px; margin-bottom: 8px;'>
                            <b>{conn['name']}</b><br>
                            <small style='color: #6c757d;'>{conn['user']}@{conn['host']}:{conn['port']}/{conn['dbname']}</small>
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
        
    if can_proceed:
        st.write("---")
        st.markdown("#### 🚦 Ready to Migrate")
        if st.button("Start Migration Now", type="primary"):
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
