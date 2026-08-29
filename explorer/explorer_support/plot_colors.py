import numpy as np
import matplotlib.pyplot as plt

from .colors import color_strings, hex_to_rgb

colors = np.array(color_strings).reshape(5, 3)

rgb = np.array([
    [hex_to_rgb(c) for c in row]
    for row in colors
])

plt.rcParams.update({
    "font.size": 16,
})

fig, ax = plt.subplots(figsize=(8, 8))

ax.imshow(rgb, interpolation="nearest", aspect="equal")

ax.xaxis.tick_top()
ax.xaxis.set_label_position("top")
ax.set_xticks(range(3))
ax.set_xticklabels(["Day 1", "Day 2", "Day 3"])

ax.set_yticks(range(5))
ax.set_yticklabels(["Dextrose", "Galactose", "Glycerol", "Acetate", "Synthetic"])

# Right-side letters
for y, letter in enumerate(["d", "l", "y", "a", "s"]):
    ax.text(
        2.7, y, letter,
        va="center", ha="left",
        clip_on=False
    )

plt.tight_layout()
plt.savefig("color_matrix.pdf")
plt.show()
