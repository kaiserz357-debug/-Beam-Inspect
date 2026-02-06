import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np

# ==========================================
# 1. [STREAMLIT UI SECTION]
# ==========================================
st.set_page_config(layout="wide")
st.title("Beam Reinforcement Design (ACI 318-19)")

# สร้าง Sidebar สำหรับ Input
st.sidebar.header("Design Parameters")
# แก้ไขจุดที่ต้องการ: Dropdown สำหรับ f'c
fc_prime = st.sidebar.selectbox(
    "Select f'c (ksc):",
    options=[210, 240, 280, 320, 350],
    index=2  # default ที่ 280
)

# Input อื่นๆ (เผื่ออยากปรับในอนาคต)
fy = 4000            
span_cc = 6.40       
col_left_w = 0.40    
col_right_w = 0.50   
beam_h = 0.60
db_mm = 20           
db_m = db_mm / 1000
stirrup_db = 9       
offset = 0.08
covering = 0.04

# ==========================================
# 2. [ACI 318-19 CALCULATION LOGIC]
# ==========================================
psi_t, psi_e, psi_g, lambda_val = 1.0, 1.0, 1.0, 1.0
psi_s = 0.8 if db_mm <= 19 else 1.0  
sqrt_fc_ksc = min(np.sqrt(fc_prime), 26.2)
fc_psi = fc_prime * 14.223
sqrt_fc_psi = min(np.sqrt(fc_psi), 100)

ld_m = (fy * psi_t * psi_e * psi_g * psi_s) / (5.3 * lambda_val * sqrt_fc_ksc) * db_m
ld_m = max(ld_m, 0.30)

psi_c = (fc_psi / 15000) + 0.6 if fc_psi < 6000 else 1.0
db_in = db_mm / 25.4
fy_psi = fy * 14.223
ldh_in = (fy_psi * psi_e * 1.0 * 1.0 * psi_c) / (50 * lambda_val * sqrt_fc_psi) * (db_in**1.5)
ldh_m = max(ldh_in * 0.0254, 8 * db_m, 0.15)

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
        ax.text(b/2, -0.12, f"2-DB{db_mm} (Extra Bot)", ha='center', color='orange', weight='bold', fontsize=9)
    else:
        for x in r_x: ax.add_patch(patches.Circle((x, y_top_m - layer_dist), db_r, color='purple', zorder=3))
        ax.text(b/2, h+0.07, f"2-DB{db_mm} (Extra Top)", ha='center', color='purple', weight='bold', fontsize=9)
    ax.set_xlim(-0.15, b+0.15); ax.set_ylim(-0.25, h+0.25); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, weight='bold', pad=25, fontsize=10)

# Main Plotting
fig = plt.figure(figsize=(16, 10))
gs = gridspec.GridSpec(3, 4, height_ratios=[1.8, 1, 0.3], hspace=0.2)
ax0 = fig.add_subplot(gs[0, :])

# Draw Columns, Beam, Rebars (เหมือนเดิม)
ax0.axvline(x=0, color='gray', ls='-.', lw=1.2, alpha=0.8)
ax0.axvline(x=span_cc, color='gray', ls='-.', lw=1.2, alpha=0.8)
ax0.add_patch(patches.Rectangle((-col_left_w/2, -0.6), col_left_w, beam_h+1.2, color='#f2f2f2', ec='gray', ls='--'))
ax0.add_patch(patches.Rectangle((span_cc-col_right_w/2, -0.6), col_right_w, beam_h+1.2, color='#f2f2f2', ec='gray', ls='--'))
ax0.plot([-col_left_w/2, x_break], [beam_h, beam_h], 'k', lw=2); ax0.plot([-col_left_w/2, x_break], [0, 0], 'k', lw=2)
ax0.plot([-col_left_w/2, -col_left_w/2], [0, beam_h], 'k', lw=2)
bw = 0.12; ax0.plot([x_break, x_break-bw, x_break+bw, x_break], [beam_h, beam_h*0.6, beam_h*0.4, 0], 'k', lw=2)

x_re_start = x_face_l - ldh_m
ax0.plot([x_re_start, x_break+0.3], [beam_h-0.05, beam_h-0.05], 'blue', lw=2)
ax0.plot([x_re_start, x_re_start], [beam_h-0.05, beam_h-0.05-hook_len], 'blue', lw=2)
ax0.plot([x_re_start, x_break+0.3], [0.05, 0.05], 'red', lw=2)
ax0.plot([x_re_start, x_re_start], [0.05, 0.05+hook_len], 'red', lw=2)

y_et, y_eb = beam_h - 0.05 - offset, 0.05 + offset
ax0.plot([et_mid_start, et_mid_end], [y_et, y_et], 'darkmagenta', lw=2.5)
ax0.plot([eb_start, eb_end], [y_eb, y_eb], 'orange', lw=2.5)

ax0.set_title(f"LONGITUDINAL SECTION (f'c = {fc_prime} ksc)", fontsize=15, weight='bold', pad=30)
ax0.set_xlim(-1, x_break+0.5); ax0.set_ylim(-1.0, beam_h+1.0); ax0.set_aspect('equal'); ax0.axis('off')

draw_cross(fig.add_subplot(gs[1, 1]), "Section B-B (Mid-Span)", "mid")
draw_cross(fig.add_subplot(gs[1, 2]), "Section A-A (Support)", "support")

ax_txt = fig.add_subplot(gs[2, :])
res_txt = (f"ACI 318-19: f'c = {fc_prime} ksc, Fy = {fy} ksc | Ld = {ld_m:.3f} m, Ldh = {ldh_m:.3f} m")
ax_txt.text(0.5, 0.5, res_txt, ha='center', va='center', fontsize=12, weight='bold', color='darkgreen',
            bbox=dict(facecolor='#f1f8e9', edgecolor='darkgreen', boxstyle='round,pad=1.0'))
ax_txt.axis('off')

# แสดงรูปภาพใน Streamlit
st.pyplot(fig)
