import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np

# ปรับตั้งค่าหน้าจอให้เหมาะกับมือถือ
st.set_page_config(page_title="Beam Rebar Calculator", layout="centered")

st.title("🏗️ Beam Rebar Detailer")
st.write("ACI 318-19 (ksc unit)")

# ==========================================
# 1. [SIDEBAR / INPUT SECTION]
# ==========================================
with st.sidebar:
    st.header("📌 Input Parameters")
    fc_prime = st.number_input("f'c (ksc)", value=280)
    fy = st.number_input("Fy (ksc)", value=4000)
    
    st.divider()
    span_cc = st.number_input("Span C/C (m)", value=6.40)
    col_left_w = st.number_input("Left Column Width (m)", value=0.40)
    col_right_w = st.number_input("Right Column Width (m)", value=0.50)
    beam_h = st.number_input("Beam Height (m)", value=0.60)
    
    st.divider()
    db_mm = st.selectbox("Main Bar Size (mm)", [12, 16, 20, 25, 28], index=2)
    db_m = db_mm / 1000
    stirrup_db = st.selectbox("Stirrup Size (mm)", [6, 9, 12], index=1)
    covering = 0.04
    offset = 0.08

# ==========================================
# 2. [CALCULATION LOGIC]
# ==========================================
psi_t, psi_e, psi_g, lambda_val = 1.0, 1.0, 1.0, 1.0
psi_s = 0.8 if db_mm <= 19 else 1.0  
sqrt_fc_ksc = min(np.sqrt(fc_prime), 26.2)

# Ld (Straight)
ld_m = (fy * psi_t * psi_e * psi_g * psi_s) / (5.3 * lambda_val * sqrt_fc_ksc) * db_m
ld_m = max(ld_m, 0.30)

# Ldh (Hook)
fc_psi = fc_prime * 14.223
sqrt_fc_psi = min(np.sqrt(fc_psi), 100)
psi_c = (fc_psi / 15000) + 0.6 if fc_psi < 6000 else 1.0
db_in = db_mm / 25.4
fy_psi = fy * 14.223
ldh_in = (fy_psi * psi_e * 1.0 * 1.0 * psi_c) / (50 * lambda_val * sqrt_fc_psi) * (db_in**1.5)
ldh_m = max(ldh_in * 0.0254, 8 * db_m, 0.15)

# --- Coordinates ---
x_face_l = col_left_w / 2            
x_face_r = span_cc - col_right_w / 2 
clear_span = x_face_r - x_face_l     

et_reach = clear_span * 0.25
et_mid_start = x_face_r - (et_reach + 15 * db_m)
et_mid_end = (span_cc + col_right_w/2) + (et_reach + 15 * db_m)
et_total = et_mid_end - et_mid_start

eb_start = x_face_l + (clear_span * 0.25) - (20 * db_m)
eb_end = x_face_r - (clear_span * 0.25) + (20 * db_m)
eb_total = eb_end - eb_start

# ==========================================
# 3. [DRAWING SECTION]
# ==========================================
def draw_drawing():
    # ปรับ figsize ให้เป็นแนวตั้งสำหรับมือถือ
    fig = plt.figure(figsize=(10, 14))
    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 0.8, 0.2], hspace=0.3)

    # --- Longitudinal ---
    ax0 = fig.add_subplot(gs[0])
    ax0.axvline(x=0, color='gray', ls='-.', lw=1)
    ax0.axvline(x=span_cc, color='gray', ls='-.', lw=1)
    ax0.add_patch(patches.Rectangle((-col_left_w/2, -0.4), col_left_w, beam_h+0.8, color='#f2f2f2', ec='gray', ls='--'))
    ax0.add_patch(patches.Rectangle((span_cc-col_right_w/2, -0.4), col_right_w, beam_h+0.8, color='#f2f2f2', ec='gray', ls='--'))
    
    ax0.plot([-col_left_w/2, span_cc+0.5], [beam_h, beam_h], 'k', lw=2)
    ax0.plot([-col_left_w/2, span_cc+0.5], [0, 0], 'k', lw=2)
    
    # Rebars
    x_re_start = x_face_l - ldh_m
    ax0.plot([x_re_start, span_cc+0.4], [beam_h-0.05, beam_h-0.05], 'blue', lw=2)
    ax0.plot([x_re_start, x_re_start], [beam_h-0.05, beam_h-0.05-12*db_m], 'blue', lw=2)
    ax0.plot([x_re_start, span_cc+0.4], [0.05, 0.05], 'red', lw=2)
    ax0.plot([x_re_start, x_re_start], [0.05, 0.05+12*db_m], 'red', lw=2)

    # Extra Bars
    ax0.plot([et_mid_start, et_mid_end], [beam_h-0.13, beam_h-0.13], 'darkmagenta', lw=2.5)
    ax0.plot([eb_start, eb_end], [0.13, 0.13], 'orange', lw=2.5)
    
    ax0.set_title("Longitudinal Section", fontsize=14, weight='bold')
    ax0.set_xlim(-0.8, span_cc+0.8); ax0.set_ylim(-0.6, beam_h+0.6); ax0.set_aspect('equal'); ax0.axis('off')

    # --- Cross Sections (จัดเรียงแนวนอนในแถวเดียวกัน) ---
    ax1 = fig.add_subplot(gs[1])
    ax1.axis('off')
    # วาดหน้าตัดย่อยใน ax1
    def draw_inner_cross(x_off, title, s_type):
        b, h = 0.4, 0.6
        ax1.add_patch(patches.Rectangle((x_off, 0), b, h, fc='#f8f9fa', ec='black', lw=2))
        ax1.text(x_off + b/2, h+0.05, title, ha='center', weight='bold')
        # วาดเหล็กแบบย่อ
        db_r = db_m/2
        ax1.add_patch(patches.Circle((x_off+0.08, 0.52), db_r, color='blue'))
        ax1.add_patch(patches.Circle((x_off+0.32, 0.52), db_r, color='blue'))
        ax1.add_patch(patches.Circle((x_off+0.08, 0.08), db_r, color='red'))
        ax1.add_patch(patches.Circle((x_off+0.32, 0.08), db_r, color='red'))
        if s_type == "mid":
            ax1.add_patch(patches.Circle((x_off+0.08, 0.18), db_r, color='orange'))
            ax1.add_patch(patches.Circle((x_off+0.32, 0.18), db_r, color='orange'))
        else:
            ax1.add_patch(patches.Circle((x_off+0.08, 0.42), db_r, color='purple'))
            ax1.add_patch(patches.Circle((x_off+0.32, 0.42), db_r, color='purple'))

    draw_inner_cross(0, "Support", "support")
    draw_inner_cross(0.6, "Mid-Span", "mid")
    ax1.set_xlim(-0.1, 1.1); ax1.set_ylim(-0.1, 0.8); ax1.set_aspect('equal')

    # --- Summary Box ---
    ax2 = fig.add_subplot(gs[2])
    res_txt = (f"Ld = {ld_m:.3f} m. | Ldh = {ldh_m:.3f} m.\n"
               f"Extra Top Length = {et_total:.2f} m.\n"
               f"Extra Bot Length = {eb_total:.2f} m.")
    ax2.text(0.5, 0.5, res_txt, ha='center', va='center', weight='bold', color='darkgreen',
             bbox=dict(facecolor='#f1f8e9', edgecolor='darkgreen', boxstyle='round,pad=1'))
    ax2.axis('off')
    
    return fig

# แสดงผลใน Streamlit
st.pyplot(draw_drawing())
