import os
import time
import docx
import pandas as pd
import google.genai as genai
from pypdf import PdfReader
import streamlit as str_launch

# =========================================================
# 1. CONFIGURATION & AI SETUP
# =========================================================

API_KEY = os.environ.get("GCP_API_KEY", "")
client = genai.Client(api_key=API_KEY)


def read_document_texts(file) -> str:
    """Read text automatically from TXT, MD, PDF or DOCX files."""
    try:
        if file.name.endswith(".pdf"):
            reader = PdfReader(file)
            texts = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    texts += extracted + "\n"
            return texts
        elif file.name.endswith(".docx"):
            doc = docx.Document(file)
            return "\n".join([p.text for p in doc.paragraphs if p.text])
        else:
            return file.read().decode("utf-8")
    except Exception as e:
        return f"error reading file: {str(e)}"


def analyze_grand_vision(
    model_type: str,
    utility_description: str,
    supply_description: str,
    treasury_description: str,
    extra_document_texts: str = "",
) -> str:
    context_and_instructions = (
        "You are an elite Venture Capital partner, enterprise software"
        " architect, and head economist.\nAnalyze the following project and"
        " generate a master breakdown completely in professional English.\n\nYou"
        " MUST structure your response with these exact sections:\n### 🏢 PHASE"
        " 1: Industry Classification & Market Sector\nIdentify the exact"
        " industry, target market sector, and overarching business category"
        " this project falls into.\n\n### 👑 PHASE 2: Economic Architecture &"
        " Tokenomics Stress-Test\nEvaluate sustainability, value capture"
        " mechanisms, and investor readiness.\n\n### 🛠️ PHASE 3: Technical"
        " Blueprint & Execution Roadmap\nOutline exactly what needs to be"
        " built, developed, or coded (e.g., smart contracts, frontend/backend"
        " architecture, data models, APIs) and the next concrete technical"
        " steps the founder must take."
    )

    full_prompt = (
        f"{context_and_instructions}\n\n--- FOUNDER'S PROJECT DATA ---\n• Chosen"
        f" Architecture: {model_type}\n• Utility & Incentives:"
        f" {utility_description if utility_description.strip() else 'Extract directly from document'}\n•"
        f" Supply & Allocation:"
        f" {supply_description if supply_description.strip() else 'Extract directly from document'}\n•"
        f" Treasury Flows:"
        f" {treasury_description if treasury_description.strip() else 'Extract directly from document'}\n"
    )
    if extra_document_texts:
        full_prompt += (
            "\n--- FULL ATTACHED DOCUMENT / WHITE-PAPER CONTENT"
            f" ---\n{extra_document_texts}\n"
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=full_prompt
    )
    return response.text


# 10 DIFFERENT MOCK ENTERPRISES
MOCK_FARMS_REGISTRY = [
    {
        "entity": "Green Valley Agri (Pty) Ltd",
        "farm": "Farm 402 - Klerksdorp District",
        "gps": 'S 26° 52\' 10", E 26° 40\' 03"',
    },
    {
        "entity": "Goudveld Grain Farming CC",
        "farm": "Farm 112 - Potchefstroom Sector",
        "gps": 'S 26° 42\' 15", E 27° 05\' 44"',
    },
    {
        "entity": "Highveld Citrus & Dairy Enterprise",
        "farm": "Farm 804 - Bethal District",
        "gps": 'S 26° 27\' 01", E 29° 27\' 50"',
    },
    {
        "entity": "Bramley Livestock & Crops (Pty) Ltd",
        "farm": "Farm 305 - Middelburg East",
        "gps": 'S 25° 46\' 19", E 29° 28\' 33"',
    },
    {
        "entity": "Karoo Eco-Agri Co-Op",
        "farm": "Farm 12 - Graaff-Reinet District",
        "gps": 'S 32° 15\' 08", E 24° 32\' 11"',
    },
    {
        "entity": "Overberg Wheat & Wool Holdings",
        "farm": "Farm 567 - Caledon Sector",
        "gps": 'S 34° 13\' 44", E 19° 25\' 22"',
    },
    {
        "entity": "Limpopo Subtropical Produce (Pty) Ltd",
        "farm": "Farm 921 - Tzaneen Valley",
        "gps": 'S 23° 49\' 55", E 30° 09\' 40"',
    },
    {
        "entity": "Free State Maize & Soy CC",
        "farm": "Farm 208 - Kroonstad Sector",
        "gps": 'S 27° 39\' 12", E 27° 14\' 02"',
    },
    {
        "entity": "Kalahari Beef Exporters",
        "farm": "Farm 44 - Vryburg West",
        "gps": 'S 26° 57\' 30", E 24° 43\' 50"',
    },
    {
        "entity": "Natal Midlands Organics Co.",
        "farm": "Farm 610 - Howick District",
        "gps": 'S 29° 28\' 04", E 30° 13\' 18"',
    },
]

