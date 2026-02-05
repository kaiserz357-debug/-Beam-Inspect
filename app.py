import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.gridspec as gridspec
import numpy as np

# ตั้งค่าหน้าจอแนวตั้งสำหรับมือถือ
st.set_page_config(page_title="Beam Detailer", layout="centered")

st.title("🏗️ Beam Rebar Calculator")

# ==========================================
# 1. [INPUT SECTION]
# ==========================================
with st.sidebar:
    st.header("⚙️ Geometry & Material")
    fc_prime = st.number_input("f'c (ksc)", value=280)
    fy = st.number_input("Fy (ksc)", value=4000)
    span_cc = st.number_input("Span C/C (m)", value=6.40)
    col_l = st.number_input("Left Col Width (m)", value=0.40)
    col_r = st.number_input("Right Col Width (m)", value=0.50)
    beam_h_real = st.number_input("Beam Height (m)", value=0.60)
    
    # โกง Scale ลึก 2 เท่าสำหรับการวาด
    beam_h = beam_h_real * 2 

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
sqrt_fc = min(np.sqrt(fc_prime), 26.2)
psi_s = 0.8 if db_main <= 19 else 1.0
ld_m = (fy * 1.0 * 1.0 * 1.0 * psi_s) / (5.3 * 1.0 * sqrt_fc) * db_m
ld_m = max(ld_m, 0.30)

fc_psi = fc_prime * 14.223
psi_c = (fc_psi / 15000) + 0.6 if fc_psi < 6000 else 1.0
ldh_in = (fy * 14.223 * 1.0 * 1.0 * 1.0 * psi_c) / (50 * 1.0 * min(np.sqrt(fc_psi), 100)) * ((db_main/25.4)**1.5)
ldh_m = max(ldh_in * 0.0254, 8 * db_m, 0.15)

x_f_l, x_f_r = col_l / 2, span_cc - col_r / 2
ln = x_f_r - x_f_l
et_start = x_f_r - (ln * 0.25 + 15 * db_e_m)
et_end = (span_cc + col_r/2) + (ln * 0.25 + 15 * db_e_m)
eb_start = x_f_l + (ln * 0.25) - (20 * db_e_m)
eb_end = x_f_r - (ln * 0.25) + (20 * db_e_m)

