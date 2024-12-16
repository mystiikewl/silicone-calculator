import streamlit as st
import pyshorteners
from knowledge_integration import initialize_knowledge_system
from utils.joint_profiles import JOINT_PROFILES, UnitConverter, JointValidator
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

    # Initialize session state for measurements
    if 'width' not in st.session_state:
        st.session_state.width = None
    if 'depth' not in st.session_state:
        st.session_state.depth = None

    # Joint profile selection
    st.subheader("1. Select Joint Profile")
    profile_name = st.selectbox(
        "Choose a joint profile",
        list(JOINT_PROFILES.keys()) + ["Custom"]
    )

    # Unit selection for width and depth
    unit_options = ["mm", "cm"]
    selected_unit = st.selectbox("Width/Depth Unit:", unit_options, index=1)

    # Use session state values if they exist, otherwise use defaults
    default_width = st.session_state.width if st.session_state.width is not None else (1.0 if selected_unit == "cm" else 10.0)
    default_depth = st.session_state.depth if st.session_state.depth is not None else (1.0 if selected_unit == "cm" else 10.0)

    # Input fields with unit conversion
    st.subheader("2. Enter Measurements")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        width = st.number_input(f"Joint Width ({selected_unit})", 
                              min_value=0.0, 
                              value=float(default_width),
                              step=0.1 if selected_unit == "cm" else 1.0,
                              help=f"Enter the width of the joint in {selected_unit}")

    with col2:
        depth = st.number_input(f"Joint Depth ({selected_unit})", 
                              min_value=0.0,
                              value=float(default_depth),
                              step=0.1 if selected_unit == "cm" else 1.0,
                              help=f"Enter the depth of the joint in {selected_unit}")

    with col3:
        length = st.number_input("Joint Length (m)",
                               min_value=0.1,
                               value=1.0,
                               help="Enter the length of the joint in meters")

    with col4:
        package_type = st.selectbox(
            "Package Type",
            ["Sausage (600ml)", "Cartridge (300ml)"],
            help="Select the type of sealant package you plan to use"
        )

    # Convert width and depth to cm for calculations
    if selected_unit == "mm":
        width_cm = UnitConverter.mm_to_cm(width)
        depth_cm = UnitConverter.mm_to_cm(depth)
    else:  # cm
        width_cm = width
        depth_cm = depth

    # Length is already in meters, convert to cm for volume calculation
    length_cm = UnitConverter.m_to_cm(length)

    # Add joint specification guide
    with st.expander("Joint Specifications Guide"):
        # Get the current profile's specifications
        profile_specs = JointValidator.get_profile_specs(profile_name)
        
        # Display the specifications
        st.markdown(f"""
        ### {profile_name} Specifications
        """)
        
        # Profile-specific descriptions
        profile_descriptions = {
            "Square Joint": "Standard profile with width twice the depth (2:1 ratio), providing optimal balance between movement capability and material usage.",
            "Deep Joint": "Deep profile with equal width and depth (1:1 ratio), ideal for joints with limited width but requiring good depth.",
            "Wide Joint": "Wide profile with width twice the depth (2:1 ratio), suitable for larger gaps requiring multiple passes.",
            "V-Joint": "V-shaped profile for corner applications (1.5:1 ratio), uses half the volume of a square joint due to triangular profile.",
            "U-Joint": "U-shaped profile with enhanced movement capability (1.5:1 ratio), requires special tooling for proper formation."
        }
        
        st.markdown(f"""
        #### Profile Description
        {profile_descriptions.get(profile_name, "Custom profile for specific requirements.")}
        
        #### Joint Dimension Guidelines
        - **Width Range**: {profile_specs['min_width_mm']}mm - {profile_specs['max_width_mm']}mm
        - **Depth Range**: {profile_specs['min_depth_mm']}mm - {profile_specs['max_depth_mm']}mm
        - **Ideal Ratio**: Width:Depth = {profile_specs['width_to_depth_ratio']}:1
        - **Tolerance**: ±{int(profile_specs['ratio_tolerance']*100)}% from ideal ratio
        
        #### Profile-Specific Considerations
        1. **Typical Applications**:
           - {"Most common profile type, ideal for general sealing applications" if profile_name == "Square Joint" else
              "Requires backing rod, ideal for joints with limited width but requiring good depth" if profile_name == "Deep Joint" else
              "Suitable for larger gaps, may require multiple application passes" if profile_name == "Wide Joint" else
              "Ideal for corner applications, good for joints with angular movement" if profile_name == "V-Joint" else
              "Suitable for expansion joints, excellent for accommodating multi-directional movement" if profile_name == "U-Joint" else
              "Custom applications"}
           
        2. **Installation Notes**:
           - {"Use backing rod if depth exceeds 10mm" if profile_name == "Square Joint" else
              "Always use backing rod" if profile_name == "Deep Joint" else
              "Depth should not exceed half the width for proper adhesion" if profile_name == "Wide Joint" else
              "Tooling is critical for proper shape formation" if profile_name == "V-Joint" else
              "Requires special tooling for U-shape formation" if profile_name == "U-Joint" else
              "Follow manufacturer guidelines"}

        3. **Volume Considerations**:
           - {"Standard volume calculation" if profile_name == "Square Joint" else
              "Standard volume calculation" if profile_name == "Deep Joint" else
              "Consider multiple passes for large gaps" if profile_name == "Wide Joint" else
              "Volume is approximately half of a square joint due to triangular profile" if profile_name == "V-Joint" else
              "Additional material needed for curved profile" if profile_name == "U-Joint" else
              "Calculate based on specific requirements"}
        
        #### Joint Ratio Examples
        """)
        
        if profile_name == "Square Joint":
            st.markdown("""
            | Correct Ratio | Incorrect Ratio |
            |---|---|
            | 12mm wide x 6mm deep | 10mm wide x 10mm deep |
            | 20mm wide x 10mm deep | 30mm wide x 10mm deep |
            """)
        elif profile_name == "Wide Joint":
            st.markdown("""
            | Correct Ratio | Incorrect Ratio |
            |---|---|
            | 30mm wide x 12mm deep | 30mm wide x 20mm deep |
            | 40mm wide x 12mm deep | 50mm wide x 10mm deep |
            """)
        elif profile_name == "Deep Joint":
            st.markdown("""
            | Correct Ratio | Incorrect Ratio |
            |---|---|
            | 20mm wide x 20mm deep | 10mm wide x 20mm deep |
            | 15mm wide x 18mm deep | 30mm wide x 40mm deep |
            """)
        elif profile_name == "V-Joint":
            st.markdown("""
            | Correct Ratio | Incorrect Ratio |
            |---|---|
            | 15mm wide x 10mm deep | 10mm wide x 10mm deep |
            | 20mm wide x 12mm deep | 30mm wide x 10mm deep |
            """)
        elif profile_name == "U-Joint":
            st.markdown("*Due to the complexity of U-shaped joints, specific dimension recommendations are highly application-specific.*")
        else:
            st.markdown("*Custom profile dimensions should be based on specific project requirements.*")
        
        # Add visual separator
        st.markdown("---")
        
    # Convert measurements for validation
    width_mm = UnitConverter.cm_to_mm(width_cm) if selected_unit == "cm" else width
    depth_mm = UnitConverter.cm_to_mm(depth_cm) if selected_unit == "cm" else depth
    
    # Get recommendations
    recommendations = JointValidator.get_recommended_dimensions(width_mm=width_mm, depth_mm=depth_mm, profile_name=profile_name)
    
    # Validate dimensions with profile
    validation = JointValidator.validate_dimensions(width_mm, depth_mm, profile_name, unit=selected_unit)
    
    # Show recommendations before calculation
    if validation["recommendations"]:
        st.info("📏 " + "\n".join(validation["recommendations"]))
    
    # Show warnings if dimensions are not ideal
    if validation["warnings"]:
        st.warning("⚠️ " + "\n".join(validation["warnings"]))
    
    # Create two columns for recommendation buttons
    rec_col1, rec_col2 = st.columns(2)
    
    with rec_col1:
        if recommendations["recommended_width"] is not None:
            recommended_value = (
                UnitConverter.mm_to_cm(recommendations["recommended_width"]) 
                if selected_unit == "cm" 
                else recommendations["recommended_width"]
            )
            if st.button(f"Use Recommended Width ({recommended_value:.1f} {selected_unit})"):
                st.session_state.width = recommended_value
                st.experimental_rerun()
    
    with rec_col2:
        if recommendations["recommended_depth"] is not None:
            recommended_value = (
                UnitConverter.mm_to_cm(recommendations["recommended_depth"]) 
                if selected_unit == "cm" 
                else recommendations["recommended_depth"]
            )
            if st.button(f"Use Recommended Depth ({recommended_value:.1f} {selected_unit})"):
                st.session_state.depth = recommended_value
                st.experimental_rerun()

    # Wastage checkbox
    allow_wastage = st.checkbox("Allow 15% wastage", value=True,
                              help="Add 15% extra to account for wastage during application")

    # Display joint profile information
    if profile_name != "Custom":
        profile = JOINT_PROFILES[profile_name]
        with st.expander("Joint Profile Details"):
            st.write(f"**Description:** {profile.description}")
            st.write(f"**Typical Dimensions:**")
            st.write(f"- Width: {profile.typical_width} cm")
            st.write(f"- Depth: {profile.typical_depth} cm")
            st.write(f"**Formula:**")
            st.code(profile.formula)
            if profile.notes:
                st.write(f"**Notes:**")
                st.write(profile.notes)

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
