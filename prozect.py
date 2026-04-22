
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings('ignore')

BG     = "#0a0f1e"
CARD   = "#0d1527"
ACCENT = "#1e2d52"
TEXT   = "#e8eaf6"
MUTED  = "#7986cb"
TEAL   = "#4db6ac"
PURPLE = "#7986cb"
RED    = "#ef5350"
AMBER  = "#ffb74d"

ERA_COLORS = {"Space Race": RED, "Cold War Era": PURPLE,
              "Post-Cold War": AMBER, "Commercial Era": TEAL}
ERA_ORDER  = ["Space Race", "Cold War Era", "Post-Cold War", "Commercial Era"]

df = pd.read_csv('/mnt/user-data/uploads/space_missions.csv', encoding='latin1')
df.columns = df.columns.str.strip()
df['Date']        = pd.to_datetime(df['Date'], errors='coerce')
df['Launch Year'] = df['Date'].dt.year
df['Price']       = pd.to_numeric(df['Price'], errors='coerce')
for c in ['Company','Location','Rocket','Mission','RocketStatus','MissionStatus']:
    df[c] = df[c].astype(str).str.strip()
df['Country']         = df['Location'].str.split(',').str[-1].str.strip()
df['Era']             = df['Launch Year'].apply(lambda y: "Space Race" if y<=1969 else "Cold War Era" if y<=1989 else "Post-Cold War" if y<=2009 else "Commercial Era" if not pd.isna(y) else "Unknown")
df['Mission Success'] = df['MissionStatus'] == 'Success'

