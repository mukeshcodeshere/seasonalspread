# dash_styles.py

# This file contains common styling definitions for Dash applications to ensure visual uniformity.

# --- External Stylesheets ---
# Using a common Bootstrap theme for consistent component styling.
# Switched to a more modern Bootstrap theme (flatly) and added Google Fonts.
EXTERNAL_STYLESHEETS = [
    'https://cdn.jsdelivr.net/npm/bootswatch@5.1.3/dist/flatly/bootstrap.min.css',
    'https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap'
]

# --- Custom CSS for the main HTML index string ---
# This CSS will be injected directly into the <head> of the HTML document.
# It defines global styles for body, containers, titles, buttons, and form elements.
INDEX_STRING_CUSTOM_CSS = '''
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    :root {
        --primary-color: #007bff;
        --secondary-color: #6c757d;
        --accent-color: #28a745;
        --background-light: #f8f9fa;
        --background-dark: #e9ecef;
        --text-dark: #343a40;
        --text-light: #ffffff;
        --card-bg: #ffffff;
        --border-color: #dee2e6;
        --shadow-light: rgba(0, 0, 0, 0.08);
        --shadow-medium: rgba(0, 0, 0, 0.15);
    }

    body {
        background: var(--background-light);
        font-family: 'Poppins', sans-serif;
        color: var(--text-dark);
        line-height: 1.6;
    }
    .container {
        max-width: 960px;
        margin: 60px auto;
        padding: 40px;
        background-color: var(--card-bg);
        border-radius: 20px;
        box-shadow: 0 15px 40px var(--shadow-light);
        text-align: center;
    }
    .title {
        color: var(--primary-color);
        font-size: 3em;
        margin-bottom: 25px;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .radio-group {
        margin-top: 35px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 20px;
    }
    .button-link {
        display: inline-block;
        padding: 15px 35px;
        background-color: var(--accent-color);
        color: var(--text-light);
        text-decoration: none;
        border-radius: 10px;
        font-size: 1.2em;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 8px 20px rgba(40, 167, 69, 0.25);
        min-width: 280px;
        text-align: center;
        position: relative; /* For icon alignment */
    }
    .button-link:hover {
        background-color: #218838; /* A darker shade of accent-color */
        transform: translateY(-3px);
        color: var(--text-light);
        box-shadow: 0 12px 25px rgba(40, 167, 69, 0.4);
    }
    .button-link + .button-link {
        margin-top: 20px;
    }
    .status-message {
        margin-top: 30px;
        padding: 20px;
        border-radius: 10px;
        background-color: var(--background-dark);
        color: var(--text-dark);
        font-size: 1.1em;
        border: 1px solid var(--border-color);
        box-shadow: 0 4px 15px var(--shadow-light);
    }
    /* General Card Styling */
    .card {
        border-radius: 15px !important;
        box-shadow: 0 8px 20px var(--shadow-light) !important;
        border: none !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 25px var(--shadow-medium) !important;
    }
    /* Form Control Styling */
    .form-control, .form-select, .rc-slider {
        border-radius: 10px !important;
        border: 1px solid var(--border-color) !important;
        transition: all 0.3s ease !important;
        padding: 10px 15px !important;
    }
    .form-control:focus, .form-select:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 0.25rem rgba(0, 123, 255, 0.2) !important;
        background-color: #f0f8ff; /* Light blue on focus */
    }
    /* Button Styling */
    .btn {
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
    }
    .btn:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px var(--shadow-light);
    }
    .btn-primary {
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }
    .btn-primary:hover {
        background-color: #0056b3 !important;
        border-color: #0056b3 !important;
    }
    .btn-success {
        background-color: var(--accent-color) !important;
        border-color: var(--accent-color) !important;
    }
    .btn-success:hover {
        background-color: #218838 !important;
        border-color: #218838 !important;
    }

    /* Dropdown Styling */
    .Select-control {
        border-radius: 10px !important;
        border: 1px solid var(--border-color) !important;
        box-shadow: none !important;
        transition: all 0.3s ease !important;
    }
    .Select-control:hover {
        border-color: var(--primary-color) !important;
    }
    .Select-value-label {
        color: var(--text-dark) !important;
        font-weight: 400;
    }
    .Select-menu-outer {
        border-radius: 10px !important;
        box-shadow: 0 8px 20px var(--shadow-light) !important;
        border: 1px solid var(--border-color) !important;
    }
    .Select-option.is-focused {
        background-color: var(--primary-color) !important;
        color: var(--text-light) !important;
    }
    .Select-option.is-selected {
        background-color: #0056b3 !important; /* Darker primary */
        color: var(--text-light) !important;
    }

    /* Plotly Graph Styling */
    .main-svg, .plotly-notifier {
        border-radius: 15px !important;
        box-shadow: 0 8px 20px var(--shadow-light) !important;
        overflow: hidden; /* Ensures borders apply to content */
    }
    .js-plotly-plot .plotly .modebar {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 0 0 15px 15px !important;
        padding: 8px !important;
        box-shadow: 0 -2px 10px var(--shadow-light);
    }
    .js-plotly-plot .plotly .modebar-btn {
        color: var(--secondary-color) !important;
        transition: all 0.2s ease;
    }
    .js-plotly-plot .plotly .modebar-btn:hover {
        color: var(--primary-color) !important;
        background-color: rgba(0, 123, 255, 0.1) !important;
        border-radius: 5px;
    }

    /* Fix for active tab background and text color */
    .nav-pills .nav-link.active, .nav-pills .show > .nav-link {
        background-color: var(--primary-color) !important; /* Or any other desired color, e.g., #007bff */
        color: var(--text-light) !important; /* e.g., white */
    }

    /* Ensure tab text is visible even if not active */
    .nav-pills .nav-link {
        color: var(--primary-color); /* Color for inactive tabs, adjust as needed */
        background-color: var(--background-dark); /* Light background for inactive tabs */
        border: 1px solid var(--border-color);
        margin-right: 5px; /* Spacing between tabs */
        border-radius: 8px; /* Slightly rounded corners for tabs */
    }

    .nav-pills .nav-link:hover {
        background-color: rgba(0, 123, 255, 0.1); /* Light hover effect */
        color: var(--primary-color);
    }

    /* DataTable Styling */
    .dash-spreadsheet-container .dash-spreadsheet-inner table {
        border-collapse: separate; /* Use separate to allow border-radius on rows */
        border-spacing: 0;
        width: 100%;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 20px var(--shadow-light);
    }
    .dash-spreadsheet-container .dash-header-row {
        background-color: var(--primary-color);
        color: var(--text-light);
        font-weight: 600;
    }
    .dash-spreadsheet-container .dash-header-row .dash-header {
        padding: 12px 18px;
        text-align: left;
        border-bottom: none; /* Remove default border */
    }
    .dash-spreadsheet-container .dash-cell {
        background-color: var(--card-bg);
        color: var(--text-dark);
        border-bottom: 1px solid var(--border-color);
        padding: 10px 18px;
        font-size: 0.95em;
    }
    .dash-spreadsheet-container .dash-cell-value {
        text-align: left;
    }
    /* Remove last row border for better visual appeal */
    .dash-spreadsheet-container tbody tr:last-child .dash-cell {
        border-bottom: none;
    }
    .dash-table-container .dash-table-inner {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 20px var(--shadow-light);
    }
</style>
'''

