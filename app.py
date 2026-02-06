import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np

# ==========================================
# 1. [INPUT SECTION - STREAMLIT SIDEBAR]
# ==========================================
st.set_page_config(layout="wide", page_title="RC Beam Detailer")
st.sidebar.header("🛠 Design Parameters")

# --- Dropdown Inputs ---
fc_prime = st.sidebar.selectbox(
    "Concrete Strength: f'c (ksc)", 
    options=[210, 240, 280, 320, 350], 
    index=2
)

fy = st.sidebar.selectbox(
    "Steel Strength: fy (ksc)", 
    options=[4000, 5000], 
    index=0
)

# --- Numeric Inputs ---
st.sidebar.subheader("Geometry & Reinforcement")
span_cc = st.sidebar.number_input("Span C/C (m):", value=6.40, step=0.10)
col_left_w = st.sidebar.number_input("Left Column Width (m):", value=0.40, step=0.05)
col_right_w = st.sidebar.number_input("Right Column Width (m):", value=0.50, step=0.05)
beam_h = st.sidebar.number_input("Beam Height (m):", value=0.60, step=0.05)
db_mm = st.sidebar.number_input("Main Bar Size (DB-mm):", value=20, step=1)
stirrup_db = st.sidebar.number_input("Stirrup Size (mm):", value=9, step=1)

# Fixed Parameters
offset = 0.08
covering = 0.04
db_m = db_mm / 1000

# ==========================================
# 2. [ACI 318-19 CALCULATION LOGIC]
# ==========================================
psi_t, psi_e, psi_g, lambda_val = 1.0, 1.0, 1.0, 1.0
psi_s = 0.8 if db_mm <= 19 else 1.0  
sqrt_fc_ksc = min(np.sqrt(fc_prime), 26.2)
fc_psi = fc_prime * 14.223
sqrt_fc_psi = min(np.sqrt(fc_psi), 100)

# Ld calculation
ld_m = (fy * psi_t * psi_e * psi_g * psi_s) / (5.3 * lambda_val * sqrt_fc_ksc) * db_m
ld_m = max(ld_m, 0.30)

# Ldh calculation
psi_c = (fc_psi / 15000) + 0.6 if fc_psi < 6000 else 1.0
db_in = db_mm / 25.4
fy_psi = fy * 14.223
ldh_in = (fy_psi * psi_e * 1.0 * 1.0 * psi_c) / (50 * lambda_val * sqrt_fc_psi) * (db_in**1.5)
ldh_m = max(ldh_in * 0.0254, 8 * db_m, 0.15)

# ==========================================
# 3. [REVISED COORDINATES]
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

# ==========================================
# 4. [MAIN DRAWING FUNCTION]
# ==========================================
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
        ax.text(b/2, -0.12, f"2-DB{db_mm} (Extra Bot)", ha='center', color='orange', weight='bold', fontsize=9)
    else:
        for x in r_x: ax.add_patch(patches.Circle((x, y_top_m - layer_dist), db_r, color='purple', zorder=3))
        ax.text(b/2, h+0.07, f"2-DB{db_mm} (Extra Top)", ha='center', color='purple', weight='bold', fontsize=9)
    ax.set_xlim(-0.15, b+0.15); ax.set_ylim(-0.25, h+0.25); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, weight='bold', pad=25, fontsize=10)

