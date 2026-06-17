import random
import time

WAFER_RADIUS = 150.0
LAYER_SPACING = 0.5

LAYER_DEFINITIONS = [
    {"layer_name": "硅衬底层", "thickness": 725.0, "material": "Silicon", "color": "#4A90D9"},
    {"layer_name": "氧化层", "thickness": 1.0, "material": "SiO2", "color": "#7EC8E3"},
    {"layer_name": "多晶硅层", "thickness": 0.5, "material": "Poly-Silicon", "color": "#A0A0A0"},
    {"layer_name": "金属互连层M1", "thickness": 1.2, "material": "Cu/Al", "color": "#D4AF37"},
    {"layer_name": "金属互连层M2", "thickness": 1.4, "material": "Cu/Al", "color": "#C5A028"},
    {"layer_name": "金属互连层M3", "thickness": 1.6, "material": "Cu/Al", "color": "#B8960F"},
    {"layer_name": "金属互连层M4", "thickness": 1.8, "material": "Cu/Al", "color": "#A07800"},
    {"layer_name": "钝化层", "thickness": 1.5, "material": "Si3N4", "color": "#50C878"},
]

DEFECT_TYPES = ["scratch", "particle", "crack", "void", "contamination"]
SEVERITY_LEVELS = ["low", "medium", "high"]

DEFECT_DESCRIPTIONS = {
    "scratch": "表面划伤，可能由机械接触导致",
    "particle": "颗粒污染物，可能来自工艺环境",
    "crack": "裂纹缺陷，可能由热应力导致",
    "void": "空洞缺陷，可能由沉积工艺异常导致",
    "contamination": "污染缺陷，可能由化学残留导致",
}


def generate_layers():
    layers = []
    for i, defn in enumerate(LAYER_DEFINITIONS):
        layers.append({
            "layer_id": i + 1,
            "layer_name": defn["layer_name"],
            "thickness": defn["thickness"],
            "material": defn["material"],
            "color": defn["color"],
        })
    return layers


def generate_defects(layers):
    random.seed(time.time())
    num_defects = random.randint(15, 25)
    defects = []
    cumulative_z = 0.0
    layer_z_positions = []
    for layer in layers:
        z_start = cumulative_z
        z_end = cumulative_z + layer["thickness"]
        layer_z_positions.append((z_start, z_end))
        cumulative_z = z_end + LAYER_SPACING

    for i in range(num_defects):
        layer = random.choice(layers)
        layer_id = layer["layer_id"]
        z_start, z_end = layer_z_positions[layer_id - 1]

        angle = random.uniform(0, 2 * 3.141592653589793)
        r = WAFER_RADIUS * random.uniform(0, 1) ** 0.5
        x = round(r * random.choice([-1, 1]) * abs(random.uniform(0, 1)) + r * (1 - abs(random.uniform(0, 1))) * (1 if random.random() > 0.5 else -1), 2)
        x = round(random.uniform(-WAFER_RADIUS, WAFER_RADIUS), 2)
        y_sq_max = WAFER_RADIUS ** 2 - x ** 2
        if y_sq_max < 0:
            y_sq_max = 0
        y_max = y_sq_max ** 0.5
        y = round(random.uniform(-y_max, y_max), 2)
        z = round(random.uniform(z_start, z_end), 2)

        defect_type = random.choice(DEFECT_TYPES)
        severity = random.choice(SEVERITY_LEVELS)

        defects.append({
            "defect_id": i + 1,
            "layer_id": layer_id,
            "x": x,
            "y": y,
            "z": z,
            "defect_type": defect_type,
            "severity": severity,
            "description": DEFECT_DESCRIPTIONS[defect_type],
        })

    return defects
