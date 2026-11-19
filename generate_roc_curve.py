"""
generate_roc_curve.py
Interactive GUI and script to generate publication-grade multi-class ROC curves
matching the EXACT style, pixel layout, colors, and step functions of the reference image:
- Canvas Resolution: 1024 x 950 px
- Title: "ROC Curve -- Out-of-Fold Predictions, 5-Fold CV"
- Palette:
    - Normal (Green):     #2e7d32 (AUC=0.974)
    - Warning (Amber):    #f9a825 (AUC=0.718)
    - Critical (Crimson): #c62828 (AUC=0.979)
    - Chance (Dotted):    #000000 (0.500)
- Dialog box: Built-in native Tkinter UI to input custom values or generate the exact reference graph.
"""

import os
import sys
import json
import zlib
import base64
import argparse
import numpy as np
import matplotlib.pyplot as plt

# Embedded exact reference coordinates extracted pixel-for-pixel from the reference plot
_EMBEDDED_REFERENCE_B64 = """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"""

def get_exact_reference_curves():
    raw_json = zlib.decompress(base64.b64decode(_EMBEDDED_REFERENCE_B64.strip())).decode('utf-8')
    data = json.loads(raw_json)
    
    gx = np.array([p[0] for p in data['green']])
    gy = np.maximum.accumulate(np.clip([p[1] for p in data['green']], 0.0, 1.0))
    
    ox = np.array([p[0] for p in data['orange']])
    oy = np.maximum.accumulate(np.clip([p[1] for p in data['orange']], 0.0, 1.0))
    
    rx = np.array([p[0] for p in data['red']])
    ry = np.maximum.accumulate(np.clip([p[1] for p in data['red']], 0.0, 1.0))
    
    return {
        'Normal': {'fpr': gx, 'tpr': gy, 'auc': 0.974},
        'Warning': {'fpr': ox, 'tpr': oy, 'auc': 0.718},
        'Critical': {'fpr': rx, 'tpr': ry, 'auc': 0.979}
    }

def morph_curve_to_target_auc(xs, ys, base_auc, target_auc):
    """
    Monotonically transforms the step curve to precisely meet target_auc
    while preserving authentic staircase out-of-fold characteristics.
    """
    target_auc = max(0.50, min(0.999, float(target_auc)))
    if abs(target_auc - base_auc) < 0.001:
        return xs, ys
    
    low, high = 0.01, 60.0
    for _ in range(35):
        mid = (low + high) / 2.0
        candidate_ys = np.maximum.accumulate(np.clip(ys ** mid, 0.0, 1.0))
        computed_auc = np.trapezoid(candidate_ys, xs)
        if computed_auc < target_auc:
            high = mid
        else:
            low = mid
            
    final_p = (low + high) / 2.0
    return xs, np.maximum.accumulate(np.clip(ys ** final_p, 0.0, 1.0))

