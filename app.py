import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np

# ==========================================
# 1. [INPUT SECTION - STREAMLIT SIDEBAR]
# ==========================================
st.set_page_config(layout="wide", page_title="RC Beam Detailer (SI Units)")
st.sidebar.header("🛠 Design Parameters (SI Units)")

fc_ksc = st.sidebar.selectbox("Concrete Strength: f'c (ksc)", options=[210, 240, 280, 320, 350], index=2)
fy_choice = st.sidebar.selectbox("Steel Strength: fy (ksc)", options=[4000, 5000], index=0)

# Conversion to MPa for SI Calculation
fc_mpa = fc_ksc * 0.0980665
fy_mpa = 390 if fy_choice == 4000 else 490

st.sidebar.subheader("Geometry & Reinforcement")
span_cc = st.sidebar.number_input("Span C/C (m):", value=6.40, step=0.10)
col_left_w = st.sidebar.number_input("Left Column Width (m):", value=0.40, step=0.05)
col_right_w = st.sidebar.number_input("Right Column Width (m):", value=0.50, step=0.05)
beam_h = st.sidebar.number_input("Beam Height (m):", value=0.60, step=0.05)
db_mm = st.sidebar.number_input("Main Bar Size (DB-mm):", value=20, step=1)

# Fixed Parameters
stirrup_db = 9       
offset = 0.08
covering = 0.04
db_m = db_mm / 1000

# ==========================================
# 2. [REVISED SI CALCULATION]
# ==========================================
psi_t, psi_e, psi_g, lambda_val = 1.0, 1.0, 1.0, 1.0
psi_s = 0.8 if db_mm <= 19 else 1.0  
sqrt_fc_mpa = min(np.sqrt(fc_mpa), 8.3) 

# Ld (Straight Bar) - ใช้ตัวหาร 1.7 ตามเงื่อนไข Clear Space เพียงพอ
ld_m_val = (fy_mpa * psi_t * psi_e * psi_g * psi_s) / (1.7 * lambda_val * sqrt_fc_mpa) * (db_mm / 1000)
ld_m = max(ld_m_val, 0.30)

# Ldh (90-deg Hook) - ใช้ตัวหาร 23 ตามที่ระบุ
psi_c = (fc_mpa / 103.5) + 0.6 if fc_mpa < 40 else 1.0
ldh_mm = (fy_mpa * psi_e * psi_c * 1.0) / (23 * lambda_val * sqrt_fc_mpa) * (db_mm**1.5)
ldh_m = max(ldh_mm / 1000, 8 * db_m, 0.15)

# ==========================================
# 3. [COORDINATES & DRAWING]
# ==========================================
x_face_l = col_left_w / 2             
x_face_r = span_cc - col_right_w / 2  
clear_span = x_face_r - x_face_l      

et_mid_reach = clear_span * 0.25
et_mid_start = x_face_r - (et_mid_reach + 15 * db_m)
et_mid_end = (span_cc + col_right_w/2) + (et_mid_reach + 15 * db_m)
et_cont_total_len = et_mid_end - et_mid_start

eb_start = x_face_l + (clear_span * 0.25) - (20 * db_m)
eb_end = x_face_r - (clear_span * 0.25) + (20 * db_m)
eb_total_len = eb_end - eb_start

x_break = span_cc + (col_right_w / 2) + 1.0 
hook_len = 12 * db_m 

def draw_cross(ax, title, s_type):
    b, h = 0.40, 0.60
    db_r = db_m/2
    s_db_r = stirrup_db/2000
    layer_dist = 0.05 
    ax.add_patch(patches.Rectangle((0, 0), b, h, facecolor='#f8f9fa', edgecolor='black', lw=2))
    s_off = covering + (stirrup_db/2000)
    ax.add_patch(patches.Rectangle((s_off, s_off), b-2*s_off, h-2*s_off, fill=False, edgecolor='black', lw=1.5))
    r_x = [covering + s_db_r + db_r, b - (covering + s_db_r + db_r)]
    y_top_m, y_bot_m = h - covering - s_db_r - db_r, covering + s_db_r + db_r
    for x in r_x:
        ax.add_patch(patches.Circle((x, y_top_m), db_r, color='blue', zorder=3)) 
        ax.add_patch(patches.Circle((x, y_bot_m), db_r, color='red', zorder=3))  
    if s_type == "mid":
        for x in r_x: ax.add_patch(patches.Circle((x, y_bot_m + layer_dist), db_r, color='orange', zorder=3))
    else:
        for x in r_x: ax.add_patch(patches.Circle((x, y_top_m - layer_dist), db_r, color='purple', zorder=3))
    ax.set_xlim(-0.15, b+0.15); ax.set_ylim(-0.25, h+0.25); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, weight='bold', pad=25, fontsize=10)

