import os
import time
import docx
import pandas as pd
from google import genai
from pypdf import PdfReader
import streamlit as str_launch

# =========================================================
# 1. KONFIGURASIE & AI OPSTEL
# =========================================================

API_KEY = os.environ.get("GCP_API_KEY", "")
client = genai.Client(api_key=API_KEY)
def read_document_texts(file) -> str:
    """read text automatically from TXT, MD, PDF or DOCX files."""
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


def analiseer_groot_visie(
    model_type: str,
    utility_discription: str,
    supply_discription: str,
    treasury_discription: str,
    extra_document_texts: str = "",
) -> str:
    konteks_en_instruksies = (
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

    volledige_prompt = (
        f"{konteks_en_instruksies}\n\n--- FOUNDER'S PROJECT DATA ---\n• Chosen"
        f" Architecture: {model_tipe}\n• Utility & Incentives:"
        f" {nut_beskrywing if nut_beskrywing.strip() else 'Extract directly from document'}\n•"
        f" Supply & Allocation:"
        f" {supply_beskrywing if supply_beskrywing.strip() else 'Extract directly from document'}\n•"
        f" Treasury Flows:"
        f" {treasury_beskrywing if treasury_beskrywing.strip() else 'Extract directly from document'}\n"
    )
    if ekstra_dokument_teks:
        volledige_prompt += (
            "\n--- FULL ATTACHED DOCUMENT / WHITE-PAPER CONTENT"
            f" ---\n{ekstra_dokument_teks}\n"
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents=volledige_prompt
    )
    return response.text


# 10 VERSKILLENDE MOCK ENTERPRISES
MOCK_FARMS_REGISTRY = [
    {
        "entiteit": "Green Valley Agri (Pty) Ltd",
        "plaas": "Farm 402 - Klerksdorp District",
        "gps": 'S 26° 52\' 10", E 26° 40\' 03"',
    },
    {
        "entiteit": "Goudveld Graan Boerdery BK",
        "plaas": "Plaas 112 - Potchefstroom Sektor",
        "gps": 'S 26° 42\' 15", E 27° 05\' 44"',
    },
    {
        "entiteit": "Highveld Citrus & Dairy Enterprise",
        "plaas": "Farm 804 - Bethal District",
        "gps": 'S 26° 27\' 01", E 29° 27\' 50"',
    },
    {
        "entiteit": "Bramley Livestock & Crops (Pty) Ltd",
        "plaas": "Plaas 305 - Middelburg Oos",
        "gps": 'S 25° 46\' 19", E 29° 28\' 33"',
    },
    {
        "entiteit": "Karoo Eco-Agri Co-Op",
        "plaas": "Farm 12 - Graaff-Reinet District",
        "gps": 'S 32° 15\' 08", E 24° 32\' 11"',
    },
    {
        "entiteit": "Overberg Wheat & Wool Holdings",
        "plaas": "Plaas 567 - Caledon Sektor",
        "gps": 'S 34° 13\' 44", E 19° 25\' 22"',
    },
    {
        "entiteit": "Limpopo Subtropical Produce (Pty) Ltd",
        "plaas": "Farm 921 - Tzaneen Valley",
        "gps": 'S 23° 49\' 55", E 30° 09\' 40"',
    },
    {
        "entiteit": "Vrystaat Mielies & Soja BK",
        "plaas": "Plaas 208 - Kroonstad Sektor",
        "gps": 'S 27° 39\' 12", E 27° 14\' 02"',
    },
    {
        "entiteit": "Kalahari Beef Exporters",
        "plaas": "Farm 44 - Vryburg West",
        "gps": 'S 26° 57\' 30", E 24° 43\' 50"',
    },
    {
        "entiteit": "Natal Midlands Organics Co.",
        "plaas": "Farm 610 - Howick District",
        "gps": 'S 29° 28\' 04", E 30° 13\' 18"',
    },
]

# ==========================================
# 2. SESSION STATE (GEBRUIKER, WALLETS & TOKEN PRYS)
# ==========================================

if "is_registered" not in str_launch.session_state:
    str_launch.session_state["is_registered"] = False

if "user_profile" not in str_launch.session_state:
    str_launch.session_state["user_profile"] = {}

if "fetched_agri_data" not in str_launch.session_state:
    str_launch.session_state["fetched_agri_data"] = None

# BEURSIE SALDO'S
if "wallets" not in str_launch.session_state:
    str_launch.session_state["wallets"] = {
        "Consumer": 1000.00,
        "Merchant": 5000.00,
        "Farmer": 2500.00,
        "Treasury_Inflows": 150.00,
        "Consumer_Rewards": 25.00,
    }

# XCHEF-E TRADING TOKEN PRYS (AANVANGSWAARDE $0.0100)
if "xchef_e_price" not in str_launch.session_state:
    str_launch.session_state["xchef_e_price"] = 0.0100

if "tx_history" not in str_launch.session_state:
    str_launch.session_state["tx_history"] = []

# ==========================================
# 3. PREMIUM FINTECH VISUELE STYLING (CSS)
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

if "chat_geskiedenis" not in str_launch.session_state:
    str_launch.session_state["chat_geskiedenis"] = []

# ==========================================
# 4. HOOF LOGIKA: REGISTRASIE vs DASHBOARD
# ==========================================

if not str_launch.session_state["is_registered"]:
    str_launch.title("👑 Welcome to XCHEF | Enterprise Onboarding")
    str_launch.write(
        "Voltooi jou outomatiese verifikasie om toegang tot die XCHEF"
        " Ekosisteem te kry."
    )
    str_launch.markdown("<br>", unsafe_allow_html=True)

    col_centered = str_launch.columns([1, 2, 1])[1]
    with col_centered:
        str_launch.subheader("🔒 Create & Verify Profile")
        rol = str_launch.selectbox(
            "Kies jou Rol op die Platform:",
            ["Farmer (Boer)", "Consumer (Verbruiker)", "Business (Handelaar)"],
        )

        naam_input = str_launch.text_input(
            "Volle Naam & Van:", value="Johannes van der Merwe"
        )
        email = str_launch.text_input("E-pos Adres:")

        if rol == "Farmer (Boer)":
            str_launch.markdown("---")
            str_launch.markdown(
                "### 🚜 Automated National Agri-Registry Lookup"
            )

            landbou_no = str_launch.text_input(
                "Voer Landbou Registrasie / Belasting ID in:",
                value="AGRI-3857-ZA",
            )

            if str_launch.button("🔍 Fetch Agri Registry Data (API Sync)"):
                if not naam_input.strip():
                    str_launch.error("Tik asseblief eers jou Naam & Van bo in!")
                else:
                    with str_launch.spinner(
                        "Verbind tans met Sentrale Landbou Databasis..."
                    ):
                        time.sleep(1.2)
                        digits = "".join(filter(str.isdigit, landbou_no))
                        index = (
                            int(digits) % len(MOCK_FARMS_REGISTRY)
                            if digits
                            else 0
                        )
                        gekoose_plaas = MOCK_FARMS_REGISTRY[index]

                        str_launch.session_state["fetched_agri_data"] = {
                            "eienaar": naam_input,
                            "boerdery_naam": gekoose_plaas["entiteit"],
                            "plaas_id": gekoose_plaas["plaas"],
                            "gps_coords": gekoose_plaas["gps"],
                            "status": "VERIFIED ACTIVE PRODUCER ✅",
                        }
                    str_launch.success(
                        f"✓ Databasis gevind vir {naam_input}! Besonderhede"
                        " gelaai."
                    )
                    str_launch.rerun()

            if str_launch.session_state["fetched_agri_data"]:
                data = str_launch.session_state["fetched_agri_data"]
                str_launch.markdown(
                    f"""
                <div class="agri-card">
                    <b>🏛️ Geregistreerde Entiteit:</b> {data['boerdery_naam']}<br>
                    <b>👤 Geregistreerde Eienaar:</b> {data['eienaar']}<br>
                    <b>📍 Regstreekse Land-ID:</b> {data['plaas_id']}<br>
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
                        f"✓ GPS Koördinate gepas met {data['plaas_id']}!"
                    )

                if "gps_location" in str_launch.session_state:
                    str_launch.info(
                        "Plaas GPS Status:"
                        f" {str_launch.session_state['gps_location']}"
                    )

        elif rol == "Business (Handelaar)":
            str_launch.markdown("---")
            str_launch.markdown("### 🏪 Besigheids Verifikasie")
            cipc_no = str_launch.text_input("CIPC / BTW Registrasienommer:")

        str_launch.markdown("<br>", unsafe_allow_html=True)
        if str_launch.button("🚀 Confirm & Complete Registration"):
            if naam_input and email:
                str_launch.session_state["is_registered"] = True

                # Veilig verkry agri_data (hanteer None waardes korrek)
                agri_data = (
                    str_launch.session_state.get("fetched_agri_data") or {}
                )

                str_launch.session_state["user_profile"] = {
                    "naam": naam_input,
                    "email": email,
                    "rol": rol,
                    "boerdery_naam": agri_data.get("boerdery_naam", "N/A"),
                    "gps": str_launch.session_state.get("gps_location", "N/A"),
                }
                str_launch.success("Verifikasie Suksesvol! Welkom by XCHEF.")
                str_launch.rerun()
            else:
                str_launch.error("Vul asseblief jou Naam en E-pos in.")
else:
    # Sidebar
    str_launch.sidebar.title("👤 Active Verified Account")
    str_launch.sidebar.write(
        f"**Naam:** {str_launch.session_state['user_profile']['naam']}"
    )
    str_launch.sidebar.write(
        f"**Rol:** {str_launch.session_state['user_profile']['rol']}"
    )
    if str_launch.session_state["user_profile"]["boerdery_naam"] != "N/A":
        str_launch.sidebar.write(
            "**Entiteit:**"
            f" {str_launch.session_state['user_profile']['boerdery_naam']}"
        )
    if str_launch.session_state["user_profile"]["gps"] != "N/A":
        str_launch.sidebar.write("**Plaas GPS:** Verified 📍")

    if str_launch.sidebar.button("🔒 Log Out / Reset"):
        str_launch.session_state["is_registered"] = False
        str_launch.session_state["fetched_agri_data"] = None
        if "gps_location" in str_launch.session_state:
            del str_launch.session_state["gps_location"]
        str_launch.rerun()

    str_launch.title("👑 XCHEF | Enterprise Platform & Payment Engine")

    tab1, tab2 = str_launch.tabs([
        "💳 Interactive XCHEFPAY Simulator (Bewys vir Beleggers)",
        "📄 AI Master Blueprint Generator",
    ])

    # ------------------------------------------
    # TAB 1: INTERACTIVE PAYMENT SIMULATOR
    # ------------------------------------------
    with tab1:
        str_launch.subheader(
            "⚡ Lewendige XCHEF-P Payment & Treasury Engine Simulasie"
        )
        str_launch.write(
            "Hierdie module simuleer hoe geld deur die XCHEF-ekosisteem vloei en"
            " hoe transaksie-aanname die XCHEF-E token-waarde verhoog."
        )

        # VERTOON AL 5 WALLETS + DIE TRADING TOKEN WAARDE BLOK
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
            str_launch.subheader("🛒 Voer 'n Simulasie-Betaling Uit")
            bedrag = str_launch.number_input(
                "Transaksie Bedrag ($ / XCHEF-P):",
                min_value=1.0,
                value=100.0,
                step=10.0,
            )
            tipe_transaksie = str_launch.selectbox(
                "Kies Transaksie Tipe:",
                [
                    (
                        "Geverifieerde Boer Koop Voorraad (5% Productive"
                        " Discount)"
                    ),
                    "Verbruiker Koop Kos by Handelaar (2% Fee + 1% Cashback)",
                    "Fiat On-Ramp (10% Treasury Deposit Fee)",
                ],
            )

            if str_launch.button("💸 Simuleer Betaling Nou"):
                # Elke transaksie verhoog die XCHEF-E token-prys gebaseer op volume (Adoption Curve)
                prys_stiging = bedrag * 0.00005
                str_launch.session_state["xchef_e_price"] += prys_stiging

                if tipe_transaksie.startswith("Geverifieerde Boer Koop"):
                    if (
                        "Farmer"
                        not in str_launch.session_state["user_profile"]["rol"]
                    ):
                        str_launch.warning(
                            "⚠️ Slegs geverifieerde Boere met API &"
                            " GPS-plaasverifikasie kwalifiseer vir die 5%"
                            " Boere-Korting!"
                        )
                    else:
                        korting = bedrag * 0.05
                        eind_bedrag = bedrag - korting

                        if (
                            str_launch.session_state["wallets"]["Farmer"]
                            >= eind_bedrag
                        ):
                            str_launch.session_state["wallets"][
                                "Farmer"
                            ] -= eind_bedrag
                            treasury_fee = bedrag * 0.01
                            str_launch.session_state["wallets"][
                                "Treasury_Inflows"
                            ] += treasury_fee

                            str_launch.session_state["tx_history"].insert(
                                0,
                                f"🚜 Geverifieerde Boer ({str_launch.session_state['user_profile']['naam']} - {str_launch.session_state['user_profile']['boerdery_naam']}) koop voorraad vir {bedrag:.2f} met 5% Boere-Korting ({korting:.2f} af). XCHEF-E prys styg na ${str_launch.session_state['xchef_e_price']:.4f}!",
                            )
                            str_launch.success(
                                "Produktiewe Boere-Transaksie Suksesvol met"
                                " Korting!"
                            )
                            str_launch.rerun()
                        else:
                            str_launch.error(
                                "Onvoldoende fondse in Farmer Wallet!"
                            )

                elif tipe_transaksie.startswith("Verbruiker Koop Kos"):
                    fee = bedrag * 0.02
                    cashback = bedrag * 0.01
                    netto_merchant = bedrag - fee

                    if (
                        str_launch.session_state["wallets"]["Consumer"]
                        >= bedrag
                    ):
                        str_launch.session_state["wallets"][
                            "Consumer"
                        ] -= bedrag
                        str_launch.session_state["wallets"][
                            "Merchant"
                        ] += netto_merchant
                        str_launch.session_state["wallets"][
                            "Treasury_Inflows"
                        ] += fee
                        str_launch.session_state["wallets"][
                            "Consumer_Rewards"
                        ] += cashback

                        str_launch.session_state["tx_history"].insert(
                            0,
                            f"✅ Verbruiker spandeer {bedrag:.2f} XCHEF-P. Handelaar kry {netto_merchant:.2f}, Tesourie kry {fee:.2f} fee, Verbruiker kry {cashback:.2f} XCHEF-E cashback. Coin prys nou ${str_launch.session_state['xchef_e_price']:.4f}!",
                        )
                        str_launch.success(
                            "Verbruiker Transaksie suksesvol verwerk!"
                        )
                        str_launch.rerun()
                    else:
                        str_launch.error(
                            "Onvoldoende fondse in Consumer Wallet!"
                        )

                elif tipe_transaksie.startswith("Fiat On-Ramp"):
                    onramp_fee = bedrag * 0.10
                    netto_krediet = bedrag - onramp_fee
                    str_launch.session_state["wallets"][
                        "Consumer"
                    ] += netto_krediet
                    str_launch.session_state["wallets"][
                        "Treasury_Inflows"
                    ] += onramp_fee
                    str_launch.session_state["tx_history"].insert(
                        0,
                        f"💵 Fiat On-Ramp van ${bedrag:.2f}. Tesourie kry {onramp_fee:.2f} deposit fee. Koper kry {netto_krediet:.2f} XCHEF-P. Coin prys nou ${str_launch.session_state['xchef_e_price']:.4f}!",
                    )
                    str_launch.success("Fiat On-Ramp Suksesvol!")
                    str_launch.rerun()

        with st_col_b:
            str_launch.subheader("📜 Intydse Transaksie Logboek")
            if str_launch.session_state["tx_history"]:
                for log in str_launch.session_state["tx_history"][:6]:
                    str_launch.info(log)
            else:
                str_launch.write(
                    "Geen transaksies nog uitgevoer nie. Klik die knoppie links"
                    " om te simuleer!"
                )

    # ------------------------------------------
    # TAB 2: AI MASTER BLUEPRINT GENERATOR
    # ------------------------------------------
    with tab2:
        str_launch.subheader(
            "📄 Fast-Track: Laai 'n Projek-dokument op (PDF, DOCX, TXT, MD)"
        )
        opgelaaide_lêer = str_launch.file_uploader(
            "Sleep jou Whitepaper of Pitch Deck PDF hierin:",
            type=["pdf", "docx", "txt", "md"],
        )

        dokument_inhoud = ""
        if opgelaaide_lêer is not None:
            dokument_inhoud = lees_dokument_teks(opgelaaide_lêer)
            str_launch.success(
                f"✓ {opgelaaide_lêer.name} suksesvol gelaai! Reg om te verwerk."
            )

        str_launch.markdown("---")
        str_launch.subheader(
            "⚙️ Projek Parameters (Opsioneel as 'n dokument opgelaai is)"
        )

        model_tipe = str_launch.selectbox(
            "Kies jou Ekonomiese Argitektuur:",
            [
                (
                    "Dual-Token Model (Stablecoin + Economic Growth Token)"
                ),
                "Single Deflationary Utility Token",
                "Asset-Backed / Commodity-Pegged Token Model",
                "Hybrid Governance & Reward Token Model",
            ],
        )
        nut_beskrywing = str_launch.text_area(
            "1. Token-nut & Ekosisteem-insentiewe (Utility & Staking):", height=80
        )
        supply_beskrywing = str_launch.text_area(
            "2. Voorsiening & Distribusie (Supply, Vesting & Allocation):",
            height=80,
        )
        treasury_beskrywing = str_launch.text_area(
            "3. Tesourie Reëls & Waarde-vanging (Treasury Flows & Value"
            " Capture):",
            height=80,
        )

        str_launch.markdown("<br>", unsafe_allow_html=True)

        if str_launch.button("🚀 Genereer Volledige Projek Bloudruk"):
            het_teks_in_bokse = bool(
                nut_beskrywing.strip()
                or supply_beskrywing.strip()
                or treasury_beskrywing.strip()
            )
            het_dokument = bool(dokument_inhoud.strip())

            if not het_teks_in_bokse and not het_dokument:
                str_launch.error(
                    "⚠️ Vul asseblief minstens een teksboks in OF laai 'n"
                    " PDF/Word-dokument op!"
                )
            else:
                with str_launch.spinner(
                    "AI besig om jou dokument en parameters te ontleed... (dit"
                    " neem 5-10 sekondes)"
                ):
                    meester_verslag = analiseer_groot_visie(
                        model_tipe,
                        nut_beskrywing,
                        supply_beskrywing,
                        treasury_beskrywing,
                        dokument_inhoud,
                    )
                    str_launch.session_state["hoof_verslag"] = meester_verslag
                    str_launch.session_state["chat_geskiedenis"] = [{
                        "rol": "ai",
                        "teks": (
                            "Master Blueprint generated successfully. Ask me"
                            " any follow-up questions!"
                        ),
                    }]
                str_launch.rerun()

        if "hoof_verslag" in str_launch.session_state:
            str_launch.subheader("📊 Jou Amptelike Projek Bloudruk")
            str_launch.download_button(
                label="💾 Download Master Blueprint (.md)",
                data=str_launch.session_state["hoof_verslag"],
                file_name="XCHEF_Master_Blueprint.md",
            )
            str_launch.markdown(
                f'<div class="report-box">{str_launch.session_state["hoof_verslag"]}</div>',
                unsafe_allow_html=True,
            )