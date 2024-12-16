from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path
from knowledge_framework.documentation.doc_manager import DocumentationManager

@dataclass
class JointProfile:
    name: str
    typical_width: float
    typical_depth: float
    description: str
    diagram_path: str
    formula: str
    notes: str = ""
    
    @staticmethod
    def get_specifications() -> str:
        """Get detailed joint specifications from documentation."""
        doc_manager = DocumentationManager(Path(__file__).parent.parent)
        return doc_manager.get_joint_specifications()

# Define common joint profiles
JOINT_PROFILES = {
    "Square Joint": JointProfile(
        name="Square Joint",
        typical_width=12.0,
        typical_depth=6.0,  # Following 2:1 ratio
        description="Standard square profile, width twice the depth (2:1 ratio)",
        diagram_path="assets/square_joint.png",
        formula="Volume (L) = Width (cm) × Depth (cm) × Length (m) × 100 ÷ 1000",
        notes="Most common profile. Use backing rod if depth > 10mm. Ideal width-to-depth ratio is 2:1."
    ),
    "Deep Joint": JointProfile(
        name="Deep Joint",
        typical_width=20.0,
        typical_depth=20.0,  # Equal width and depth (1:1 ratio)
        description="Deep profile, equal width and depth (1:1 ratio)",
        diagram_path="assets/deep_joint.png",
        formula="Volume (L) = Width (cm) × Depth (cm) × Length (m) × 100 ÷ 1000",
        notes="Requires backing rod. Ideal for joints with limited width but requiring good depth."
    ),
    "Wide Joint": JointProfile(
        name="Wide Joint",
        typical_width=30.0,
        typical_depth=12.0,  # Following 2:1 ratio
        description="Wide profile, width twice the depth (2:1 ratio)",
        diagram_path="assets/wide_joint.png",
        formula="Volume (L) = Width (cm) × Depth (cm) × Length (m) × 100 ÷ 1000",
        notes="May require multiple passes. Depth should not exceed half the width for proper adhesion."
    ),
    "V-Joint": JointProfile(
        name="V-Joint",
        typical_width=15.0,
        typical_depth=10.0,  # Following 1.5:1 ratio
        description="V-shaped profile for corner applications (1.5:1 ratio)",
        diagram_path="assets/v_joint.png",
        formula="Volume (L) = Width (cm) × Depth (cm) × Length (m) × 100 ÷ 2000",  # Half volume due to triangular profile
        notes="Ideal for corner applications. Volume is half of square joint due to triangular profile."
    ),
    "U-Joint": JointProfile(
        name="U-Joint",
        typical_width=15.0,
        typical_depth=10.0,  # Following 1.5:1 ratio
        description="U-shaped profile for enhanced movement (1.5:1 ratio)",
        diagram_path="assets/u_joint.png",
        formula="Volume (L) = Width (cm) × Depth (cm) × Length (m) × 100 ÷ 1000",
        notes="Suitable for expansion joints. Requires special tooling for U-shape formation."
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
    # Common limits
    MIN_DEPTH_MM = 6
    MAX_DEPTH_MM = 12
    MIN_WIDTH_MM = 6
    MAX_WIDTH_MM = 24

    # Profile-specific ratios and limits
    PROFILE_SPECS = {
        "Square Joint": {
            "width_to_depth_ratio": 2.0,  # Standard 2:1 ratio
            "min_width_mm": 6,
            "max_width_mm": 24,
            "min_depth_mm": 6,
            "max_depth_mm": 12,
            "ratio_tolerance": 0.2  # 20% tolerance
        },
        "Deep Joint": {
            "width_to_depth_ratio": 1.0,  # 1:1 ratio for deep joints
            "min_width_mm": 6,
            "max_width_mm": 12,
            "min_depth_mm": 6,
            "max_depth_mm": 12,
            "ratio_tolerance": 0.2
        },
        "Wide Joint": {
            "width_to_depth_ratio": 2.0,  # 2:1 ratio (width:depth)
            "min_width_mm": 25,
            "max_width_mm": 50,
            "min_depth_mm": 6,
            "max_depth_mm": 12,
            "ratio_tolerance": 0.3  # More tolerance for wide joints
        },
        "V-Joint": {
            "width_to_depth_ratio": 1.5,  # 1.5:1 ratio for angular joints
            "min_width_mm": 6,
            "max_width_mm": 20,
            "min_depth_mm": 6,
            "max_depth_mm": 12,
            "ratio_tolerance": 0.25,
            "volume_factor": 0.5  # Half volume due to triangular profile
        },
        "U-Joint": {
            "width_to_depth_ratio": 1.5,  # 1.5:1 ratio for curved joints
            "min_width_mm": 8,
            "max_width_mm": 24,
            "min_depth_mm": 8,
            "max_depth_mm": 15,
            "ratio_tolerance": 0.25,
            "curved_profile": True  # Indicates special volume consideration
        }
    }
    
    @staticmethod
    def get_profile_specs(profile_name: str) -> dict:
        """Get specifications for a specific joint profile."""
        return JointValidator.PROFILE_SPECS.get(profile_name, JointValidator.PROFILE_SPECS["Square Joint"])
    
    @staticmethod
    def get_recommended_depth(width_mm: float, profile_name: str) -> float:
        """Calculate recommended depth based on width and profile type."""
        specs = JointValidator.get_profile_specs(profile_name)
        recommended = width_mm / specs["width_to_depth_ratio"]
        return max(specs["min_depth_mm"], 
                  min(recommended, specs["max_depth_mm"]))
    
    @staticmethod
    def get_recommended_dimensions(width_mm: float = None, depth_mm: float = None, profile_name: str = "Square Joint") -> dict:
        """Get recommended dimensions based on either width or depth."""
        specs = JointValidator.get_profile_specs(profile_name)
        result = {
            "recommended_width": None,
            "recommended_depth": None,
            "based_on": None
        }
        
        if width_mm is not None:
            # Calculate depth based on width
            recommended_depth = width_mm / specs["width_to_depth_ratio"]
            recommended_depth = max(specs["min_depth_mm"], 
                                 min(recommended_depth, specs["max_depth_mm"]))
            result.update({
                "recommended_depth": recommended_depth,
                "based_on": "width"
            })
        
        if depth_mm is not None:
            # Calculate width based on depth
            recommended_width = depth_mm * specs["width_to_depth_ratio"]
            recommended_width = max(specs["min_width_mm"], 
                                 min(recommended_width, specs["max_width_mm"]))
            result.update({
                "recommended_width": recommended_width,
                "based_on": "depth"
            })
            
        return result
    
    @staticmethod
    def validate_dimensions(width_mm: float, depth_mm: float, profile_name: str, unit: str = "mm") -> dict:
        """Validate joint dimensions based on profile type."""
        specs = JointValidator.get_profile_specs(profile_name)
        warnings = []
        recommendations = []
        
        # Convert min/max values if unit is cm
        unit_converter = lambda x: x/10 if unit == "cm" else x
        
        min_width = unit_converter(specs["min_width_mm"])
        max_width = unit_converter(specs["max_width_mm"])
        min_depth = unit_converter(specs["min_depth_mm"])
        max_depth = unit_converter(specs["max_depth_mm"])
        
        # Convert input values for comparison
        width = width_mm
        depth = depth_mm
        if unit == "cm":
            width = UnitConverter.mm_to_cm(width_mm)
            depth = UnitConverter.mm_to_cm(depth_mm)

        if width < min_width:
            warnings.append(f"Width ({width:.1f}{unit}) is below minimum recommended width ({min_width:.1f}{unit}) for {profile_name}")
        elif width > max_width:
            warnings.append(f"Width ({width:.1f}{unit}) exceeds maximum recommended width ({max_width:.1f}{unit}) for {profile_name}")

        if depth < min_depth:
            warnings.append(f"Depth ({depth:.1f}{unit}) is below minimum recommended depth ({min_depth:.1f}{unit}) for {profile_name}")
        elif depth > max_depth:
            warnings.append(f"Depth ({depth:.1f}{unit}) exceeds maximum recommended depth ({max_depth:.1f}{unit}) for {profile_name}")

        # Check width-to-depth ratio
        actual_ratio = width / depth if depth != 0 else float('inf')
        target_ratio = specs["width_to_depth_ratio"]
        tolerance = specs.get("ratio_tolerance", 0.5)
        
        # For Wide Joint, we mainly care if depth is greater than width
        if profile_name == "Wide Joint":
            if depth > width:
                warnings.append(f"Depth should not exceed width for {profile_name}. This may cause adhesion failure.")
        else:
            # For other profiles, check the specific ratio requirements
            if abs(actual_ratio - target_ratio) > tolerance:
                if actual_ratio > target_ratio + tolerance:
                    warnings.append(f"Joint is too shallow for {profile_name}. This may affect movement capability.")
                elif actual_ratio < target_ratio - tolerance:
                    warnings.append(f"Joint is too deep for {profile_name}. This may cause adhesion failure.")

        # Add recommendation for ideal ratio
        if width > 0:
            ideal_depth = width / specs["width_to_depth_ratio"]
            recommendations.append(f"For {profile_name}, recommended depth for {width:.1f}{unit} width is {ideal_depth:.1f}{unit} ({specs['width_to_depth_ratio']:.1f}:1 width-to-depth ratio)")

        return {
            "is_valid": len(warnings) == 0,
            "warnings": warnings,
            "recommendations": recommendations
        }
