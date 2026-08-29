color_strings = [
    # Day 1      # Day 2      # Day 3
    "#F29191", "#E64343", "#CC0000",     # Dextrose
    "#F2C491", "#E69543", "#CC6E00",     # Galactose
    "#91F2A5", "#43E669", "#00CC33",     # Glycerol 
    "#91C8F2", "#43A0E6", "#007ACC",     # Acetate 
    "#D491F2", "#B443E6", "#8800CC",     # Synthetic	
]

# ENVIRONMENTS = ("Dextrose", "Galactose", "Glycerol", "Acetate", "Synthetic")
ENVIRONMENTS = ("YPD", "YPGal", "YPGly", "AS", "SD")
ENV_TO_COLOR = dict(zip(ENVIRONMENTS, color_strings[2::3]))

def hex_to_rgb(hex_str):
    """Converts a hex string (e.g., '#F29191') to an RGB list of integers."""
    hex_str = hex_str.lstrip('#')
    return [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]

rgb_pool = [hex_to_rgb(c) for c in color_strings]

LABEL_TO_COLOR = {
    'YPD_D1' :     rgb_pool[0],
    'YPD_D2' :     rgb_pool[1],
    'YPD_D3' :     rgb_pool[2],
    'YPGal_D1' :   rgb_pool[3],
    'YPGal_D2' :   rgb_pool[4],
    'YPGal_D3' :   rgb_pool[5],
    'YPGly_D1' :   rgb_pool[6],
    'YPGly_D2' :   rgb_pool[7],
    'YPGly_D3' :   rgb_pool[8],
    'AS_D1' : rgb_pool[9],
    'AS_D2' : rgb_pool[10],
    'AS_D3' : rgb_pool[11],
    'SD_D1' :      rgb_pool[12],
    'SD_D2' :      rgb_pool[13],
    'SD_D3' :      rgb_pool[14],
}