# ==========================================
# 2. SESSION STATE (USER, WALLETS & TOKEN PRICE)
# ==========================================

if "is_registered" not in str_launch.session_state:
    str_launch.session_state["is_registered"] = False

if "user_profile" not in str_launch.session_state:
    str_launch.session_state["user_profile"] = {}

if "fetched_agri_data" not in str_launch.session_state:
    str_launch.session_state["fetched_agri_data"] = None

# WALLET BALANCES
if "wallets" not in str_launch.session_state:
    str_launch.session_state["wallets"] = {
        "Consumer": 1000.00,
        "Merchant": 5000.00,
        "Farmer": 2500.00,
        "Treasury_Inflows": 150.00,
        "Consumer_Rewards": 25.00,
    }

# XCHEF-E TRADING TOKEN PRICE (INITIAL VALUE $0.0100)
if "xchef_e_price" not in str_launch.session_state:
    str_launch.session_state["xchef_e_price"] = 0.0100

if "tx_history" not in str_launch.session_state:
    str_launch.session_state["tx_history"] = []

# ==========================================
# 3. PREMIUM FINTECH VISUAL STYLING (CSS)
# ==========================================

str_launch.set_page_config(
    page_title="XCHEF | Enterprise Platform", page_icon="👑", layout="wide"
)