def dark_ax(ax, fc="#0a0f1e"):
    ax.set_facecolor(fc)
    ax.tick_params(colors=MUTED, labelsize=8)
    for s in ax.spines.values(): s.set_edgecolor(ACCENT); s.set_linewidth(0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

def kpi_card(ax, value, label, sub="", sub_color=MUTED, vs=22):
    ax.set_facecolor(CARD)
    for s in ax.spines.values(): s.set_edgecolor(ACCENT); s.set_linewidth(0.8)
    ax.set_xticks([]); ax.set_yticks([])
    ax.text(0.5, 0.60, str(value), transform=ax.transAxes, ha='center', va='center',
            fontsize=vs, fontweight='bold', color=TEXT, fontfamily='monospace')
    ax.text(0.5, 0.28, label, transform=ax.transAxes, ha='center', va='center',
            fontsize=9, color=MUTED)
    if sub:
        ax.text(0.5, 0.10, sub, transform=ax.transAxes, ha='center', va='center',
                fontsize=8, color=sub_color)

total_missions = len(df)
success_rate   = round(df['Mission Success'].mean()*100, 1)
total_cost     = df['Price'].sum()
active_rockets = df[df['RocketStatus']=='Active']['Rocket'].nunique()
total_orgs     = df['Company'].nunique()
most_active    = df['Company'].value_counts().idxmax()
cost_count     = df['Price'].notna().sum()
sr_60s         = round(df[(df['Launch Year']>=1960)&(df['Launch Year']<=1969)]['Mission Success'].mean()*100,1)
sr_diff        = round(success_rate - sr_60s, 1)

# ── PAGE 1 ────────────────────────────────────────────────────────────────────
fig1 = plt.figure(figsize=(22, 14), facecolor=BG)
fig1.suptitle("Space Mission Control  ·  1957 – 2022", fontsize=22,
              fontweight='bold', color=TEXT, y=0.975, x=0.035, ha='left')
fig1.text(0.035, 0.945, f"65 Years  ·  {total_missions:,} Missions  ·  {total_orgs} Organisations",
          fontsize=10, color=MUTED, ha='left')

gs1 = gridspec.GridSpec(3, 4, figure=fig1, top=0.92, bottom=0.05,
                         left=0.04, right=0.97, hspace=0.50, wspace=0.30)

ax_k1 = fig1.add_subplot(gs1[0,0]); ax_k2 = fig1.add_subplot(gs1[0,1])
ax_k3 = fig1.add_subplot(gs1[0,2]); ax_k4 = fig1.add_subplot(gs1[0,3])
kpi_card(ax_k1, f"{total_missions:,}", "Total Missions", "1957 – 2022", MUTED)
kpi_card(ax_k2, f"{success_rate}%",    "Success Rate",   f"+{sr_diff}% vs 1960s", TEAL)
kpi_card(ax_k3, f"${total_cost:,.0f}M","Total Cost (USD M)", "Incl. missing values", AMBER)
kpi_card(ax_k4, active_rockets,        "Active Rockets",  "Still operational", TEAL)

ax_bar = fig1.add_subplot(gs1[1,:2])
dark_ax(ax_bar)
yearly = df[df['Era']!='Unknown'].groupby(['Launch Year','Era']).size().reset_index(name='Count')
years  = np.arange(int(df['Launch Year'].min()), int(df['Launch Year'].max())+1)
yi     = {y:i for i,y in enumerate(years)}
bottom = np.zeros(len(years))
for era in ERA_ORDER:
    sub = yearly[yearly['Era']==era]
    h = np.zeros(len(years))
    for _,row in sub.iterrows():
        idx = yi.get(int(row['Launch Year']))
        if idx is not None: h[idx] = row['Count']
    ax_bar.bar(years, h, bottom=bottom, color=ERA_COLORS[era], width=0.9, alpha=0.92, label=era)
    bottom += h
ax_bar.set_title("Launches Per Year (1957 – 2022)", color=TEXT, fontsize=12, pad=10, loc='left')
ax_bar.set_xlabel("Year", color=MUTED, fontsize=9)
ax_bar.set_ylabel("Mission Count", color=MUTED, fontsize=9)
ax_bar.grid(axis='y', color=ACCENT, linewidth=0.4, alpha=0.6)
ax_bar.xaxis.set_tick_params(labelcolor=MUTED)
ax_bar.yaxis.set_tick_params(labelcolor=MUTED)
ax_bar.legend(fontsize=8, framealpha=0, labelcolor=TEXT, loc='upper left', ncol=2)

ax_d = fig1.add_subplot(gs1[1,2:])
ax_d.set_facecolor(CARD)
for s in ax_d.spines.values(): s.set_edgecolor(ACCENT)
sc = df['MissionStatus'].value_counts()
dm = {'Success':TEAL,'Failure':RED,'Partial Failure':AMBER,'Prelaunch Failure':PURPLE}
dc = [dm.get(s,'#888') for s in sc.index]
wedges,_,autotexts = ax_d.pie(sc.values, labels=None, colors=dc, autopct='%1.1f%%',
                                pctdistance=0.78, startangle=90,
                                wedgeprops=dict(width=0.50, edgecolor=BG, linewidth=2))
for at in autotexts: at.set_color(TEXT); at.set_fontsize(9); at.set_fontweight('bold')
ax_d.text(0,0,f"{success_rate}%\nSuccess", ha='center', va='center',
          fontsize=13, fontweight='bold', color=TEXT, linespacing=1.4)
patches = [mpatches.Patch(color=dm.get(s,'#888'), label=s) for s in sc.index]
ax_d.legend(handles=patches, loc='lower center', ncol=2, fontsize=8,
            framealpha=0, labelcolor=TEXT, bbox_to_anchor=(0.5,-0.06))
ax_d.set_title("Mission Status Breakdown", color=TEXT, fontsize=12, pad=10)

ax_cty = fig1.add_subplot(gs1[2,:])
dark_ax(ax_cty)
cty = df['Country'].value_counts().head(12).reset_index()
cty.columns = ['Country','Count']
cc = [TEAL if i==0 else PURPLE for i in range(len(cty))]
bars_c = ax_cty.barh(cty['Country'][::-1], cty['Count'][::-1], color=cc[::-1], alpha=0.88, height=0.65)
for bar,val in zip(bars_c, cty['Count'][::-1]):
    ax_cty.text(bar.get_width()+10, bar.get_y()+bar.get_height()/2, f"{val:,}", va='center', color=TEXT, fontsize=9)
ax_cty.set_title("Missions by Country (Top 12)", color=TEXT, fontsize=12, pad=10, loc='left')
ax_cty.set_xlabel("Mission Count", color=MUTED, fontsize=9)
ax_cty.grid(axis='x', color=ACCENT, linewidth=0.4, alpha=0.6)
ax_cty.set_xlim(0, cty['Count'].max()*1.12)

plt.savefig("/mnt/user-data/outputs/page1_mission_overview.png", dpi=150, bbox_inches='tight', facecolor=BG)
print("Page 1 saved.")
plt.close()

# ── PAGE 2 ────────────────────────────────────────────────────────────────────
fig2 = plt.figure(figsize=(22, 14), facecolor=BG)
fig2.suptitle("Organisation & Cost Analysis", fontsize=22,
              fontweight='bold', color=TEXT, y=0.975, x=0.035, ha='left')
fig2.text(0.035, 0.945, "Who launched, how much it cost, and who succeeded most",
          fontsize=10, color=MUTED, ha='left')

gs2 = gridspec.GridSpec(3, 2, figure=fig2, top=0.92, bottom=0.05,
                         left=0.04, right=0.97, hspace=0.50, wspace=0.30)

gs2_kpi = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs2[0,:], wspace=0.25)
ax_k5 = fig2.add_subplot(gs2_kpi[0]); ax_k6 = fig2.add_subplot(gs2_kpi[1]); ax_k7 = fig2.add_subplot(gs2_kpi[2])
kpi_card(ax_k5, total_orgs,        "Total Organisations",    "", MUTED)
kpi_card(ax_k6, most_active,       "Most Active Organisation","", TEAL, vs=13)
kpi_card(ax_k7, f"{cost_count:,}", "Missions with Cost Data", "", MUTED)

