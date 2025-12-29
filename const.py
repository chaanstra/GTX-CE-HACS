DOMAIN = "greenthinx_ce"
DEFAULT_SCAN_INTERVAL = 300

API_BASE_URL = "https://greenthinx.nl/ce/api/latest.php"

SOIL_PROFILES = {
    "clay": {"min": 65, "max": 105, "capacity": 17},
    "light clay": {"min": 65, "max": 97, "capacity": 18},
    "silty clay": {"min": 65, "max": 98, "capacity": 18},
    "silty loam": {"min": 20, "max": 50, "capacity": 20},
    "sandy loam": {"min": 30, "max": 60, "capacity": 14},
    "loamy sand": {"min": 20, "max": 50, "capacity": 10},
    "sand": {"min": 10, "max": 40, "capacity": 4},
    "silty clay (topsoil)": {"min": 50, "max": 80, "capacity": 18},
    "silty clay (subsoil)": {"min": 50, "max": 75, "capacity": 18},
    "heavy clay": {"min": 45, "max": 98, "capacity": 14},
    "potting soil": {"min": 30, "max": 105, "capacity": 10},
}