import streamlit as st
import pyshorteners
from knowledge_integration import initialize_knowledge_system
from utils.joint_profiles import JOINT_PROFILES, UnitConverter
from utils.pdf_generator import generate_calculation_summary
import os
import tempfile
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Silicone Sealant Calculator",
    page_icon="🔧",
    layout="wide"
)

# Initialize knowledge system
knowledge = initialize_knowledge_system()

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .joint-diagram {
        border: 2px solid #f0f2f6;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and Introduction
st.title("🔧 Silicone Sealant Calculator")
st.markdown("""
This calculator helps you determine the amount of silicone sealant needed for your project.
Simply enter the dimensions of the area to be sealed, and we'll calculate the volume required.
""")

# Create two columns for the main layout
left_col, right_col = st.columns([2, 1])

with left_col:
    # Instructions and formula explanation
    with st.expander("📖 Instructions and Formula Explanation", expanded=True):
        st.markdown("""
        ### How to Use
        1. Select a joint profile or enter custom dimensions
        2. Enter the joint measurements in your preferred units
        3. Click calculate to see the required volume
        4. Download a detailed PDF report of your calculations
        
        ### Formula Used
        Volume (L) = Joint Width (cm) × Joint Depth (cm) × Joint Length (cm) ÷ 1000
        
        ### Tips
        - Measure your gap carefully for accurate results
        - Consider adding 15% extra for wastage
        - Always check manufacturer recommendations for your specific application
        """)

    # Joint profile selection
    st.subheader("1. Select Joint Profile")
    profile_name = st.selectbox(
        "Choose a joint profile",
        list(JOINT_PROFILES.keys()) + ["Custom"]
    )

    # Unit selection
    unit_options = ["mm", "cm", "m"]
    selected_unit = st.selectbox("Select measurement unit", unit_options, index=1)

    # Input fields with unit conversion
    st.subheader("2. Enter Measurements")
    col1, col2, col3, col4 = st.columns(4)

    # Get default values from profile
    if profile_name != "Custom":
        profile = JOINT_PROFILES[profile_name]
        default_width = profile.typical_width
        default_depth = profile.typical_depth
    else:
        default_width = 0.5
        default_depth = 0.5

    with col1:
        width = st.number_input(
            f"Joint width ({selected_unit})", 
            min_value=0.1, 
            value=UnitConverter.convert(default_width, "cm", selected_unit),
            step=0.1,
            format="%.1f",
            help="The width of the joint to be sealed"
        )

    with col2:
        depth = st.number_input(
            f"Joint depth ({selected_unit})", 
            min_value=0.1, 
            value=UnitConverter.convert(default_depth, "cm", selected_unit),
            step=0.1,
            format="%.1f",
            help="The depth of the joint to be sealed"
        )

    with col3:
        length = st.number_input(
            f"Joint length ({selected_unit})", 
            min_value=0.1, 
            value=UnitConverter.convert(100.0, "cm", selected_unit),
            step=0.1,
            format="%.1f",
            help="The length of the joint to be sealed"
        )

    with col4:
        package_type = st.selectbox(
            "Package Type",
            ["Sausage (600ml)", "Cartridge (300ml)"],
            help="Select the type of sealant package you plan to use"
        )

    # Convert all measurements to cm for calculation
    width_cm = UnitConverter.convert(width, selected_unit, "cm")
    depth_cm = UnitConverter.convert(depth, selected_unit, "cm")
    length_cm = UnitConverter.convert(length, selected_unit, "cm")

    # Wastage checkbox
    allow_wastage = st.checkbox("Allow 15% wastage", value=True,
                              help="Add 15% extra to account for wastage during application")

with right_col:
    # Display joint diagram
    st.subheader("Joint Profile Diagram")
    if profile_name != "Custom":
        profile = JOINT_PROFILES[profile_name]
        st.markdown(f"""
        <div class="joint-diagram">
        <h4>{profile.name}</h4>
        <p>{profile.description}</p>
        <img src="{profile.diagram_path}" alt="{profile.name}" width="100%">
        </div>
        """, unsafe_allow_html=True)

# Calculation
if st.button("Calculate Required Sealant"):
    # Prepare input data
    inputs = {
        'width': width_cm,
        'depth': depth_cm,
        'length': length_cm,
        'package_type': package_type,
        'allow_wastage': allow_wastage,
        'unit': selected_unit,
        'profile': profile_name
    }
    
    # Calculate base volume in litres
    base_volume = (width_cm * depth_cm * length_cm) / 1000
    
    # Add wastage if enabled
    volume = base_volume * 1.15 if allow_wastage else base_volume
    
    # Convert volume to ml for package calculations
    volume_ml = volume * 1000
    
    # Get package size based on selection
    package_size = 600 if package_type == "Sausage (600ml)" else 300
    package_name = "sausages" if package_type == "Sausage (600ml)" else "cartridges"
    
    packages_needed = volume_ml / package_size
    full_packages = int(packages_needed)
    partial_package = packages_needed - full_packages
    
    # Prepare results data
    results = {
        'base_volume': base_volume,
        'final_volume': volume,
        'volume_ml': volume_ml,
        'packages_needed': packages_needed,
        'full_packages': full_packages,
        'partial_package': partial_package
    }
    
    # Log calculation to knowledge system
    knowledge.log_calculation(inputs, results)
    
    # Display results
    st.markdown("### Results")
    
    if full_packages == 0:
        st.info(f"You need **1** {package_name[:-1]} (using {(packages_needed * 100):.1f}% of it)")
    else:
        if partial_package > 0:
            st.info(f"You need **{full_packages}** full {package_name} plus **1** partial {package_name[:-1]} " +
                   f"(using {(partial_package * 100):.1f}% of it)")
        else:
            st.info(f"You need **{full_packages}** full {package_name}")
    
    # Display volume details with wastage information
    if allow_wastage:
        st.write(f"Base volume required: {base_volume:.3f} L ({base_volume * 1000:.1f} ml)")
        st.write(f"Volume with 15% wastage: {volume:.3f} L ({volume * 1000:.1f} ml)")
    else:
        st.write(f"Total volume required: {volume:.3f} L ({volume * 1000:.1f} ml)")
    
    # Generate PDF report
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        pdf_path = generate_calculation_summary({**inputs, **results}, tmp_file.name)
        with open(pdf_path, 'rb') as pdf_file:
            st.download_button(
                label="Download Calculation Summary (PDF)",
                data=pdf_file,
                file_name=f"sealant_calculation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf"
            )

# Display insights from knowledge system
with st.expander("📊 Usage Insights", expanded=False):
    insights = knowledge.get_insights()
    if insights:
        for insight in insights:
            st.write(f"- {insight}")
    else:
        st.write("No insights available yet. Use the calculator more to generate insights!")

# Share section
with st.expander("🔗 Share this Calculator"):
    st.markdown("""
    To share this calculator with others:
    1. Deploy the app using Streamlit Sharing
    2. Copy and share the generated URL
    
    Note: This is a local version. For sharing, deploy the app on Streamlit Cloud or a similar service.
    """)