def plot_roc_curve(
    normal_auc: float = 0.974,
    warning_auc: float = 0.718,
    critical_auc: float = 0.979,
    title: str = "ROC Curve -- Out-of-Fold Predictions, 5-Fold CV",
    save_path: str = "results/roc_curve_output.png",
    show_plot: bool = False
):
    """
    Renders the exact ROC plot matching the reference image layout, font metrics, and colors.
    """
    ref = get_exact_reference_curves()
    
    # Check if exact reference values
    if abs(normal_auc - 0.974) < 0.001:
        gx, gy = ref['Normal']['fpr'], ref['Normal']['tpr']
    else:
        gx, gy = morph_curve_to_target_auc(ref['Normal']['fpr'], ref['Normal']['tpr'], 0.974, normal_auc)
        
    if abs(warning_auc - 0.718) < 0.001:
        ox, oy = ref['Warning']['fpr'], ref['Warning']['tpr']
    else:
        ox, oy = morph_curve_to_target_auc(ref['Warning']['fpr'], ref['Warning']['tpr'], 0.718, warning_auc)
        
    if abs(critical_auc - 0.979) < 0.001:
        rx, ry = ref['Critical']['fpr'], ref['Critical']['tpr']
    else:
        rx, ry = morph_curve_to_target_auc(ref['Critical']['fpr'], ref['Critical']['tpr'], 0.979, critical_auc)

    # Use standard sans-serif font
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
    plt.rcParams['font.family'] = 'sans-serif'

    # Pixel-accurate canvas: exactly 1024 x 950 px at 100 dpi
    fig = plt.figure(figsize=(10.24, 9.5), dpi=100)
    
    # Exact axes bounding box in canvas coordinates:
    # row 54 to 865 (811 px high), col 96 to 1002 (906 px wide)
    ax = fig.add_axes([96.0 / 1024.0, (950.0 - 865.0) / 950.0, 906.0 / 1024.0, 811.0 / 950.0])

    # Light gray background grid matching reference
    ax.grid(True, color='#ebebeb', linestyle='-', linewidth=0.8)
    ax.set_axisbelow(True)

    # Plot curves with exact colors and line widths
    p_green, = ax.plot(gx, gy, color='#2e7d32', linewidth=2.3, label=f'Normal (AUC={normal_auc:.3f})')
    p_orange, = ax.plot(ox, oy, color='#f9a825', linewidth=2.3, label=f'Warning (AUC={warning_auc:.3f})')
    p_red, = ax.plot(rx, ry, color='#c62828', linewidth=2.3, label=f'Critical (AUC={critical_auc:.3f})')
    p_chance, = ax.plot([0, 1], [0, 1], color='#000000', linestyle=':', linewidth=1.1, label='Chance (0.500)')

    # Axis limits
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)

    # Title & Labels
    ax.set_title(title, fontsize=13, pad=11)
    ax.set_xlabel('False Positive Rate', fontsize=11, labelpad=9)
    ax.set_ylabel('True Positive Rate', fontsize=11, labelpad=9)
    
    # Ticks
    ax.tick_params(direction='out', length=5, width=1.0, labelsize=10.5)

    # Legend in lower right corner
    leg = ax.legend(
        handles=[p_green, p_orange, p_red, p_chance],
        loc='lower right',
        frameon=True,
        edgecolor='#d0d0d0',
        fontsize=10.5,
        borderpad=0.6,
        handletextpad=0.8,
        labelspacing=0.5
    )
    leg.get_frame().set_alpha(1.0)
    leg.get_frame().set_facecolor('#ffffff')

    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    fig.savefig(save_path, dpi=100)
    print(f'[SUCCESS] ROC Curve saved to: {os.path.abspath(save_path)}')

    if show_plot:
        plt.show()
    plt.close(fig)
    return save_path

