import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np

# ตั้งค่าหน้าจอแนวตั้ง
st.set_page_config(page_title="Beam Detailer", layout="centered")

st.title("🏗️ Beam Rebar Calculator")
st.write("ACI 318-19 (ksc unit)")

# ==========================================
# 1. [INPUT SECTION - แบ่งหมวดหมู่]
# ==========================================
with st.sidebar:
    st.header("⚙️ Geometry & Material")
    fc_prime = st.number_input("f'c (ksc)", value=280)
    fy = st.number_input("Fy (ksc)", value=4000)
    span_cc = st.number_input("Span C/C (m)", value=6.40)
    col_l = st.number_input("Left Col Width (m)", value=0.40)
    col_r = st.number_input("Right Col Width (m)", value=0.50)
    beam_h = st.number_input("Beam Height (m)", value=0.60)

    st.divider()
    st.header("🟦 Main Rebars (MT/MB)")
    db_main = st.selectbox("Size (mm)", [12, 16, 20, 25, 28], index=2)
    qty_mt = st.number_input("Qty Main Top (MT)", value=2)
    qty_mb = st.number_input("Qty Main Bot (MB)", value=2)

    st.divider()
    st.header("🟪 Extra Rebars (ET/EB)")
    db_extra = st.selectbox("Extra Size (mm)", [12, 16, 20, 25, 28], index=2)
    qty_et = st.number_input("Qty Extra Top (ET)", value=2)
    qty_eb = st.number_input("Qty Extra Bot (EB)", value=2)

# ==========================================
# 2. [CALCULATION LOGIC]
# ==========================================
db_m = db_main / 1000
db_e_m = db_extra / 1000

# ACI 318-19 Ld & Ldh
sqrt_fc = min(np.sqrt(fc_prime), 26.2)
psi_s = 0.8 if db_main <= 19 else 1.0
ld_m = (fy * 1.0 * 1.0 * 1.0 * psi_s) / (5.3 * 1.0 * sqrt_fc) * db_m
ld_m = max(ld_m, 0.30)

fc_psi = fc_prime * 14.223
psi_c = (fc_psi / 15000) + 0.6 if fc_psi < 6000 else 1.0
ldh_in = (fy * 14.223 * 1.0 * 1.0 * 1.0 * psi_c) / (50 * 1.0 * min(np.sqrt(fc_psi), 100)) * ((db_main/25.4)**1.5)
ldh_m = max(ldh_in * 0.0254, 8 * db_m, 0.15)

# Coordinates & Dimensions
x_f_l = col_l / 2
x_f_r = span_cc - col_r / 2
ln = x_f_r - x_f_l

et_start = x_f_r - (ln * 0.25 + 15 * db_e_m)
et_end = (span_cc + col_r/2) + (ln * 0.25 + 15 * db_e_m)
eb_start = x_f_l + (ln * 0.25) - (20 * db_e_m)
eb_end = x_f_r - (ln * 0.25) + (20 * db_e_m)

