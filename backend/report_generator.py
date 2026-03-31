# report_generator.py
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid threading issues
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import numpy as np

def generate_csv(output_path, analysis_data):
    # Create a more organized CSV with better formatting
    df = pd.DataFrame({
        "Filename": analysis_data["metric_data"]["Filename"],
        "Temperature (°C)": [f"{t:.1f}" for t in analysis_data["metric_data"]["Temperature"]],
        "Mean": [f"{v:.6f}" for v in analysis_data["metric_data"]["Mean"]],
        "Std_Deviation": [f"{v:.6f}" for v in analysis_data["metric_data"]["Std Deviation"]],
        "RMS": [f"{v:.6f}" for v in analysis_data["metric_data"]["RMS"]],
        "Entropy": [f"{v:.6f}" for v in analysis_data["metric_data"]["Entropy"]],
        "Contrast": [f"{v:.6f}" for v in analysis_data["metric_data"]["Contrast"]],
        "Energy": [f"{v:.2f}" for v in analysis_data["metric_data"]["Energy"]],
        "Transmittance": [f"{v:.6f}" for v in analysis_data["metric_data"]["Transmittance"]],
        "Absorption_Coefficient": [f"{v:.6f}" for v in analysis_data["metric_data"]["Absorption_Coefficient"]],
        "Refractive_Index": [f"{v:.6f}" for v in analysis_data["metric_data"]["Refractive_Index"]],
        "Birefringence": [f"{v:.6f}" for v in analysis_data["metric_data"]["Birefringence"]]
    })
    
    # Add summary information at the top
    from datetime import datetime
    
    summary_lines = [
        f"Liquid Crystal Phase Analysis Report",
        f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        f"Total Images Analyzed: {len(analysis_data['metric_data']['Temperature'])}",
        f"Temperature Range: {min(analysis_data['metric_data']['Temperature']):.1f}°C - {max(analysis_data['metric_data']['Temperature']):.1f}°C",
        f"Phase Transitions Detected: {len(analysis_data['transitions'])}",
        ""
    ]
    
    # Write summary to CSV
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        for line in summary_lines:
            f.write(line + '\n')
        
        # Write the data
        df.to_csv(f, index=False)
    
    # Add transition information at the end
    with open(output_path, 'a', newline='', encoding='utf-8') as f:
        f.write('\n')
        f.write('Detected Phase Transitions:\n')
        for label, temp in analysis_data['transitions'].items():
            f.write(f"{temp:.1f}°C → {label}\n")