def open_dialog():
    """
    Native Tkinter dialog box for user input and instantaneous graph generation.
    """
    import tkinter as tk
    from tkinter import messagebox, filedialog

    root = tk.Tk()
    root.title("ProfessorMode -- ROC Curve Generator")
    root.geometry("560x600")
    root.resizable(False, False)
    root.configure(bg="#f8fafc")

    # Header
    header = tk.Frame(root, bg="#0f172a", padx=22, pady=16)
    header.pack(fill="x")
    tk.Label(
        header, text="ROC Curve Generator Studio",
        font=("Segoe UI", 13, "bold"), fg="#f8fafc", bg="#0f172a"
    ).pack(anchor="w")
    tk.Label(
        header, text="Pixel-perfect reproduction of 5-Fold Cross Validation ROC Curves",
        font=("Segoe UI", 9), fg="#94a3b8", bg="#0f172a"
    ).pack(anchor="w")

    # Content
    body = tk.Frame(root, bg="#f8fafc", padx=24, pady=16)
    body.pack(fill="both", expand=True)

    # Title field
    tk.Label(body, text="Graph Title:", font=("Segoe UI", 9, "bold"), fg="#1e293b", bg="#f8fafc").pack(anchor="w")
    ent_title = tk.Entry(body, font=("Segoe UI", 10), bg="#ffffff", relief="solid", bd=1)
    ent_title.insert(0, "ROC Curve -- Out-of-Fold Predictions, 5-Fold CV")
    ent_title.pack(fill="x", pady=(3, 14), ipady=3)

    # AUC Values
    tk.Label(body, text="Class AUC Benchmark Values (Scale: 0.500 - 1.000):", font=("Segoe UI", 9, "bold"), fg="#1e293b", bg="#f8fafc").pack(anchor="w")

    classes = [
        ("Normal", "0.974", "#2e7d32", "Forest Green"),
        ("Warning", "0.718", "#f9a825", "Golden Amber"),
        ("Critical", "0.979", "#c62828", "Crimson Red")
    ]
    entries = {}

    for name, default_val, color, color_desc in classes:
        row = tk.Frame(body, bg="#ffffff", padx=12, pady=7, relief="solid", bd=1)
        row.pack(fill="x", pady=4)

        swatch = tk.Label(row, bg=color, width=2, height=1)
        swatch.pack(side="left", padx=(0, 10))

        tk.Label(
            row, text=f"{name} ({color_desc}):",
            font=("Segoe UI", 9, "bold"), fg="#1e293b", bg="#ffffff", width=24, anchor="w"
        ).pack(side="left")

        e = tk.Entry(row, font=("Segoe UI", 10, "bold"), justify="center", width=10, relief="solid", bd=1)
        e.insert(0, default_val)
        e.pack(side="right", ipady=2)
        entries[name] = e

    # Destination path
    tk.Label(body, text="Save Output Path:", font=("Segoe UI", 9, "bold"), fg="#1e293b", bg="#f8fafc").pack(anchor="w", pady=(14, 2))
    p_frame = tk.Frame(body, bg="#f8fafc")
    p_frame.pack(fill="x", pady=(0, 15))

    ent_dest = tk.Entry(p_frame, font=("Segoe UI", 9), bg="#ffffff", relief="solid", bd=1)
    ent_dest.insert(0, "results/roc_curve_output.png")
    ent_dest.pack(side="left", fill="x", expand=True, ipady=3)

    def browse():
        fn = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("All Files", "*.*")],
            initialfile="roc_curve_output.png"
        )
        if fn:
            ent_dest.delete(0, tk.END)
            ent_dest.insert(0, fn)

    tk.Button(p_frame, text="Browse...", font=("Segoe UI", 8), command=browse).pack(side="right", padx=(6, 0))

    def reset():
        ent_title.delete(0, tk.END)
        ent_title.insert(0, "ROC Curve -- Out-of-Fold Predictions, 5-Fold CV")
        entries["Normal"].delete(0, tk.END)
        entries["Normal"].insert(0, "0.974")
        entries["Warning"].delete(0, tk.END)
        entries["Warning"].insert(0, "0.718")
        entries["Critical"].delete(0, tk.END)
        entries["Critical"].insert(0, "0.979")
        ent_dest.delete(0, tk.END)
        ent_dest.insert(0, "results/roc_curve_output.png")

    def generate(preview=False):
        t = ent_title.get().strip() or "ROC Curve -- Out-of-Fold Predictions, 5-Fold CV"
        dest = ent_dest.get().strip() or "results/roc_curve_output.png"
        try:
            val_n = float(entries["Normal"].get().strip())
            val_w = float(entries["Warning"].get().strip())
            val_c = float(entries["Critical"].get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for all AUC fields.")
            return

        try:
            out = plot_roc_curve(
                normal_auc=val_n,
                warning_auc=val_w,
                critical_auc=val_c,
                title=t,
                save_path=dest,
                show_plot=preview
            )
            if not preview:
                messagebox.showinfo("Success", f"ROC Curve generated successfully!\n\nSaved to:\n{os.path.abspath(out)}")
        except Exception as ex:
            messagebox.showerror("Error", f"Failed to generate graph:\n{ex}")

    # Bottom action buttons
    foot = tk.Frame(root, bg="#f1f5f9", padx=20, pady=14, relief="groove", bd=1)
    foot.pack(fill="x", side="bottom")

    tk.Button(foot, text="Reset Defaults", font=("Segoe UI", 9), command=reset).pack(side="left")

    tk.Button(
        foot, text="Preview Graph", font=("Segoe UI", 9, "bold"),
        bg="#334155", fg="#ffffff", padx=10, command=lambda: generate(preview=True)
    ).pack(side="right", padx=(8, 0))

    tk.Button(
        foot, text="Generate & Save PNG", font=("Segoe UI", 9, "bold"),
        bg="#0f172a", fg="#ffffff", padx=14, command=lambda: generate(preview=False)
    ).pack(side="right")

    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Generate exact pixel-perfect publication ROC curves.")
    parser.add_argument("--gui", action="store_true", help="Launch native Tkinter GUI dialog box.")
    parser.add_argument("--out", type=str, default="results/roc_curve_output.png", help="Output file path.")
    parser.add_argument("--normal", type=float, default=0.974, help="Normal AUC")
    parser.add_argument("--warning", type=float, default=0.718, help="Warning AUC")
    parser.add_argument("--critical", type=float, default=0.979, help="Critical AUC")
    parser.add_argument("--title", type=str, default="ROC Curve -- Out-of-Fold Predictions, 5-Fold CV", help="Title")
    args = parser.parse_args()

    # Always generate the output image
    plot_roc_curve(
        normal_auc=args.normal,
        warning_auc=args.warning,
        critical_auc=args.critical,
        title=args.title,
        save_path=args.out
    )

    if args.gui or (len(sys.argv) == 1 and sys.stdin.isatty()):
        open_dialog()

if __name__ == '__main__':
    main()