# ==========================================
# 3. [DRAWING FUNCTION]
# ==========================================
def draw_app():
    fig = plt.figure(figsize=(10, 16))
    gs = gridspec.GridSpec(4, 1, height_ratios=[1.2, 0.4, 0.8, 0.25], hspace=0.4)

    # --- 1. Longitudinal Section ---
    ax0 = fig.add_subplot(gs[0])
    # Column/Grid
    ax0.axvline(0, color='gray', ls='-.', alpha=0.5)
    ax0.axvline(span_cc, color='gray', ls='-.', alpha=0.5)
    ax0.add_patch(patches.Rectangle((-col_l/2, -0.6), col_l, beam_h+1.2, fc='#f2f2f2', ec='gray', ls='--'))
    ax0.add_patch(patches.Rectangle((span_cc-col_r/2, -0.6), col_r, beam_h+1.2, fc='#f2f2f2', ec='gray', ls='--'))
    
    # Beam & Rebars
    ax0.plot([-col_l/2, span_cc+0.5], [beam_h, beam_h], 'k', lw=2)
    ax0.plot([-col_l/2, span_cc+0.5], [0, 0], 'k', lw=2)
    
    # MT/MB with Ldh Hook
    ax0.plot([x_f_l-ldh_m, span_cc+0.5], [beam_h-0.05, beam_h-0.05], 'blue', lw=2, label='MT')
    ax0.plot([x_f_l-ldh_m, x_f_l-ldh_m], [beam_h-0.05, beam_h-0.05-12*db_m], 'blue', lw=2)
    ax0.plot([x_f_l-ldh_m, span_cc+0.5], [0.05, 0.05], 'red', lw=2, label='MB')
    ax0.plot([x_f_l-ldh_m, x_f_l-ldh_m], [0.05, 0.05+12*db_m], 'red', lw=2)

    # ET/EB
    ax0.plot([et_start, et_end], [beam_h-0.13, beam_h-0.13], 'purple', lw=2.5)
    ax0.plot([eb_start, eb_end], [0.13, 0.13], 'orange', lw=2.5)
    ax0.text((et_start+et_end)/2, beam_h-0.13, f"ET: L={et_end-et_start:.2f}", ha='center', va='bottom', fontsize=8, color='purple', weight='bold')
    ax0.text((eb_start+eb_end)/2, 0.13, f"EB: L={eb_end-eb_start:.2f}", ha='center', va='bottom', fontsize=8, color='darkorange', weight='bold')

    # Dimensions
    ax0.annotate('', xy=(0, beam_h+0.4), xytext=(span_cc, beam_h+0.4), arrowprops=dict(arrowstyle='<->', color='red'))
    ax0.text(span_cc/2, beam_h+0.45, f"Span C/C = {span_cc:.2f} m", color='red', ha='center', weight='bold')
    ax0.annotate('', xy=(x_f_l, -0.4), xytext=(x_f_r, -0.4), arrowprops=dict(arrowstyle='<->', color='black'))
    ax0.text(span_cc/2, -0.55, f"Ln = {ln:.2f} m", ha='center', weight='bold')

    ax0.set_xlim(-1, span_cc+1); ax0.set_ylim(-0.8, beam_h+0.8); ax0.set_aspect('equal'); ax0.axis('off')
    ax0.set_title("Longitudinal Section", fontsize=14, weight='bold')

    # --- 2. Cross Sections ---
    def draw_cs(ax, title, type):
        b, h = 0.4, 0.6
        ax.add_patch(patches.Rectangle((0,0), b, h, fc='#fafafa', ec='k', lw=2))
        ax.set_title(title, fontsize=10, weight='bold')
        # MT
        for i in range(qty_mt): ax.add_patch(patches.Circle((0.08 + i*0.24/(qty_mt-1 if qty_mt>1 else 1), h-0.08), 0.015, color='blue'))
        # MB
        for i in range(qty_mb): ax.add_patch(patches.Circle((0.08 + i*0.24/(qty_mb-1 if qty_mb>1 else 1), 0.08), 0.015, color='red'))
        if type == "mid":
            for i in range(qty_eb): ax.add_patch(patches.Circle((0.08 + i*0.24/(qty_eb-1 if qty_eb>1 else 1), 0.18), 0.015, color='orange'))
        else:
            for i in range(qty_et): ax.add_patch(patches.Circle((0.08 + i*0.24/(qty_et-1 if qty_et>1 else 1), h-0.18), 0.015, color='purple'))
        ax.set_xlim(-0.1, 0.5); ax.set_ylim(-0.1, 0.75); ax.set_aspect('equal'); ax.axis('off')

    draw_cs(fig.add_subplot(gs[2,0], anchor='W'), "Support A-A", "support")
    draw_cs(fig.add_subplot(gs[2,0], anchor='E'), "Mid-Span B-B", "mid")

    # --- 3. Result Box ---
    ax_res = fig.add_subplot(gs[3])
    txt = f"ACI 318-19 Summary\nLd (Straight) = {ld_m:.3f} m\nLdh (Hook) = {ldh_m:.3f} m"
    ax_res.text(0.5, 0.5, txt, ha='center', va='center', weight='bold', color='darkgreen', bbox=dict(fc='#f1f8e9', ec='darkgreen', boxstyle='round,pad=1'))
    ax_res.axis('off')

    return fig

st.pyplot(draw_app())