def generate_pdf(output_path, analysis_data):
    temps = analysis_data["metric_data"]["Temperature"]
    transitions = analysis_data["transitions"]
    filenames = analysis_data["metric_data"]["Filename"]

    # Sort data by temperature for better visualization
    sorted_indices = np.argsort(temps)[::-1]  # Sort in descending order
    temps_sorted = [temps[i] for i in sorted_indices]
    
    metrics = [
        ("Mean", [analysis_data["metric_data"]["Mean"][i] for i in sorted_indices], "#1f77b4"),
        ("Std Deviation", [analysis_data["metric_data"]["Std Deviation"][i] for i in sorted_indices], "#2ca02c"),
        ("RMS", [analysis_data["metric_data"]["RMS"][i] for i in sorted_indices], "#ff7f0e"),
        ("Entropy", [analysis_data["metric_data"]["Entropy"][i] for i in sorted_indices], "#d62728"),
        ("Contrast", [analysis_data["metric_data"]["Contrast"][i] for i in sorted_indices], "#9467bd"),
        ("Energy", [analysis_data["metric_data"]["Energy"][i] for i in sorted_indices], "#17becf"),
        ("Transmittance", [analysis_data["metric_data"]["Transmittance"][i] for i in sorted_indices], "#8c564b"),
        ("Absorption Coefficient", [analysis_data["metric_data"]["Absorption_Coefficient"][i] for i in sorted_indices], "#e377c2"),
        ("Refractive Index", [analysis_data["metric_data"]["Refractive_Index"][i] for i in sorted_indices], "#7f7f7f"),
        ("Birefringence", [analysis_data["metric_data"]["Birefringence"][i] for i in sorted_indices], "#bcbd22"),
    ]

    with PdfPages(output_path) as pdf:
        # Title page
        fig, ax = plt.subplots(figsize=(11, 8.5))
        ax.axis('off')
        
        # Title
        ax.text(0.5, 0.9, "Liquid Crystal Phase Analysis Report", 
                fontsize=24, fontweight='bold', ha='center', va='center',
                transform=ax.transAxes, color='#2c3e50')
        
        # Subtitle
        ax.text(0.5, 0.8, "CNN-Based Deep Learning Analysis", 
                fontsize=16, ha='center', va='center',
                transform=ax.transAxes, color='#7f8c8d')
        
        # Analysis summary
        ax.text(0.1, 0.6, "Analysis Summary:", fontsize=14, fontweight='bold',
                transform=ax.transAxes, color='#2c3e50')
        
        y_pos = 0.55
        ax.text(0.15, y_pos, f"• Total Images Analyzed: {len(temps)}", 
                fontsize=12, transform=ax.transAxes, color='#34495e')
        y_pos -= 0.05
        ax.text(0.15, y_pos, f"• Temperature Range: {min(temps):.1f}°C - {max(temps):.1f}°C", 
                fontsize=12, transform=ax.transAxes, color='#34495e')
        y_pos -= 0.05
        ax.text(0.15, y_pos, f"• Phase Transitions Detected: {len(transitions)}", 
                fontsize=12, transform=ax.transAxes, color='#34495e')
        y_pos -= 0.05
        ax.text(0.15, y_pos, f"• Data Points: {len(temps_sorted)} temperature points", 
                fontsize=12, transform=ax.transAxes, color='#34495e')
        
        # Detected transitions
        if transitions:
            ax.text(0.1, 0.4, "Detected Phase Transitions:", fontsize=14, fontweight='bold',
                    transform=ax.transAxes, color='#2c3e50')
            
            y_pos = 0.35
            for i, (label, temp) in enumerate(transitions.items()):
                ax.text(0.15, y_pos, f"• {temp:.1f}°C → {label}", 
                        fontsize=12, transform=ax.transAxes, color='#27ae60')
                y_pos -= 0.05
        
        # Generated date
        from datetime import datetime
        ax.text(0.5, 0.1, f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                fontsize=10, ha='center', va='center',
                transform=ax.transAxes, color='#95a5a6', style='italic')
        
        pdf.savefig(fig)
        plt.close()

        # Data table page - Split into multiple pages if needed
        rows_per_page = 15
        total_rows = len(temps_sorted)
        num_pages = (total_rows + rows_per_page - 1) // rows_per_page
        
        for page in range(num_pages):
            start_idx = page * rows_per_page
            end_idx = min((page + 1) * rows_per_page, total_rows)
            
            fig, ax = plt.subplots(figsize=(12, 10))
            ax.axis('off')
            
            # Table title
            ax.text(0.5, 0.95, f"Detailed Analysis Results (Page {page + 1}/{num_pages})", 
                    fontsize=16, fontweight='bold', ha='center', va='center',
                    transform=ax.transAxes, color='#2c3e50')
            
            # Create clean data table for this page
            page_temps = temps_sorted[start_idx:end_idx]
            page_filenames = [filenames[sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_means = [analysis_data["metric_data"]["Mean"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_stds = [analysis_data["metric_data"]["Std Deviation"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_rms = [analysis_data["metric_data"]["RMS"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_entropy = [analysis_data["metric_data"]["Entropy"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_contrast = [analysis_data["metric_data"]["Contrast"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_energy = [analysis_data["metric_data"]["Energy"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_transmittance = [analysis_data["metric_data"]["Transmittance"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_absorption = [analysis_data["metric_data"]["Absorption_Coefficient"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_refractive = [analysis_data["metric_data"]["Refractive_Index"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            page_birefringence = [analysis_data["metric_data"]["Birefringence"][sorted_indices[i]] for i in range(start_idx, end_idx)]
            
            df = pd.DataFrame({
                "Temp (°C)": [f"{t:.1f}" for t in page_temps],
                "Filename": [f.split('.')[0][:20] for f in page_filenames],  # Truncate long names
                "Mean": [f"{v:.4f}" for v in page_means],
                "Std Dev": [f"{v:.4f}" for v in page_stds],
                "RMS": [f"{v:.4f}" for v in page_rms],
                "Entropy": [f"{v:.4f}" for v in page_entropy],
                "Contrast": [f"{v:.4f}" for v in page_contrast],
                "Energy": [f"{v:.2f}" for v in page_energy],
                "Trans": [f"{v:.4f}" for v in page_transmittance],
                "Abs Coeff": [f"{v:.4f}" for v in page_absorption],
                "Ref Index": [f"{v:.4f}" for v in page_refractive],
                "Biref": [f"{v:.4f}" for v in page_birefringence]
            })
            
            # Create table with better formatting
            table = ax.table(cellText=df.values,
                            colLabels=df.columns,
                            loc='center',
                            cellLoc='center',
                            bbox=[0.05, 0.05, 0.9, 0.85])
            
            # Style the table
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 2.5)
            
            # Color header row
            for i in range(len(df.columns)):
                table[(0, i)].set_facecolor('#3498db')
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            # Color alternating rows
            for i in range(1, len(df) + 1):
                for j in range(len(df.columns)):
                    if i % 2 == 0:
                        table[(i, j)].set_facecolor('#f8f9fa')
                    else:
                        table[(i, j)].set_facecolor('#ffffff')
            
            pdf.savefig(fig)
            plt.close()

        # Individual metric plots with improved accuracy
        for label, values, color in metrics:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Plot data with proper temperature ordering
            ax.plot(temps_sorted, values, marker='o', color=color, linewidth=2, markersize=6, alpha=0.8)
            
            # Add transition lines
            for phase, temp in transitions.items():
                ax.axvline(x=temp, color='#e74c3c', linestyle='--', linewidth=2, alpha=0.7)
                ax.text(temp + 0.5, max(values) * 0.95, f"{temp:.1f}°C\n{phase}", 
                       rotation=0, fontsize=10, color='#e74c3c', fontweight='bold',
                       ha='center', va='top', bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
            
            # Styling
            ax.set_title(f"{label} vs Temperature", fontsize=16, fontweight='bold', pad=20, color='#2c3e50')
            ax.set_xlabel("Temperature (°C)", fontsize=14, color='#34495e')
            ax.set_ylabel(label, fontsize=14, color='#34495e')
            
            # Set proper temperature range and ticks
            temp_min, temp_max = min(temps_sorted), max(temps_sorted)
            ax.set_xlim(temp_max + 2, temp_min - 2)  # Add padding
            
            # Create custom tick labels for better readability
            tick_positions = np.linspace(temp_max, temp_min, 8)
            tick_labels = [f"{t:.1f}°C" for t in tick_positions]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            # Add grid for better readability
            ax.grid(True, alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Add some padding and improve readability
            ax.margins(x=0.05, y=0.1)
            
            # Add temperature range info
            ax.text(0.02, 0.95, f'Temp Range: {temp_min:.1f}°C - {temp_max:.1f}°C', 
                   transform=ax.transAxes, fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.8))
            
            # Add statistics
            mean_val = np.mean(values)
            std_val = np.std(values)
            ax.text(0.02, 0.85, f'Mean: {mean_val:.4f}\nStd: {std_val:.4f}', 
                   transform=ax.transAxes, fontsize=10, verticalalignment='top',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgray', alpha=0.8))
            
            pdf.savefig(fig)
            plt.close()

        # Summary page with all metrics in a grid
        fig, axes = plt.subplots(3, 4, figsize=(20, 15))
        axes = axes.flatten()
        
        for i, (label, values, color) in enumerate(metrics):
            ax = axes[i]
            ax.plot(temps_sorted, values, marker='o', color=color, linewidth=2, markersize=4, alpha=0.8)
            
            # Add transition lines
            for phase, temp in transitions.items():
                ax.axvline(x=temp, color='#e74c3c', linestyle='--', linewidth=1, alpha=0.7)
            
            ax.set_title(label, fontsize=12, fontweight='bold', color='#2c3e50')
            ax.set_xlabel("Temperature (°C)", fontsize=10)
            ax.set_ylabel(label, fontsize=10)
            
            # Set proper temperature range and ticks for summary plots
            temp_min, temp_max = min(temps_sorted), max(temps_sorted)
            ax.set_xlim(temp_max + 1, temp_min - 1)
            
            # Create custom tick labels
            tick_positions = np.linspace(temp_max, temp_min, 5)
            tick_labels = [f"{t:.0f}°C" for t in tick_positions]
            ax.set_xticks(tick_positions)
            ax.set_xticklabels(tick_labels, rotation=45, ha='right')
            
            ax.grid(True, alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            # Add statistics
            mean_val = np.mean(values)
            ax.text(0.02, 0.98, f'μ: {mean_val:.3f}', 
                   transform=ax.transAxes, fontsize=8, verticalalignment='top',
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgray', alpha=0.8))
        
        plt.tight_layout(pad=3.0)
        pdf.savefig(fig)
        plt.close()

        # Phase transition analysis page
        if transitions:
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Create a phase diagram
            transition_temps = list(transitions.values())
            transition_labels = list(transitions.keys())
            
            # Sort transitions by temperature
            sorted_transitions = sorted(transitions.items(), key=lambda x: x[1], reverse=True)
            
            # Create phase regions
            y_positions = np.linspace(0.1, 0.9, len(sorted_transitions) + 1)
            
            for i, ((label, temp), y_pos) in enumerate(zip(sorted_transitions, y_positions[:-1])):
                # Phase region
                ax.axhspan(y_pos, y_positions[i+1], alpha=0.3, color=f'C{i}')
                ax.text(0.5, (y_pos + y_positions[i+1])/2, f"{label}\n({temp:.1f}°C)", 
                       ha='center', va='center', fontsize=12, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
                
                # Transition line
                ax.axhline(y=y_pos, color='red', linestyle='--', linewidth=2)
            
            ax.set_title("Phase Transition Diagram", fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel("Temperature (°C)", fontsize=14)
            ax.set_ylabel("Phase", fontsize=14)
            ax.set_xlim(min(temps) - 5, max(temps) + 5)
            ax.invert_xaxis()
            ax.grid(True, alpha=0.3)
            
            pdf.savefig(fig)
            plt.close()