def draw_main():
    st.title("RC Beam Detail (ACI 318-19 SI Metric)")
    
    # คำอธิบายสูตรที่ใช้
    st.info(f"สูตรที่ใช้: Ld = (fy * psi_s) / (1.7 * √f'c) * db  |  Ldh = (fy * psi_c) / (23 * √f'c) * db^1.5")

    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(3, 4, height_ratios=[1.8, 1, 0.3], hspace=0.2)
    ax0 = fig.add_subplot(gs[0, :])
    
    # Columns
    ax0.axvline(x=0, color='gray', ls='-.', lw=1.2, alpha=0.8)
    ax0.axvline(x=span_cc, color='gray', ls='-.', lw=1.2, alpha=0.8)
    ax0.add_patch(patches.Rectangle((-col_left_w/2, -0.6), col_left_w, beam_h+1.2, color='#f2f2f2', ec='gray', ls='--'))
    ax0.add_patch(patches.Rectangle((span_cc-col_right_w/2, -0.6), col_right_w, beam_h+1.2, color='#f2f2f2', ec='gray', ls='--'))
    
    # Beam
    ax0.plot([-col_left_w/2, x_break], [beam_h, beam_h], 'k', lw=2); ax0.plot([-col_left_w/2, x_break], [0, 0], 'k', lw=2)
    
    # Rebars with Calculated Ldh
    x_re_start = x_face_l - ldh_m
    ax0.plot([x_re_start, x_break+0.3], [beam_h-0.05, beam_h-0.05], 'blue', lw=2)
    ax0.plot([x_re_start, x_re_start], [beam_h-0.05, beam_h-0.05-hook_len], 'blue', lw=2)
    ax0.plot([x_re_start, x_break+0.3], [0.05, 0.05], 'red', lw=2)
    ax0.plot([x_re_start, x_re_start], [0.05, 0.05+hook_len], 'red', lw=2)

    # Extra Bars Label
    y_et, y_eb = beam_h - 0.05 - offset, 0.05 + offset
    ax0.plot([et_mid_start, et_mid_end], [y_et, y_et], 'darkmagenta', lw=2.5)
    ax0.plot([eb_start, eb_end], [y_eb, y_eb], 'orange', lw=2.5)
    ax0.text((et_mid_start+et_mid_end)/2, y_et - 0.08, f"L = {et_cont_total_len:.2f} m", color='darkmagenta', ha='center', weight='bold', fontsize=9)
    ax0.text((eb_start+eb_end)/2, y_eb + 0.05, f"L = {eb_total_len:.2f} m", color='darkorange', ha='center', weight='bold', fontsize=9)

    ax0.set_title(f"LONGITUDINAL SECTION (f'c={fc_mpa:.1f} MPa, fy={fy_mpa} MPa)", fontsize=15, weight='bold', pad=30)
    ax0.set_xlim(-1, x_break+0.5); ax0.set_ylim(-1.0, beam_h+1.0); ax0.set_aspect('equal'); ax0.axis('off')

    draw_cross(fig.add_subplot(gs[1, 1]), "Section B-B (Mid-Span)", "mid")
    draw_cross(fig.add_subplot(gs[1, 2]), "Section A-A (Support)", "support")

# ==========================================
    # [KDA STANDARD LOGIC - REVISED]
    # ==========================================
    kda_l1_multiplier = 0
    kda_ldh_multiplier = 0

    if fy_choice == 4000:
        # เงื่อนไขสำหรับ L1 (Lapping)
        if fc_ksc in [210, 240]:
            kda_l1_multiplier = 50
            kda_ldh_multiplier = 17
        elif fc_ksc in [280, 320, 350]:
            kda_l1_multiplier = 45
            kda_ldh_multiplier = 16
            
    elif fy_choice == 5000:
        if fc_ksc in [210, 240]:
            kda_l1_multiplier = 68
            kda_ldh_multiplier = 21
        elif fc_ksc == 280:
            kda_l1_multiplier = 60
            kda_ldh_multiplier = 20
        elif fc_ksc in [320, 350]:
            kda_l1_multiplier = 55
            kda_ldh_multiplier = 20

    # คำนวณค่าเพื่อแสดงผล (หน่วย mm)
    l1_kda_display = kda_l1_multiplier * db_mm
    ldh_kda_display = kda_ldh_multiplier * db_mm

    # ==========================================
    # [SUMMARY SECTION]
    # ==========================================
    
    # --- กล่องที่ 1 (ACI 318-19) ---
    ax_txt = fig.add_subplot(gs[2, :2])
    ld_mm_display = ld_m * 1000
    ldh_mm_display = ldh_m * 1000
    
    res_txt = (f"ACI 318-19: f'c = {fc_ksc} ksc,  fy = {fy_choice} ksc,  Main Bar = DB{db_mm}\n"
               f"Ld (Straight) = {ld_mm_display:.0f} mm.  |  Ldh (90 Hook) = {ldh_mm_display:.0f} mm.")
    
    ax_txt.text(0.5, 0.5, res_txt, ha='center', va='center', fontsize=12, weight='bold', color='darkgreen',
                bbox=dict(facecolor='#f1f8e9', edgecolor='darkgreen', boxstyle='round,pad=1.0'))
    ax_txt.axis('off')

    # --- กล่องที่ 2 (KDA Standard) ---
    ax_txt2 = fig.add_subplot(gs[2, 2:])
    
    res_txt2 = (f"KDA Standard: f'c = {fc_ksc} ksc,  fy = {fy_choice} ksc,  Main Bar = DB{db_mm}\n"
                f"L1 (Lapping) = {l1_kda_display:.0f} mm.  |  Ldh (90 Hook) = {ldh_kda_display:.0f} mm.")
    
    ax_txt2.text(0.5, 0.5, res_txt2, ha='center', va='center', fontsize=12, weight='bold', color='#1a237e',
                bbox=dict(facecolor='#e8eaf6', edgecolor='#1a237e', boxstyle='round,pad=1.0'))
    ax_txt2.axis('off')

    st.pyplot(fig)

draw_main()
