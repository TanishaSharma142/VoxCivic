# config/wards.py
"""
Single source of truth for ward and department reference data.
Both the intake agent and the Streamlit submission form import from here,
so a citizen's manual selection and the AI's extraction are validated
against the exact same list.
"""

WARDS = [
    "Ward 1",
    "Ward 2",
    "Ward 3",
    "Ward 4",
    "Ward 5",
    "Ward 6",
    "Ward 7",
    "Ward 8",
]

DEPARTMENTS = [
    "Roads & Infrastructure",
    "Sanitation & Waste",
    "Water Supply & Sewage",
    "Electrical / Streetlights",
    "Drainage & Flood Control",
    "Public Safety",
]

CATEGORY_TO_DEPARTMENT = {
    "pothole": "Roads & Infrastructure",
    "road_damage": "Roads & Infrastructure",
    "garbage": "Sanitation & Waste",
    "water_leakage": "Water Supply & Sewage",
    "streetlight": "Electrical / Streetlights",
    "flooding": "Drainage & Flood Control",
    "public_safety": "Public Safety",
    "other": "Roads & Infrastructure",  # default routing; officer can reassign
}