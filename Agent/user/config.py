"""
Materials Science Dashboard Configuration
"""

# Application configuration
APP_CONFIG = {
    "title": "Materials Science Interactive Dashboard",
    "version": "1.0.0",
    "author": "Materials Science Research Team",
    "description": "Professional UI for copper alloy performance prediction and analysis",
    "theme": {
        "primary_color": "#1a56db",
        "secondary_color": "#0c418d",
        "accent_color": "#2563eb",
        "success_color": "#10b981",
        "warning_color": "#f59e0b",
        "error_color": "#ef4444",
        "background_color": "#f9fafb",
        "card_bg": "#ffffff",
        "text_primary": "#1f2937",
        "text_secondary": "#6b7280"
    }
}

# Materials science domain configuration
MATERIALS_CONFIG = {
    "alloy_systems": ["Cu-Al-Mg", "Cu-Zn-Sn", "Cu-Ni-Si"],
    "performance_metrics": [
        {"name": "Hardness/HV", "unit": "HV", "description": "Vickers Hardness Number"},
        {"name": "EC/%IACS", "unit": "%IACS", "description": "Electrical Conductivity (International Annealed Copper Standard)"},
        {"name": "Q3-Euclidean", "unit": "", "description": "Comprehensive Performance Score"}
    ],
    "process_parameters": [
        {"name": "Solution_Temp_C", "unit": "°C", "description": "Solution Treatment Temperature"},
        {"name": "Aging_Temp_C", "unit": "°C", "description": "Aging Temperature"},
        {"name": "Aging_Time_h", "unit": "h", "description": "Aging Time"},
        {"name": "Quench_Rate_C_s", "unit": "°C/s", "description": "Quenching Rate"}
    ],
    "composition_elements": [
        {"symbol": "Cu", "name": "Copper", "unit": "wt.%", "range": [70.0, 95.0]},
        {"symbol": "Al", "name": "Aluminum", "unit": "wt.%", "range": [0.0, 15.0]},
        {"symbol": "Mg", "name": "Magnesium", "unit": "wt.%", "range": [0.0, 10.0]},
        {"symbol": "Zn", "name": "Zinc", "unit": "wt.%", "range": [0.0, 10.0]},
        {"symbol": "Sn", "name": "Tin", "unit": "wt.%", "range": [0.0, 5.0]}
    ]
}

# Visualization configuration
VISUALIZATION_CONFIG = {
    "default_color_scale": "Viridis",
    "heatmap_color_scale": "RdBu_r",
    "phase_diagram_color_scale": "Plasma",
    "max_data_points": 1000,
    "sample_size": 100
}

# API configuration (for future integration with backend)
API_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "retry_attempts": 3
}
