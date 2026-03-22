# ============================================================
# 1. IMPORTS
# ============================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import cachai.chplot as chp
import cachai.data as chd
import cachai.utilities as chu
# ============================================================
# 2. LOAD DATA (this is the ONLY separate file)
# ============================================================

# Replace 'your_data.csv' with your file name.
# Your data file MUST be in the same folder as your notebook.

df = pd.read_csv("your_data.csv")

# If Excel, use:
# df = pd.read_excel("your_data.xlsx")

df.head()
# ============================================================
# 3. COMPUTE CORRELATION MATRIX
# ============================================================

corr_matrix = df.corr(numeric_only=True)

corr_matrix

# ============================================================
# 4. BASIC CHORD DIAGRAM
# ============================================================
plt.figure(figsize=(7,7))
chp.chord(corr_matrix)
plt.show()

# ============================================================
# 5. CHORD DIAGRAM WITH LEGEND + THRESHOLD 
# ============================================================
plt.figure(figsize=(6,6), facecolor='w')

chp.chord(
    corr_matrix,
    threshold=0.3,           # Ignore correlations smaller than 0.3
    negative_hatch='///',    # Pattern for negative correlations
    legend=True,
    rasterized=True
)

plt.legend(
    loc='center',
    bbox_to_anchor=[0.5, 0],
    ncols=2,
    fontsize=13,
    handletextpad=0
)

plt.show()

# ============================================================
# 6. COMPARING LINEAR VS LOG CORRELATION THICKNESS
# ============================================================
fig, ax = plt.subplots(1, 2, figsize=(12,6), facecolor='w')

# Linear scale
chp.chord(
    corr_matrix,
    ax=ax[0],
    threshold=0.4,
    scale='linear',
    rasterized=True
)
ax[0].set_title("Linear scale", fontsize=20, pad=0)

# Log scale
chp.chord(
    corr_matrix,
    ax=ax[1],
    threshold=0.4,
    scale='log',
    rasterized=True
)
ax[1].set_title("Logarithmic scale", fontsize=20, pad=0)

plt.subplots_adjust(wspace=0)
plt.show()
# ============================================================
# 7. CUSTOMIZED CHORD DIAGRAMS — 3 VERSIONS
# ============================================================
# Optional colors — safe even if your dataset changes
colors = plt.cm.tab20(np.linspace(0, 1, len(corr_matrix.columns)))
names = corr_matrix.columns

fig, ax = plt.subplots(1, 3, figsize=(20, 7), facecolor='w')

# ------------------------------------------------------------
# EXAMPLE 1 — BASIC CLEAN VERSION
# ------------------------------------------------------------
chp.chord(corr_matrix, ax=ax[0], rasterized=True)
ax[0].set_title("Basic", fontsize=18)


# ------------------------------------------------------------
# EXAMPLE 2 — FONT, HATCHING, NODE GAP, HIGHLIGHTING
# ------------------------------------------------------------
chord_plot = chp.chord(
    corr_matrix,
    colors=colors,
    ax=ax[1],
    threshold=0.25,
    node_gap=0.02,
    negative_hatch='oo',
    font={'family':'serif','size':17},
    rasterized=True
)

# Highlight correlation at index (3,3)
chord_plot.highlight_chord(3, 3)

# Make nodes 3 and 4 bold
for n in [3, 4]:
    chord_plot.node_labels[n].set_font({'size':25,'weight':'bold','family':'serif'})
    chord_plot.node_labels[n].set_pad(0.3)
    chord_plot.node_patches[n].set_linewidth(35)

ax[1].set_title("Customized + Highlight", fontsize=18)

# ------------------------------------------------------------
# EXAMPLE 3 — FILTER WEAK LINKS + LOG SCALE + THICK LINES
# ------------------------------------------------------------
chp.chord(
    corr_matrix,
    colors=colors,
    ax=ax[2],
    blend=False,
    threshold=0.4,
    max_rho_radius=0.5,
    scale='log',
    node_linewidth=20,
    chord_linewidth=1.5,
    node_labelpad=0.3,
    fontsize=20,
    show_axis=False,
    legend=True,
    rasterized=True
)

ax[2].legend(loc='center', bbox_to_anchor=[0.5,1], ncols=2, fontsize=17)
ax[2].set_title("Strong Correlations Only", fontsize=18)

plt.subplots_adjust(wspace=0)
plt.show()

