"""Constants for the HDBaseT Matrix integration."""

DOMAIN = "hdbaset_matrix"

CONF_INPUTS = "inputs"
CONF_OUTPUTS = "outputs"
CONF_SCAN_INTERVAL = "scan_interval"

NUM_PORTS = 4
DEFAULT_NAME = "HDBaseT Matrix"
DEFAULT_SCAN_INTERVAL = 10
DEFAULT_INPUTS = ["Apple TV", "Computer", "Apple TV 2", "NVR"]
DEFAULT_OUTPUTS = ["Loft", "Living Room", "Office", "Basement"]

EDID_OPTIONS = {
    **{f"EDIDD{i}": f"Default EDID {i}" for i in range(1, 13)},
    "EDIDD1": "Default EDID 1 (1080p)",
    "EDIDD10": "Default EDID 10 (4K)",
    **{f"EDIDU{i}": f"User EDID {i}" for i in range(1, 4)},
    **{f"EDIDO{i}": f"Copy from output {i}" for i in range(1, 5)},
}
