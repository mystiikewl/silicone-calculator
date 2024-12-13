from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class JointProfile:
    name: str
    typical_width: float
    typical_depth: float
    description: str
    diagram_path: str

# Define common joint profiles
JOINT_PROFILES = {
    "Square Joint": JointProfile(
        name="Square Joint",
        typical_width=1.0,
        typical_depth=1.0,
        description="Standard square profile, equal width and depth",
        diagram_path="assets/square_joint.png"
    ),
    "Deep Joint": JointProfile(
        name="Deep Joint",
        typical_width=1.0,
        typical_depth=2.0,
        description="Deep profile, depth greater than width",
        diagram_path="assets/deep_joint.png"
    ),
    "Wide Joint": JointProfile(
        name="Wide Joint",
        typical_width=2.0,
        typical_depth=1.0,
        description="Wide profile, width greater than depth",
        diagram_path="assets/wide_joint.png"
    ),
    "V-Joint": JointProfile(
        name="V-Joint",
        typical_width=1.0,
        typical_depth=1.5,
        description="V-shaped profile, commonly used in corners",
        diagram_path="assets/v_joint.png"
    ),
    "U-Joint": JointProfile(
        name="U-Joint",
        typical_width=1.5,
        typical_depth=1.5,
        description="U-shaped profile, rounded bottom",
        diagram_path="assets/u_joint.png"
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