# --- Common Layout Components and Styles ---
# These can be used directly in layouts or as arguments for component styling.

# Card header background colors for different sections
CARD_HEADER_COLORS = {
    "primary": "bg-primary text-white",
    "info": "bg-info text-white",
    "success": "bg-success text-white",
    "light": "bg-light text-dark",
    "dark": "bg-dark text-white" # Added a dark option
}

# Common margin and padding classes for containers and cards
CONTAINER_FLUID_CLASSES = "px-5 py-5 bg-light min-vh-100" # Increased padding
CARD_COMMON_CLASSES = "mb-5 shadow-lg border-0" # Used larger shadow
CARD_BORDER_RADIUS = {'borderRadius': '15px'} # Increased border-radius

# Common styles for dropdowns and inputs
DROPDOWN_INPUT_STYLE = {'borderRadius': '10px', 'minHeight': '45px'} # Increased border-radius and min-height
SHADOW_SM_CLASS = "shadow" # Using a slightly larger shadow for general elements

# Plotly Graph Configuration
PLOTLY_GRAPH_CONFIG = {
    'displayModeBar': True,
    'displaylogo': False,
    # Kept only essential buttons for cleaner interface
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'zoom2d', 'select2d', 'zoomIn2d', 'zoomOut2d', 'autoscale', 'resetScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']
}

