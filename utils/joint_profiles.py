from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class JointProfile:
    name: str
    typical_width: float
    typical_depth: float
    description: str
    diagram_path: str
    formula: str
    notes: str = ""

# Define common joint profiles
JOINT_PROFILES = {
    "Square Joint": JointProfile(
        name="Square Joint",
        typical_width=1.0,
        typical_depth=1.0,
        description="Standard square profile, equal width and depth",
        diagram_path="assets/square_joint.png",
        formula="Volume (L) = Width (cm) × Depth (cm) × Length (m) × 100 ÷ 1000",
        notes="Most common profile. Use backing rod if depth > 10mm. Length is in meters, width/depth in cm."
    ),
    "Deep Joint": JointProfile(
        name="Deep Joint",
        typical_width=1.0,
        typical_depth=2.0,
        description="Deep profile, depth greater than width",
        diagram_path="assets/deep_joint.png",
        formula="Volume (L) = Width (cm) × Depth (cm) × Length (m) × 100 ÷ 1000\nRecommended: Depth = Width × 2",
        notes="Requires backing rod. Add 10% for material settling. Length is in meters, width/depth in cm."
    ),
    "Wide Joint": JointProfile(
        name="Wide Joint",
        typical_width=2.0,
        typical_depth=1.0,
        description="Wide profile, width greater than depth",
        diagram_path="assets/wide_joint.png",
        formula="Volume (L) = Width (cm) × Depth (cm) × Length (m) × 100 ÷ 1000\nRecommended: Depth = Width ÷ 2",
        notes="May require multiple passes. Consider joint movement. Length is in meters, width/depth in cm."
    ),
    "V-Joint": JointProfile(
        name="V-Joint",
        typical_width=1.0,
        typical_depth=1.5,
        description="V-shaped profile, commonly used in corners",
        diagram_path="assets/v_joint.png",
        formula="Volume (L) = (Width (cm) × Depth (cm) × Length (m) × 100) ÷ 2000",
        notes="Use half of square joint volume due to triangular profile. Length is in meters, width/depth in cm."
    ),
    "U-Joint": JointProfile(
        name="U-Joint",
        typical_width=1.5,
        typical_depth=1.5,
        description="U-shaped profile, rounded bottom",
        diagram_path="assets/u_joint.png",
        formula="Volume (L) = (π × Width (cm) × Depth (cm) × Length (m) × 100) ÷ 4000",
        notes="Accounts for rounded bottom. Add 15% for curvature filling. Length is in meters, width/depth in cm."
    )
}

def get_joint_profile(profile_name: str) -> JointProfile:
    """Get joint profile by name."""
    return JOINT_PROFILES.get(profile_name, JOINT_PROFILES["Square Joint"])

class UnitConverter:
    @staticmethod
    def mm_to_cm(value: float) -> float:
        return value / 10

    @staticmethod
    def cm_to_mm(value: float) -> float:
        return value * 10

    @staticmethod
    def m_to_cm(value: float) -> float:
        return value * 100

    @staticmethod
    def cm_to_m(value: float) -> float:
        return value / 100

    @staticmethod
    def convert(value: float, from_unit: str, to_unit: str) -> float:
        """Convert between different units."""
        # Convert to cm first
        if from_unit == "mm":
            value = UnitConverter.mm_to_cm(value)
        elif from_unit == "m":
            value = UnitConverter.m_to_cm(value)
        
        # Convert from cm to target unit
        if to_unit == "mm":
            return UnitConverter.cm_to_mm(value)
        elif to_unit == "m":
            return UnitConverter.cm_to_m(value)
        return value  # cm

class JointValidator:
    MIN_DEPTH_MM = 6  # minimum 6mm depth
    MAX_DEPTH_MM = 12  # maximum 12mm depth
    MIN_WIDTH_MM = 6  # minimum 6mm width
    MAX_WIDTH_MM = 24  # maximum 24mm width
    
    @staticmethod
    def get_recommended_depth(width_mm: float) -> float:
        """Calculate recommended depth based on width (2:1 ratio)."""
        recommended = width_mm / 2
        return max(JointValidator.MIN_DEPTH_MM, 
                  min(recommended, JointValidator.MAX_DEPTH_MM))
    
    @staticmethod
    def validate_dimensions(width_mm: float, depth_mm: float) -> dict:
        """Validate joint dimensions and return status with messages."""
        status = {
            "is_valid": True,
            "warnings": [],
            "recommendations": []
        }
        
        # Check width limits
        if width_mm < JointValidator.MIN_WIDTH_MM:
            status["warnings"].append(f"Width ({width_mm}mm) is below minimum recommended width ({JointValidator.MIN_WIDTH_MM}mm)")
            status["is_valid"] = False
        elif width_mm > JointValidator.MAX_WIDTH_MM:
            status["warnings"].append(f"Width ({width_mm}mm) exceeds maximum recommended width ({JointValidator.MAX_WIDTH_MM}mm)")
            status["is_valid"] = False
            
        # Check depth limits
        if depth_mm < JointValidator.MIN_DEPTH_MM:
            status["warnings"].append(f"Depth ({depth_mm}mm) is below minimum recommended depth ({JointValidator.MIN_DEPTH_MM}mm)")
            status["is_valid"] = False
        elif depth_mm > JointValidator.MAX_DEPTH_MM:
            status["warnings"].append(f"Depth ({depth_mm}mm) exceeds maximum recommended depth ({JointValidator.MAX_DEPTH_MM}mm)")
            status["is_valid"] = False
            
        # Check width-to-depth ratio
        recommended_depth = JointValidator.get_recommended_depth(width_mm)
        ratio = width_mm / depth_mm if depth_mm > 0 else float('inf')
        
        if abs(depth_mm - recommended_depth) > 1:  # 1mm tolerance
            status["recommendations"].append(
                f"Recommended depth for {width_mm}mm width is {recommended_depth}mm (2:1 width-to-depth ratio)"
            )
            if ratio < 1.5:  # Too deep relative to width
                status["warnings"].append("Joint is too deep relative to width. This may cause adhesion failure.")
            elif ratio > 2.5:  # Too shallow relative to width
                status["warnings"].append("Joint is too shallow relative to width. This may affect movement capability.")
                
        return status