str_launch.markdown(
    """
    <style>
    .stApp { background-color: #0d0e12; color: #e4e6eb; }
    h1 { color: #d4af37 !important; font-weight: 700 !important; letter-spacing: 1px; }
    h2, h3 { color: #f3cd5d !important; border-bottom: 1px solid #3a3b3c; padding-bottom: 8px; margin-top: 25px !important; }
    label { color: #d4af37 !important; font-weight: bold !important; }
    textarea, input { background-color: #16181d !important; color: #ffffff !important; border: 1px solid #2a2b32 !important; border-radius: 8px !important; }
    
    .metric-card { background-color: #16181d; padding: 15px; border-radius: 10px; border: 1px solid #d4af37; text-align: center; }
    .metric-card-token { background-color: #1a231a; padding: 15px; border-radius: 10px; border: 1px solid #28a745; text-align: center; }
    .metric-title { font-size: 0.85rem; color: #a0a0a0; }
    .metric-value { font-size: 1.35rem; font-weight: bold; color: #f3cd5d; }
    .token-value { font-size: 1.35rem; font-weight: bold; color: #28a745; }
    
    .agri-card { background-color: #1a1f26; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745; margin-top: 10px; }
    
    div.stButton > button, div.stDownloadButton > button {
        background-color: #d4af37 !important; color: #0d0e12 !important;
        font-weight: bold !important; border: 1px solid #d4af37 !important;
        border-radius: 6px !important; padding: 10px 18px !important; transition: all 0.3s ease; width: 100%;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover { background-color: #f3cd5d !important; transform: translateY(-2px); }
    .report-box { background-color: #16181d; padding: 25px; border-radius: 8px; border-left: 4px solid #d4af37; margin-top: 20px; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "chat_history" not in str_launch.session_state:
    str_launch.session_state["chat_history"] = []

# ==========================================
# 4. MAIN LOGIC: REGISTRATION vs DASHBOARD
# ==========================================

if not str_launch.session_state["is_registered"]:
    str_launch.title("👑 Welcome to XCHEF | Enterprise Onboarding")
    str_launch.write(
        "Complete your automated verification to gain access to the XCHEF"
        " Ecosystem."
    )
    str_launch.markdown("<br>", unsafe_allow_html=True)

    col_centered = str_launch.columns([1, 2, 1])[1]
    with col_centered:
        str_launch.subheader("🔒 Create & Verify Profile")
        role = str_launch.selectbox(
            "Select your Role on the Platform:",
            ["Farmer", "Consumer", "Business (Merchant)"],
        )

        name_input = str_launch.text_input(
            "Full Name & Surname:", value="Johannes van der Merwe"
        )
        email = str_launch.text_input("Email Address:")

        if role == "Farmer":
            str_launch.markdown("---")
            str_launch.markdown(
                "### 🚜 Automated National Agri-Registry Lookup"
            )

            agri_id = str_launch.text_input(
                "Enter Agricultural Registration / Tax ID:",
                value="AGRI-3857-ZA",
            )

            if str_launch.button("🔍 Fetch Agri Registry Data (API Sync)"):
                if not name_input.strip():
                    str_launch.error("Please enter your Full Name & Surname above first!")
                else:
                    with str_launch.spinner(
                        "Connecting to Central Agricultural Database..."
                    ):
                        time.sleep(1.2)
                        digits = "".join(filter(str.isdigit, agri_id))
                        index = (
                            int(digits) % len(MOCK_FARMS_REGISTRY)
                            if digits
                            else 0
                        )
                        selected_farm = MOCK_FARMS_REGISTRY[index]

                        str_launch.session_state["fetched_agri_data"] = {
                            "owner": name_input,
                            "farm_name": selected_farm["entity"],
                            "farm_id": selected_farm["farm"],
                            "gps_coords": selected_farm["gps"],
                            "status": "VERIFIED ACTIVE PRODUCER ✅",
                        }
                    str_launch.success(
                        f"✓ Database record found for {name_input}! Details"
                        " loaded."
                    )
                    str_launch.rerun()

            if str_launch.session_state["fetched_agri_data"]:
                data = str_launch.session_state["fetched_agri_data"]
                str_launch.markdown(
                    f"""
                <div class="agri-card">
                    <b>🏛️ Registered Entity:</b> {data['farm_name']}<br>
                    <b>👤 Registered Owner:</b> {data['owner']}<br>
                    <b>📍 Direct Land ID:</b> {data['farm_id']}<br>
                    <b>🛡️ Status:</b> <span style="color:#28a745;">{data['status']}</span>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                str_launch.markdown("<br>", unsafe_allow_html=True)

                if str_launch.button(
                    "📍 Confirm Location via GPS (Find My Farm)"
                ):
                    str_launch.session_state["gps_location"] = (
                        f"{data['gps_coords']} (Verified Farmland)"
                    )
                    str_launch.success(
                        f"✓ GPS Coordinates matched with {data['farm_id']}!"
                    )

                if "gps_location" in str_launch.session_state:
                    str_launch.info(
                        "Farm GPS Status:"
                        f" {str_launch.session_state['gps_location']}"
                    )

        elif role == "Business (Merchant)":
            str_launch.markdown("---")
            str_launch.markdown("### 🏪 Business Verification")
            cipc_no = str_launch.text_input("CIPC / VAT Registration Number:")

        str_launch.markdown("<br>", unsafe_allow_html=True)
        if str_launch.button("🚀 Confirm & Complete Registration"):
            if name_input and email:
                str_launch.session_state["is_registered"] = True

                # Safely retrieve agri_data (handles None values correctly)
                agri_data = (
                    str_launch.session_state.get("fetched_agri_data") or {}
                )

                str_launch.session_state["user_profile"] = {
                    "name": name_input,
                    "email": email,
                    "role": role,
                    "farm_name": agri_data.get("farm_name", "N/A"),
                    "gps": str_launch.session_state.get("gps_location", "N/A"),
                }
                str_launch.success("Verification Successful! Welcome to XCHEF.")
                str_launch.rerun()
            else:
                str_launch.error("Please fill in your Name and Email.")
else:
    # Sidebar
    str_launch.sidebar.title("👤 Active Verified Account")
    str_launch.sidebar.write(
        f"**Name:** {str_launch.session_state['user_profile']['name']}"
    )
    str_launch.sidebar.write(
        f"**Role:** {str_launch.session_state['user_profile']['role']}"
    )
    if str_launch.session_state["user_profile"]["farm_name"] != "N/A":
        str_launch.sidebar.write(
            "**Entity:**"
            f" {str_launch.session_state['user_profile']['farm_name']}"
        )
    if str_launch.session_state["user_profile"]["gps"] != "N/A":
        str_launch.sidebar.write("**Farm GPS:** Verified 📍")

    if str_launch.sidebar.button("🔒 Log Out / Reset"):
        str_launch.session_state["is_registered"] = False
        str_launch.session_state["fetched_agri_data"] = None
        if "gps_location" in str_launch.session_state:
            del str_launch.session_state["gps_location"]
        str_launch.rerun()

    str_launch.title("👑 XCHEF | Enterprise Platform & Payment Engine")

    tab1, tab2 = str_launch.tabs([
        "💳 Interactive XCHEFPAY Simulator (Proof for Investors)",
        "📄 AI Master Blueprint Generator",
    ])

    # ------------------------------------------
    # TAB 1: INTERACTIVE PAYMENT SIMULATOR
    # ------------------------------------------
    with tab1:
        str_launch.subheader(
            "⚡ Live XCHEF-P Payment & Treasury Engine Simulation"
        )
        str_launch.write(
            "This module simulates how money flows through the XCHEF ecosystem and"
            " how transaction adoption increases the XCHEF-E token value."
        )

        # DISPLAY ALL 5 WALLETS + TRADING TOKEN VALUE CARD
        c1, c2, c3, c4, c5, c6 = str_launch.columns(6)
        with c1:
            str_launch.markdown(
                '<div class="metric-card"><div class="metric-title">🛒 Consumer'
                ' Wallet</div><div'
                ' class="metric-value">'
                f'{str_launch.session_state["wallets"]["Consumer"]:.2f} P</div></div>',
                unsafe_allow_html=True,
            )
        with c2:
            str_launch.markdown(
                '<div class="metric-card"><div class="metric-title">🚜 Farmer'
                ' Wallet</div><div'
                ' class="metric-value">'
                f'{str_launch.session_state["wallets"]["Farmer"]:.2f} P</div></div>',
                unsafe_allow_html=True,
            )
        with c3:
            str_launch.markdown(
                '<div class="metric-card"><div class="metric-title">🏪 Merchant'
                ' Wallet</div><div'
                ' class="metric-value">'
                f'{str_launch.session_state["wallets"]["Merchant"]:.2f} P</div></div>',
                unsafe_allow_html=True,
            )
        with c4:
            str_launch.markdown(
                '<div class="metric-card"><div class="metric-title">🏛️ XCHEF'
                ' Treasury</div><div'
                ' class="metric-value">'
                f'{str_launch.session_state["wallets"]["Treasury_Inflows"]:.2f}'
                " P</div></div>",
                unsafe_allow_html=True,
            )
        with c5:
            str_launch.markdown(
                '<div class="metric-card"><div class="metric-title">🌟'
                ' Rewards</div><div'
                ' class="metric-value">'
                f'{str_launch.session_state["wallets"]["Consumer_Rewards"]:.2f}'
                " E</div></div>",
                unsafe_allow_html=True,
            )
        with c6:
            str_launch.markdown(
                '<div class="metric-card-token"><div class="metric-title">📈'
                ' XCHEF-E Price</div><div'
                ' class="token-value">$'
                f'{str_launch.session_state["xchef_e_price"]:.4f}</div></div>',
                unsafe_allow_html=True,
            )

        str_launch.markdown("---")

        st_col_a, st_col_b = str_launch.columns([1, 1])

        with st_col_a:
            str_launch.subheader("🛒 Execute Simulation Payment")
            amount = str_launch.number_input(
                "Transaction Amount ($ / XCHEF-P):",
                min_value=1.0,
                value=100.0,
                step=10.0,
            )
            transaction_type = str_launch.selectbox(
                "Select Transaction Type:",
                [
                    (
                        "Verified Farmer Purchases Inventory (5% Productive"
                        " Discount)"
                    ),
                    "Consumer Purchases Food from Merchant (2% Fee + 1% Cashback)",
                    "Fiat On-Ramp (10% Treasury Deposit Fee)",
                ],
            )

            if str_launch.button("💸 Simulate Payment Now"):
                # Every transaction increases the XCHEF-E token price based on volume (Adoption Curve)
                price_increase = amount * 0.00005
                str_launch.session_state["xchef_e_price"] += price_increase

                if transaction_type.startswith("Verified Farmer Purchases"):
                    if (
                        "Farmer"
                        not in str_launch.session_state["user_profile"]["role"]
                    ):
                        str_launch.warning(
                            "⚠️ Only verified Farmers with API &"
                            " GPS farm verification qualify for the 5%"
                            " Farmer Discount!"
                        )
                    else:
                        discount = amount * 0.05
                        final_amount = amount - discount

                        if (
                            str_launch.session_state["wallets"]["Farmer"]
                            >= final_amount
                        ):
                            str_launch.session_state["wallets"][
                                "Farmer"
                            ] -= final_amount
                            treasury_fee = amount * 0.01
                            str_launch.session_state["wallets"][
                                "Treasury_Inflows"
                            ] += treasury_fee

                            str_launch.session_state["tx_history"].insert(
                                0,
                                f"🚜 Verified Farmer ({str_launch.session_state['user_profile']['name']} - {str_launch.session_state['user_profile']['farm_name']}) buys inventory for {amount:.2f} with a 5% Farmer Discount ({discount:.2f} off). XCHEF-E price increased to ${str_launch.session_state['xchef_e_price']:.4f}!",
                            )
                            str_launch.success(
                                "Productive Farmer Transaction Successful with"
                                " Discount!"
                            )
                            str_launch.rerun()
                        else:
                            str_launch.error(
                                "Insufficient funds in Farmer Wallet!"
                            )

                elif transaction_type.startswith("Consumer Purchases Food"):
                    fee = amount * 0.02
                    cashback = amount * 0.01
                    net_merchant = amount - fee

                    if (
                        str_launch.session_state["wallets"]["Consumer"]
                        >= amount
                    ):
                        str_launch.session_state["wallets"][
                            "Consumer"
                        ] -= amount
                        str_launch.session_state["wallets"][
                            "Merchant"
                        ] += net_merchant
                        str_launch.session_state["wallets"][
                            "Treasury_Inflows"
                        ] += fee
                        str_launch.session_state["wallets"][
                            "Consumer_Rewards"
                        ] += cashback

                        str_launch.session_state["tx_history"].insert(
                            0,
                            f"✅ Consumer spends {amount:.2f} XCHEF-P. Merchant receives {net_merchant:.2f}, Treasury receives {fee:.2f} fee, Consumer receives {cashback:.2f} XCHEF-E cashback. Coin price now ${str_launch.session_state['xchef_e_price']:.4f}!",
                        )
                        str_launch.success(
                            "Consumer Transaction processed successfully!"
                        )
                        str_launch.rerun()
                    else:
                        str_launch.error(
                            "Insufficient funds in Consumer Wallet!"
                        )

                elif transaction_type.startswith("Fiat On-Ramp"):
                    onramp_fee = amount * 0.10
                    net_credit = amount - onramp_fee
                    str_launch.session_state["wallets"][
                        "Consumer"
                    ] += net_credit
                    str_launch.session_state["wallets"][
                        "Treasury_Inflows"
                    ] += onramp_fee
                    str_launch.session_state["tx_history"].insert(
                        0,
                        f"💵 Fiat On-Ramp of ${amount:.2f}. Treasury receives {onramp_fee:.2f} deposit fee. Buyer receives {net_credit:.2f} XCHEF-P. Coin price now ${str_launch.session_state['xchef_e_price']:.4f}!",
                    )
                    str_launch.success("Fiat On-Ramp Successful!")
                    str_launch.rerun()

        with st_col_b:
            str_launch.subheader("📜 Real-Time Transaction Log")
            if str_launch.session_state["tx_history"]:
                for log in str_launch.session_state["tx_history"][:6]:
                    str_launch.info(log)
            else:
                str_launch.write(
                    "No transactions executed yet. Click the button on the left"
                    " to simulate!"
                )

    # ------------------------------------------
    # TAB 2: AI MASTER BLUEPRINT GENERATOR
    # ------------------------------------------
    with tab2:
        str_launch.subheader(
            "📄 Fast-Track: Upload a Project Document (PDF, DOCX, TXT, MD)"
        )
        uploaded_file = str_launch.file_uploader(
            "Drag & drop your Whitepaper or Pitch Deck PDF here:",
            type=["pdf", "docx", "txt", "md"],
        )

        document_content = ""
        if uploaded_file is not None:
            document_content = read_document_texts(uploaded_file)
            str_launch.success(
                f"✓ {uploaded_file.name} successfully loaded! Ready to process."
            )

        str_launch.markdown("---")
        str_launch.subheader(
            "⚙️ Project Parameters (Optional if a document is uploaded)"
        )

        model_type = str_launch.selectbox(
            "Select your Economic Architecture:",
            [
                (
                    "Dual-Token Model (Stablecoin + Economic Growth Token)"
                ),
                "Single Deflationary Utility Token",
                "Asset-Backed / Commodity-Pegged Token Model",
                "Hybrid Governance & Reward Token Model",
            ],
        )
        utility_description = str_launch.text_area(
            "1. Token Utility & Ecosystem Incentives (Utility & Staking):", height=80
        )
        supply_description = str_launch.text_area(
            "2. Supply & Distribution (Supply, Vesting & Allocation):",
            height=80,
        )
        treasury_description = str_launch.text_area(
            "3. Treasury Rules & Value Capture (Treasury Flows & Value"
            " Capture):",
            height=80,
        )

        str_launch.markdown("<br>", unsafe_allow_html=True)

        if str_launch.button("🚀 Generate Full Project Blueprint"):
            has_text_in_boxes = bool(
                utility_description.strip()
                or supply_description.strip()
                or treasury_description.strip()
            )
            has_document = bool(document_content.strip())

            if not has_text_in_boxes and not has_document:
                str_launch.error(
                    "⚠️ Please fill in at least one text box OR upload a"
                    " PDF/Word document!"
                )
            else:
                with str_launch.spinner(
                    "AI analyzing your document and parameters... (this"
                    " takes 5-10 seconds)"
                ):
                    master_report = analyze_grand_vision(
                        model_type,
                        utility_description,
                        supply_description,
                        treasury_description,
                        document_content,
                    )
                    str_launch.session_state["main_report"] = master_report
                    str_launch.session_state["chat_history"] = [{
                        "role": "ai",
                        "text": (
                            "Master Blueprint generated successfully. Ask me"
                            " any follow-up questions!"
                        ),
                    }]
                str_launch.rerun()

        if "main_report" in str_launch.session_state:
            str_launch.subheader("📊 Your Official Project Blueprint")
            str_launch.download_button(
                label="💾 Download Master Blueprint (.md)",
                data=str_launch.session_state["main_report"],
                file_name="XCHEF_Master_Blueprint.md",
            )
            str_launch.markdown(
                f'<div class="report-box">{str_launch.session_state["main_report"]}</div>',
                unsafe_allow_html=True,
            )