ax_org = fig2.add_subplot(gs2[1,0])
dark_ax(ax_org)
top_orgs = df['Company'].value_counts().head(10).reset_index()
top_orgs.columns = ['Org','Count']
oc = [TEAL if o==most_active else PURPLE for o in top_orgs['Org']]
bars_o = ax_org.barh(top_orgs['Org'][::-1], top_orgs['Count'][::-1], color=oc[::-1], alpha=0.88, height=0.65)
for bar,val in zip(bars_o, top_orgs['Count'][::-1]):
    ax_org.text(bar.get_width()+5, bar.get_y()+bar.get_height()/2, f"{val:,}", va='center', color=TEXT, fontsize=9)
ax_org.set_title("Top 10 Organisations by Missions", color=TEXT, fontsize=12, pad=10, loc='left')
ax_org.set_xlabel("Mission Count", color=MUTED, fontsize=9)
ax_org.grid(axis='x', color=ACCENT, linewidth=0.4, alpha=0.6)
ax_org.set_xlim(0, top_orgs['Count'].max()*1.15)

ax_sr = fig2.add_subplot(gs2[1,1])
dark_ax(ax_sr)
top10n = top_orgs['Org'].tolist()
sr_g   = df[df['Company'].isin(top10n)].groupby('Company')['Mission Success'].mean().multiply(100).round(1).reindex(top10n).sort_values()
src    = [TEAL if v>=90 else AMBER if v>=75 else RED for v in sr_g.values]
bars_sr= ax_sr.barh(sr_g.index, sr_g.values, color=src, alpha=0.88, height=0.65)
for bar,val in zip(bars_sr, sr_g.values):
    ax_sr.text(bar.get_width()+0.4, bar.get_y()+bar.get_height()/2, f"{val}%", va='center', color=TEXT, fontsize=9)
ax_sr.set_title("Success Rate by Organisation (Top 10)", color=TEXT, fontsize=12, pad=10, loc='left')
ax_sr.set_xlabel("Success Rate %", color=MUTED, fontsize=9)
ax_sr.set_xlim(0, 115)
ax_sr.grid(axis='x', color=ACCENT, linewidth=0.4, alpha=0.6)

ax_cost = fig2.add_subplot(gs2[2,0])
dark_ax(ax_cost)
avg_cost = df.groupby('Era')['Price'].mean().reindex(ERA_ORDER).dropna()
ebc = [ERA_COLORS[e] for e in avg_cost.index]
bars_cost = ax_cost.bar(range(len(avg_cost)), avg_cost.values, color=ebc, alpha=0.88, width=0.55)
for bar,val in zip(bars_cost, avg_cost.values):
    ax_cost.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
                 f"${val:,.0f}M", ha='center', color=TEXT, fontsize=9)
ax_cost.set_xticks(range(len(avg_cost)))
ax_cost.set_xticklabels(avg_cost.index, color=MUTED, fontsize=8)
ax_cost.set_title("Avg Mission Cost by Era (USD M)", color=TEXT, fontsize=12, pad=10, loc='left')
ax_cost.set_ylabel("USD Millions", color=MUTED, fontsize=9)
ax_cost.grid(axis='y', color=ACCENT, linewidth=0.4, alpha=0.6)
ax_cost.set_ylim(0, avg_cost.max()*1.18)

ax_tbl = fig2.add_subplot(gs2[2,1])
ax_tbl.set_facecolor(CARD)
for s in ax_tbl.spines.values(): s.set_edgecolor(ACCENT)
ax_tbl.set_xticks([]); ax_tbl.set_yticks([])
ax_tbl.set_title("Top 5 Most Expensive Missions", color=TEXT, fontsize=12, pad=10)
top5 = (df[['Mission','Company','Price','MissionStatus']].dropna(subset=['Price'])
        .drop_duplicates(subset=['Mission']).nlargest(5,'Price').reset_index(drop=True))
cell_data = [[row['Mission'][:20], row['Company'][:12],
              f"${row['Price']:,.0f}M", row['MissionStatus']] for _,row in top5.iterrows()]
tbl = ax_tbl.table(cellText=cell_data, colLabels=['Mission','Organisation','Cost','Status'],
                   cellLoc='center', loc='center', bbox=[0.0,0.02,1.0,0.95])
tbl.auto_set_font_size(False); tbl.set_fontsize(8.5)
for (row,col),cell in tbl.get_celld().items():
    cell.set_edgecolor(ACCENT); cell.set_linewidth(0.5)
    if row==0:
        cell.set_facecolor(ACCENT); cell.set_text_props(color=TEXT, fontweight='bold')
    else:
        cell.set_facecolor(CARD)
        st = cell_data[row-1][3] if row<=len(cell_data) else None
        cell.set_text_props(color=TEAL if (col==3 and st=='Success') else RED if (col==3 and st=='Failure') else TEXT)

plt.savefig("/mnt/user-data/outputs/page2_org_cost_analysis.png", dpi=150, bbox_inches='tight', facecolor=BG)
print("Page 2 saved.")
plt.close()
print("Done!")