def draw_main():
    st.title("RC Beam Reinforcement Detail (ACI 318-19)")
    
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(3, 4, height_ratios=[1.8, 1, 0.3], hspace=0.2)
    ax0 = fig.add_subplot(gs[0, :])
    
    # --- Columns & Grid lines ---
    ax0.axvline(x=0, color='gray', ls='-.', lw=1.2, alpha=0.8)
    ax0.axvline(x=span_cc, color='gray', ls='-.', lw=1.2, alpha=0.8)
    ax0.text(0, -0.7, f"COL \n({col_left_w:.2f})", color='blue', ha='center', fontsize=10)
    ax0.text(span_cc, -0.7, f"COL \n({col_right_w:.2f})", color='blue', ha='center', fontsize=10)
    
    ax0.add_patch(patches.Rectangle((-col_left_w/2, -0.6), col_left_w, beam_h+1.2, color='#f2f2f2', ec='gray', ls='--'))
    ax0.add_patch(patches.Rectangle((span_cc-col_right_w/2, -0.6), col_right_w, beam_h+1.2, color='#f2f2f2', ec='gray', ls='--'))
    
    # Beam Outline
    ax0.plot([-col_left_w/2, x_break], [beam_h, beam_h], 'k', lw=2); ax0.plot([-col_left_w/2, x_break], [0, 0], 'k', lw=2)
    ax0.plot([-col_left_w/2, -col_left_w/2], [0, beam_h], 'k', lw=2)
    bw = 0.12; ax0.plot([x_break, x_break-bw, x_break+bw, x_break], [beam_h, beam_h*0.6, beam_h*0.4, 0], 'k', lw=2)

    # --- Dimension Lines ---
    ax0.annotate('', xy=(0, beam_h + 0.35), xytext=(span_cc, beam_h + 0.35), arrowprops=dict(arrowstyle='<->', color='red'))
    ax0.text(span_cc/2, beam_h + 0.40, f"Span C/C = {span_cc:.2f} m.", color='red', ha='center', weight='bold')
    ax0.annotate('', xy=(x_face_l, -0.35), xytext=(x_face_r, -0.35), arrowprops=dict(arrowstyle='<->', color='black'))
    ax0.text((x_face_l + x_face_r)/2, -0.45, f"Clear Span Lo = {clear_span:.2f} m.", ha='center')

    # Rebars
    x_re_start = x_face_l - ldh_m
    ax0.plot([x_re_start, x_break+0.3], [beam_h-0.05, beam_h-0.05], 'blue', lw=2)
    ax0.plot([x_re_start, x_re_start], [beam_h-0.05, beam_h-0.05-hook_len], 'blue', lw=2)
    ax0.plot([x_re_start, x_break+0.3], [0.05, 0.05], 'red', lw=2)
    ax0.plot([x_re_start, x_re_start], [0.05, 0.05+hook_len], 'red', lw=2)

    # Extra Bars
    y_et, y_eb = beam_h - 0.05 - offset, 0.05 + offset
    ax0.plot([et_mid_start, et_mid_end], [y_et, y_et], 'darkmagenta', lw=2.5)
    ax0.plot([eb_start, eb_end], [y_eb, y_eb], 'orange', lw=2.5)
    ax0.text((et_mid_start+et_mid_end)/2, y_et - 0.08, f"L = {et_cont_total_len:.2f} m", color='darkmagenta', ha='center', weight='bold', fontsize=9)
    ax0.text((eb_start+eb_end)/2, y_eb + 0.05, f"L = {eb_total_len:.2f} m", color='darkorange', ha='center', weight='bold', fontsize=9)

    ax0.set_title("LONGITUDINAL SECTION", fontsize=15, weight='bold', pad=30)
    ax0.set_xlim(-1, x_break+0.5); ax0.set_ylim(-1.0, beam_h+1.0); ax0.set_aspect('equal'); ax0.axis('off')

    # Cross Sections
    draw_cross(fig.add_subplot(gs[1, 1]), "Section B-B (Mid-Span)", "mid")
    draw_cross(fig.add_subplot(gs[1, 2]), "Section A-A (Support)", "support")

    # Calculation Summary (Bottom)
    ax_txt = fig.add_subplot(gs[2, :])
    res_txt = (f"ACI 318-19 Summary:  f'c = {fc_prime} ksc,  Fy = {fy} ksc,  Main Bar = DB{db_mm}\n"
               f"Development Length: Ld = {ld_m:.3f} m.    |    Hook Length: Ldh = {ldh_m:.3f} m.")
    ax_txt.text(0.5, 0.5, res_txt, ha='center', va='center', fontsize=12, weight='bold', color='darkgreen',
                bbox=dict(facecolor='#f1f8e9', edgecolor='darkgreen', boxstyle='round,pad=1.0'))
    ax_txt.axis('off')

    st.pyplot(fig)

# Execute
draw_main()
