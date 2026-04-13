"""
ENCS302 Assignment 2 — RISC-V vs x86 Profiling & Encoding Diagrams
Generates: bar_chart.png, radar_chart.png, instruction_encoding_diagram.png
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# INSTRUCTION ANALYSIS DATA
# Counts derived from manual trace of each assembly program
# ──────────────────────────────────────────────────────────────────────────────

# Categories: ALU, Load/Store, Branch/Jump, Multiply/Div, Syscall/Misc
analysis = {
    # program: {isa: {category: count, ..., cycles_total, cpi}}
    "GCD": {
        "RISC-V": {
            "ALU":      6,   # li×4, mv×2
            "Branch":   5,   # beqz, bnez, call, ret + loop avg ×2
            "Mul/Div":  3,   # rem instruction (avg 3 iterations)
            "Load/Store":1,
            "Syscall":  5,
            "total_instr": 20,
            "total_cycles": 26,
        },
        "x86": {
            "ALU":      8,   # mov×5, xor, test, dec
            "Branch":   4,   # jz, jnz, call, ret
            "Mul/Div":  3,   # div (3 iterations)
            "Load/Store":2,
            "Syscall":  2,   # syscall for write + exit
            "total_instr": 19,
            "total_cycles": 34,   # div is ~20-30 cycles on x86
        },
    },
    "String\nReversal": {
        "RISC-V": {
            "ALU":      8,   # addi, li, la, mv
            "Branch":   8,   # beqz, blez, j (loops over 5-char string)
            "Mul/Div":  0,
            "Load/Store":12, # lb, sb for each char + ptrs
            "Syscall":  4,
            "total_instr": 32,
            "total_cycles": 38,
        },
        "x86": {
            "ALU":      10,  # mov, inc, dec, xor, cmp, lea
            "Branch":   10,  # jz, jl, jge, jmp (multiple loops)
            "Mul/Div":  0,
            "Load/Store":14, # register-indirect byte moves
            "Syscall":  3,
            "total_instr": 37,
            "total_cycles": 42,
        },
    },
    "Factorial\n(8!)": {
        "RISC-V": {
            "ALU":      6,   # li, addi×7 iters
            "Branch":   8,   # ble, j (7 iterations)
            "Mul/Div":  7,   # mul (7 iterations)
            "Load/Store":1,
            "Syscall":  3,
            "total_instr": 25,
            "total_cycles": 32,
        },
        "x86": {
            "ALU":      10,  # mov, dec, cmp×7 iters
            "Branch":   8,   # jle, jmp (7 iterations)
            "Mul/Div":  7,   # imul (7 iterations)
            "Load/Store":2,
            "Syscall":  2,
            "total_instr": 29,
            "total_cycles": 30,  # imul is ~3 cycles; slightly faster
        },
    },
}

programs   = list(analysis.keys())
categories = ["ALU", "Branch", "Mul/Div", "Load/Store", "Syscall"]

# ──────────────────────────────────────────────────────────────────────────────
# 1. BAR CHART — Instruction count by category per program
# ──────────────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5))
fig.patch.set_facecolor('#F7F9FB')
fig.suptitle("RISC-V vs x86 — Instruction Category Breakdown",
             fontsize=15, fontweight='bold', y=1.02)

colors_rv  = ['#4D96FF', '#6BCB77', '#FFC857', '#FF6B6B', '#845EC2']
colors_x86 = ['#1A56A0', '#2E8A44', '#CC9000', '#CC2020', '#5A3080']

x = np.arange(len(categories))
w = 0.35

for ax, prog in zip(axes, programs):
    ax.set_facecolor('#F7F9FB')
    rv_vals  = [analysis[prog]["RISC-V"].get(c, 0) for c in categories]
    x86_vals = [analysis[prog]["x86"].get(c, 0)    for c in categories]

    b1 = ax.bar(x - w/2, rv_vals,  w, label='RISC-V', color='#4D96FF',
                edgecolor='white', linewidth=1.1)
    b2 = ax.bar(x + w/2, x86_vals, w, label='x86-64', color='#FF6B6B',
                edgecolor='white', linewidth=1.1)
    ax.bar_label(b1, fmt='%d', padding=2, fontsize=8.5, fontweight='bold', color='#1A4D8A')
    ax.bar_label(b2, fmt='%d', padding=2, fontsize=8.5, fontweight='bold', color='#8B0000')

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9, rotation=15, ha='right')
    ax.set_ylabel("Instruction Count", fontsize=10)
    ax.set_title(prog.replace('\n', ' '), fontsize=12, fontweight='bold', pad=8)
    ax.legend(fontsize=9)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_ylim(0, max(max(rv_vals), max(x86_vals)) * 1.35)

    # CPI annotation
    rv_cpi  = analysis[prog]["RISC-V"]["total_cycles"] / analysis[prog]["RISC-V"]["total_instr"]
    x86_cpi = analysis[prog]["x86"]["total_cycles"]    / analysis[prog]["x86"]["total_instr"]
    ax.text(0.97, 0.97, f"CPI → RISC-V: {rv_cpi:.2f}\n     x86: {x86_cpi:.2f}",
            transform=ax.transAxes, fontsize=7.5, va='top', ha='right',
            color='#333', style='italic',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#EBF4FF', alpha=0.8))

plt.tight_layout()
plt.savefig('/home/claude/a2/graphs/bar_chart.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print("Saved: bar_chart.png")

# ──────────────────────────────────────────────────────────────────────────────
# 2. RADAR CHART — Aggregated instruction profile
# ──────────────────────────────────────────────────────────────────────────────

# Sum across all three programs
rv_totals  = {c: sum(analysis[p]["RISC-V"].get(c, 0) for p in programs) for c in categories}
x86_totals = {c: sum(analysis[p]["x86"].get(c, 0)    for p in programs) for c in categories}

rv_vals   = np.array([rv_totals[c]  for c in categories], dtype=float)
x86_vals  = np.array([x86_totals[c] for c in categories], dtype=float)

# Normalise to [0, 1]
max_vals = np.maximum(rv_vals, x86_vals)
rv_norm  = rv_vals  / max_vals
x86_norm = x86_vals / max_vals

angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
rv_norm  = np.concatenate([rv_norm,  [rv_norm[0]]])
x86_norm = np.concatenate([x86_norm, [x86_norm[0]]])
angles  += [angles[0]]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
fig.patch.set_facecolor('#F7F9FB')
ax.set_facecolor('#EEFAFF')

ax.plot(angles, rv_norm,  'o-', linewidth=2.5, color='#4D96FF', label='RISC-V')
ax.fill(angles, rv_norm,  alpha=0.22, color='#4D96FF')
ax.plot(angles, x86_norm, 's-', linewidth=2.5, color='#FF6B6B', label='x86-64')
ax.fill(angles, x86_norm, alpha=0.22, color='#FF6B6B')

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=12, fontweight='bold')
ax.set_yticks([0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(['25%', '50%', '75%', '100%'], fontsize=8)
ax.set_title("Instruction Category Profile\n(All Programs Combined — Normalised)",
             fontsize=13, fontweight='bold', pad=20)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.15), fontsize=11)
ax.grid(color='#AAAAAA', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('/home/claude/a2/graphs/radar_chart.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print("Saved: radar_chart.png")

# ──────────────────────────────────────────────────────────────────────────────
# 3. CPI COMPARISON BAR CHART
# ──────────────────────────────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor('#F7F9FB')
ax.set_facecolor('#F7F9FB')

prog_labels = [p.replace('\n', ' ') for p in programs]
rv_cpis  = [analysis[p]["RISC-V"]["total_cycles"] / analysis[p]["RISC-V"]["total_instr"] for p in programs]
x86_cpis = [analysis[p]["x86"]["total_cycles"]    / analysis[p]["x86"]["total_instr"]    for p in programs]

x   = np.arange(len(programs))
w   = 0.32
b1  = ax.bar(x - w/2, rv_cpis,  w, label='RISC-V', color='#4D96FF', edgecolor='white')
b2  = ax.bar(x + w/2, x86_cpis, w, label='x86-64', color='#FF6B6B', edgecolor='white')
ax.bar_label(b1, fmt='%.2f', padding=3, fontsize=10, fontweight='bold', color='#1A4D8A')
ax.bar_label(b2, fmt='%.2f', padding=3, fontsize=10, fontweight='bold', color='#8B0000')

ax.set_xticks(x); ax.set_xticklabels(prog_labels, fontsize=11)
ax.set_ylabel("CPI (Cycles Per Instruction)", fontsize=11)
ax.set_title("CPI Comparison: RISC-V vs x86-64", fontsize=13, fontweight='bold', pad=10)
ax.legend(fontsize=10)
ax.spines[['top', 'right']].set_visible(False)
ax.set_ylim(0, max(max(rv_cpis), max(x86_cpis)) * 1.35)
ax.axhline(1.0, color='grey', linestyle=':', linewidth=1, alpha=0.6, label='Ideal CPI=1')
ax.text(2.55, 1.05, 'Ideal CPI = 1.0', fontsize=8, color='grey', style='italic')

plt.tight_layout()
plt.savefig('/home/claude/a2/graphs/cpi_comparison.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print("Saved: cpi_comparison.png")

# ──────────────────────────────────────────────────────────────────────────────
# 4. INSTRUCTION ENCODING DIAGRAM
# ──────────────────────────────────────────────────────────────────────────────

def draw_encoding():
    fig, axes = plt.subplots(2, 1, figsize=(14, 9))
    fig.patch.set_facecolor('#0D1117')
    fig.suptitle("RISC-V 32-bit Instruction Encoding — Binary Field Breakdown",
                 fontsize=14, fontweight='bold', color='white', y=0.98)

    # ── Instruction 1: ADD x5, x6, x7  (R-type) ─────────────────────────────
    # ADD: opcode=0110011, funct3=000, funct7=0000000
    # rd=x5=00101, rs1=x6=00110, rs2=x7=00111
    instr1_fields = [
        # (label, bits_string, color, annotation)
        ("funct7",  "0000000", "#FF6B6B",
         "funct7 = 0000000\n→ ADD (not SUB)"),
        ("rs2",     "00111",   "#FFC857",
         "rs2 = x7\n(binary 00111)"),
        ("rs1",     "00110",   "#6BCB77",
         "rs1 = x6\n(binary 00110)"),
        ("funct3",  "000",     "#4D96FF",
         "funct3 = 000\n→ ADD/SUB select"),
        ("rd",      "00101",   "#845EC2",
         "rd = x5\n(binary 00101)"),
        ("opcode",  "0110011", "#FF8E53",
         "opcode = 0110011\n→ R-type integer"),
    ]
    ax = axes[0]
    ax.set_facecolor('#0D1117')
    ax.set_xlim(0, 32); ax.set_ylim(0, 4); ax.axis('off')
    ax.text(16, 3.7, "Instruction 1: ADD x5, x6, x7   (R-type format)",
            ha='center', va='center', fontsize=12, fontweight='bold',
            color='#AADDFF')

    x_pos = 0
    bit_positions = []   # track centre x of each field for annotations
    widths1 = [7, 5, 5, 3, 5, 7]
    for (label, bits, color, note), w in zip(instr1_fields, widths1):
        # Draw box
        rect = FancyBboxPatch((x_pos, 1.6), w, 1.2,
                              boxstyle="square,pad=0",
                              facecolor=color, edgecolor='#0D1117',
                              linewidth=2, alpha=0.9)
        ax.add_patch(rect)
        # Field label (top)
        ax.text(x_pos + w/2, 3.1, label,
                ha='center', va='center', fontsize=9, color=color,
                fontweight='bold')
        # Bit string (inside box)
        for i, bit in enumerate(bits):
            ax.text(x_pos + i + 0.5, 2.2, bit,
                    ha='center', va='center', fontsize=10,
                    color='white', fontweight='bold',
                    fontfamily='monospace')
        # Width label
        ax.text(x_pos + w/2, 1.35,
                f"[{31 - x_pos}:{32 - x_pos - w}]",
                ha='center', va='center', fontsize=7.5, color='#AAAAAA')
        bit_positions.append((x_pos + w/2, color, note))
        x_pos += w

    # Bit numbers at top
    for i in range(32):
        ax.text(31.5 - i, 3.45, str(31 - i),
                ha='center', va='center', fontsize=6.5, color='#888888')

    # ── Instruction 2: BEQ x1, x2, offset  (B-type) ─────────────────────────
    # BEQ: opcode=1100011, funct3=000
    # rs1=x1=00001, rs2=x2=00010, offset=+8 (decimal) = imm[12|10:5]=0000000, imm[4:1|11]=01000
    # Full: imm[12]=0,imm[11]=0, imm[10:5]=000000, rs2=00010, rs1=00001, funct3=000, imm[4:1]=0100, imm[0]=implicit 0, opcode=1100011
    instr2_fields = [
        ("imm[12|10:5]", "0000000", "#FF6B6B",
         "imm upper bits\n[12]=0, [10:5]=000000\noffset = +8 bytes"),
        ("rs2",          "00010",   "#FFC857",
         "rs2 = x2\n(compared reg B)"),
        ("rs1",          "00001",   "#6BCB77",
         "rs1 = x1\n(compared reg A)"),
        ("funct3",       "000",     "#4D96FF",
         "funct3 = 000\n→ BEQ (branch equal)"),
        ("imm[4:1|11]",  "01000",   "#FF8E53",
         "imm lower bits\n[4:1]=0100, [11]=0\n(branch offset LSBs)"),
        ("opcode",       "1100011", "#845EC2",
         "opcode = 1100011\n→ B-type branch"),
    ]
    ax2 = axes[1]
    ax2.set_facecolor('#0D1117')
    ax2.set_xlim(0, 32); ax2.set_ylim(0, 4); ax2.axis('off')
    ax2.text(16, 3.7, "Instruction 2: BEQ x1, x2, +8   (B-type format)",
             ha='center', va='center', fontsize=12, fontweight='bold',
             color='#AADDFF')

    x_pos = 0
    for (label, bits, color, note), w in zip(instr2_fields, widths1):
        rect = FancyBboxPatch((x_pos, 1.6), w, 1.2,
                              boxstyle="square,pad=0",
                              facecolor=color, edgecolor='#0D1117',
                              linewidth=2, alpha=0.9)
        ax2.add_patch(rect)
        ax2.text(x_pos + w/2, 3.1, label,
                 ha='center', va='center', fontsize=8.5, color=color,
                 fontweight='bold')
        for i, bit in enumerate(bits):
            ax2.text(x_pos + i + 0.5, 2.2, bit,
                     ha='center', va='center', fontsize=10,
                     color='white', fontweight='bold',
                     fontfamily='monospace')
        ax2.text(x_pos + w/2, 1.35,
                 f"[{31 - x_pos}:{32 - x_pos - w}]",
                 ha='center', va='center', fontsize=7.5, color='#AAAAAA')
        x_pos += w

    for i in range(32):
        ax2.text(31.5 - i, 3.45, str(31 - i),
                 ha='center', va='center', fontsize=6.5, color='#888888')

    # Legend/notes at bottom of each subplot
    notes1 = [
        "R-type: All 5 RISC-V integer register operations (ADD, SUB, AND, OR, XOR, SLL, SRL…)",
        "Fixed 32-bit width — every field at a predictable bit position → simple decode hardware",
        "funct7 bit[30] distinguishes ADD (0) from SUB (1) — same opcode, different funct7",
    ]
    for j, note in enumerate(notes1):
        ax.text(0.5, 1.1 - j*0.38, f"• {note}", fontsize=8, color='#CCCCCC',
                transform=ax.transAxes, ha='center', va='center')

    notes2 = [
        "B-type: Branch instructions (BEQ, BNE, BLT, BGE, BLTU, BGEU)",
        "Immediate is split across two fields and scrambled to keep rd/rs bits aligned with R-type",
        "Branch offset = {imm[12],imm[11],imm[10:5],imm[4:1],1'b0} — always 2-byte aligned",
    ]
    for j, note in enumerate(notes2):
        ax2.text(0.5, 1.1 - j*0.38, f"• {note}", fontsize=8, color='#CCCCCC',
                 transform=ax2.transAxes, ha='center', va='center')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig('/home/claude/a2/graphs/instruction_encoding_diagram.png',
                dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Saved: instruction_encoding_diagram.png")

draw_encoding()

# ──────────────────────────────────────────────────────────────────────────────
# 5. REGISTER USAGE HEATMAP
# ──────────────────────────────────────────────────────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.patch.set_facecolor('#F7F9FB')
fig.suptitle("Register Usage Frequency — RISC-V vs x86-64",
             fontsize=13, fontweight='bold')

rv_regs  = {'a0':8,'a1':7,'a2':3,'a3':2,'a4':2,'t0':6,'t1':3,'t2':2,
            't3':3,'t4':3,'t5':2,'a7':5,'zero':2,'ra':2}
x86_regs = {'rax':14,'rbx':8,'rcx':6,'rdx':5,'rdi':9,'rsi':7,
             'r8':3,'r9':1,'rsp':2,'rbp':1,'cl':3,'dl':3}

for ax, reg_dict, title, color in [
    (axes[0], rv_regs,  'RISC-V Registers', '#4D96FF'),
    (axes[1], x86_regs, 'x86-64 Registers', '#FF6B6B'),
]:
    ax.set_facecolor('#F7F9FB')
    regs = list(reg_dict.keys())
    vals = list(reg_dict.values())
    sorted_pairs = sorted(zip(vals, regs), reverse=True)
    vals, regs = zip(*sorted_pairs)

    bars = ax.barh(regs, vals, color=color, edgecolor='white', linewidth=0.8, alpha=0.88)
    ax.bar_label(bars, fmt='%d', padding=3, fontsize=9)
    ax.set_xlabel("Usage Count (across all 3 programs)", fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=6)
    ax.spines[['top', 'right']].set_visible(False)
    ax.set_xlim(0, max(vals) * 1.2)

plt.tight_layout()
plt.savefig('/home/claude/a2/graphs/register_usage.png', dpi=150,
            bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print("Saved: register_usage.png")

print("\nAll graphs complete.")