# ==========================================
# 3. [DRAWING FUNCTION]
# ==========================================
def draw_app():
    # ปรับ figsize ให้กระชับขึ้นเพื่อลดการ scroll
    fig = plt.figure(figsize=(10, 12))
    # จัดการ Grid: 0=Long, 1=Cross, 2=Table
    gs = gridspec.GridSpec(3, 1, height_ratios=[1.2, 0.6, 0.2], hspace=0.3)

    # --- 1. Longitudinal Section ---
    ax0 = fig.add_subplot(gs[0])
    ax0.axvline(0, color='gray', ls='-.', alpha=0.5)
    ax0.axvline(span_cc, color='gray', ls='-.', alpha=0.5)
    ax0.add_patch(patches.Rectangle((-col_l/2, -0.4), col_l, beam_h+0.8, fc='#f2f2f2', ec='gray', ls='--'))
    ax0.add_patch(patches.Rectangle((span_cc-col_r/2, -0.4), col_r, beam_h+0.8, fc='#f2f2f2', ec='gray', ls='--'))
    ax0.plot([-col_l/2, span_cc+0.5], [beam_h, beam_h], 'k', lw=2)
    ax0.plot([-col_l/2, span_cc+0.5], [0, 0], 'k', lw=2)
    
    hook_vis = 12 * db_m * 2
    ax0.plot([x_f_l-ldh_m, span_cc+0.5], [beam_h-0.08, beam_h-0.08], 'blue', lw=2)
    ax0.plot([x_f_l-ldh_m, x_f_l-ldh_m], [beam_h-0.08, beam_h-0.08-hook_vis], 'blue', lw=2)
    ax0.plot([x_f_l-ldh_m, span_cc+0.5], [0.08, 0.08], 'red', lw=2)
    ax0.plot([x_f_l-ldh_m, x_f_l-ldh_m], [0.08, 0.08+hook_vis], 'red', lw=2)

    # ET/EB
    ax0.plot([et_start, et_end], [beam_h-0.25, beam_h-0.25], 'purple', lw=2.5)
    ax0.text((et_start+et_end)/2, beam_h-0.30, f"ET (cont'): L={et_end-et_start:.2f} m", 
             ha='center', va='top', fontsize=9, color='purple', weight='bold')
    
    ax0.plot([eb_start, eb_end], [0.25, 0.25], 'orange', lw=2.5)
    ax0.text((eb_start+eb_end)/2, 0.30, f"EB: L={eb_end-eb_start:.2f} m", 
             ha='center', va='bottom', fontsize=9, color='darkorange', weight='bold')

    # Dimensions
    ax0.annotate('', xy=(0, beam_h+0.4), xytext=(span_cc, beam_h+0.4), arrowprops=dict(arrowstyle='<->', color='red'))
    ax0.text(span_cc/2, beam_h+0.45, f"Span C/C = {span_cc:.2f} m", color='red', ha='center', weight='bold')
    ax0.annotate('', xy=(x_f_l, -0.4), xytext=(x_f_r, -0.4), arrowprops=dict(arrowstyle='<->', color='black'))
    ax0.text(span_cc/2, -0.55, f"Ln = {ln:.2f} m", ha='center', weight='bold')

    ax0.set_xlim(-1, span_cc+1); ax0.set_ylim(-1.0, beam_h+1.0); ax0.set_aspect('equal'); ax0.axis('off')
    ax0.set_title(f"Longitudinal Section (Actual H={beam_h_real:.2f} m)", fontsize=13, weight='bold')

    # --- 2. Cross Sections (Moved closer) ---
    def draw_cs(ax, title, type):
        b, h = 0.4, 0.6
        ax.add_patch(patches.Rectangle((0,0), b, h, fc='#fafafa', ec='k', lw=2))
        ax.set_title(title, fontsize=10, weight='bold', pad=10)
        # Rebar Circles
        for i in range(qty_mt): ax.add_patch(patches.Circle((0.08 + i*0.24/(max(qty_mt-1,1)), h-0.08), 0.015, color='blue'))
        for i in range(qty_mb): ax.add_patch(patches.Circle((0.08 + i*0.24/(max(qty_mb-1,1)), 0.08), 0.015, color='red'))
        if type == "mid":
            for i in range(qty_eb): ax.add_patch(patches.Circle((0.08 + i*0.24/(max(qty_eb-1,1)), 0.18), 0.015, color='orange'))
        else:
            for i in range(qty_et): ax.add_patch(patches.Circle((0.08 + i*0.24/(max(qty_et-1,1)), h-0.18), 0.015, color='purple'))
        ax.set_xlim(-0.1, 0.5); ax.set_ylim(-0.1, 0.8); ax.set_aspect('equal'); ax.axis('off')

    # วาดหน้าตัดสองอันข้างกันใน Grid เดียวกัน
    inner_gs = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs[1], wspace=0.1)
    draw_cs(fig.add_subplot(inner_gs[0]), "Support A-A", "support")
    draw_cs(fig.add_subplot(inner_gs[1]), "Mid-Span B-B", "mid")

    # --- 3. Result Summary (Moved closer) ---
    ax_res = fig.add_subplot(gs[2])
    txt = f"ACI 318-19 Summary:  Ld = {ld_m:.3f} m  |  Ldh = {ldh_m:.3f} m"
    ax_res.text(0.5, 0.5, txt, ha='center', va='center', weight='bold', color='darkgreen', 
                bbox=dict(fc='#f1f8e9', ec='darkgreen', boxstyle='round,pad=0.8', alpha=0.9))
    ax_res.axis('off')

    return fig

st.pyplot(draw_app())