# Plotly Graph Layout Templates
PLOTLY_TEMPLATE_LIGHT = "plotly_white"
PLOTLY_TEMPLATE_DARK = "plotly_dark" # Keep dark for potential theme switching

# Common margin for graphs (adjusted for more breathing room)
GRAPH_MARGIN = dict(l=60, r=60, t=90, b=60)

# Common classes for graph containers
GRAPH_CONTAINER_CLASSES = "shadow border rounded-lg p-3" # Added padding and rounded-lg for consistency

# Text alignment classes
TEXT_CENTER_CLASS = "text-center"
TEXT_PRIMARY_CLASS = "text-primary"
TEXT_SECONDARY_CLASS = "text-secondary" # Added secondary text class
TEXT_MUTED_CLASS = "text-muted"
FW_BOLD_CLASS = "fw-bold"
FS_4_CLASS = "fs-4" # Adjusted font size for better hierarchy
DISPLAY_5_CLASS = "display-5" # Adjusted display class
LEAD_CLASS = "lead"

# Utility classes (adjusted margins/paddings for more spacing)
ME_3_CLASS = "me-3" # margin-end (right)
MB_1_CLASS = "mb-1" # margin-bottom (finer control)
MB_2_CLASS = "mb-2"
MB_3_CLASS = "mb-3"
MB_4_CLASS = "mb-4"
MB_5_CLASS = "mb-5"
PY_3_CLASS = "py-3" # padding-y
PY_4_CLASS = "py-4"
PY_5_CLASS = "py-5"
W_100_CLASS = "w-100" # width 100%
D_FLEX_CLASS = "d-flex" # display flex
ALIGN_ITEMS_CENTER_CLASS = "align-items-center"
JUSTIFY_CONTENT_CENTER_CLASS = "justify-content-center"
MS_3_CLASS = "ms-3" # margin-start (left)
PB_3_CLASS = "pb-3" # padding-bottom
MT_4_CLASS = "mt-4" # margin-top

# DataTable Styles
DATATABLE_STYLE_TABLE = {'overflowX': 'auto', 'borderRadius': '15px', 'boxShadow': '0 8px 20px rgba(0, 0, 0, 0.08)'}
DATATABLE_STYLE_CELL = {
    'backgroundColor': '#ffffff', # White background for cells
    'color': '#343a40', # Darker text for readability
    'textAlign': 'left',
    'fontSize': 14, # Slightly larger font size
    'padding': '12px 18px', # More padding
    'borderBottom': '1px solid #e0e6ed' # Softer border
}
DATATABLE_STYLE_HEADER = {
    'backgroundColor': '#007bff', # Primary color for header
    'color': 'white',
    'fontWeight': '600', # Semi-bold
    'padding': '14px 18px', # More padding
    'borderBottom': 'none' # No border below header
}
DATATABLE_STYLE_HEADER_CELL = {
    'textAlign': 'left'
}