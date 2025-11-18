import numpy as np
import matplotlib.pyplot as plt
import subprocess
import os
import shutil
from typing import List
import pandas as pd
import sys

# Set matplotlib to use Agg backend (Headless plotting)
import matplotlib
matplotlib.use('Agg')

class AirfoilCFDAnalyzer:
    def __init__(self, V_cr: float = 42.0, rho: float = 1.225, chord: float = 1.0):
        self.V_cr = V_cr
        self.rho = rho
        self.chord = chord
        self.results = {}
        
        self.base_dir = os.getcwd()
        # IMPORTANT: Point to the REFINED data
        self.data_dir = os.path.join(self.base_dir, 'airfoil_data_refined')
        
        # Fallback
        if not os.path.exists(self.data_dir):
            self.data_dir = os.path.join(self.base_dir, 'airfoil_data_clean')
        
        # Create results directories
        os.makedirs('results/xfoil_results/polar_files', exist_ok=True)
        os.makedirs('results/xfoil_results/summary_plots', exist_ok=True)
        os.makedirs('results/xfoil_results/reports', exist_ok=True)

    def check_xfoil_available(self) -> bool:
        if shutil.which('xfoil') is None:
            print("❌ CRITICAL: 'xfoil' command not found in PATH.")
            return False
        return True
        
    def prepare_airfoil_file(self, airfoil_name: str):
        source_file = os.path.join(self.data_dir, f"{airfoil_name}.dat")
        temp_file = os.path.join(self.base_dir, f"{airfoil_name}.dat")
        
        if not os.path.exists(source_file):
            print(f"  ❌ Source not found: {source_file}")
            return False
            
        try:
            with open(source_file, 'r') as f:
                content = f.read()
            
            # Force Unix format
            with open(temp_file, 'w', newline='\n') as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
                
            return True
        except Exception as e:
            print(f"  ❌ Prepare Error: {e}")
            return False
      
        
    def create_xfoil_script(self, airfoil_name: str, alpha_list: List[float], 
                            reynolds: float, output_file_base: str):
        """
        Brute Force Script:
        - Replaces ASEQ with explicit ALFA loops.
        - Adds RPM 0.6 (Relaxation) to prevent oscillation.
        - Uses aggressive smoothing for the 6-series.
        """
        if not alpha_list: return ""
        
        # Organize Alphas: Center -> Out
        pos_alphas = sorted([a for a in alpha_list if a >= 0])
        neg_alphas = sorted([a for a in alpha_list if a < 0], reverse=True)

        commands = [f"LOAD {airfoil_name}.dat", f"{airfoil_name}"]

        # --- BRANCH 1: 6-SERIES BRUTE FORCE ---
        if "63012" in airfoil_name or "6series" in airfoil_name:
            print(f"  -> Using 6-Series Brute Force (Manual Step + Relaxation)")
            
            # 1. Heavy Geometry Fixes
            commands.append("GDES")
            commands.append("TGAP")
            commands.append("0.005") 
            commands.append("0.5")
            commands.append("EXEC")
            commands.append("\n")
            
            # 2. Smooth (Bring back FILT, the refined data might still have noise)
            commands.append("MDES")
            commands.append("FILT") # Smooth once
            commands.append("EXEC")
            commands.append("\n")
            
            # 3. Density
            commands.append("PPAR")
            commands.append("N 140") 
            commands.append("\n")
            commands.append("\n")
            
            # 4. Solver Settings
            commands.append("OPER")
            commands.append("ITER 500")
            commands.append("RPM 0.6")   # <--- NEW: Relaxation. Prevents wild oscillations.
            commands.append("VACC 0.01") # Keep Damping
            
            # 5. Initialization (Ramp)
            commands.append("ALFA 0") 
            commands.append("VISC 100000") 
            commands.append("ALFA 0")
            commands.append(f"VISC {reynolds}") 
            commands.append("M 0.0")
            commands.append("ALFA 0")
            
            # 6. MANUAL RECORDING LOOP (No ASEQ)
            commands.append("PACC")
            commands.append(f"{output_file_base}.polar")
            commands.append(f"{output_file_base}.dump")
            
            # Manual Step: 0 -> Positive
            for alpha in pos_alphas:
                commands.append(f"ALFA {alpha}")
            
            # Manual Step: 0 -> Negative
            commands.append("INIT") # Reset
            commands.append("ALFA 0")
            for alpha in neg_alphas:
                commands.append(f"ALFA {alpha}")

        # --- BRANCH 2: STANDARD AIRFOILS ---
        else:
            # Keep the ASEQ logic that is working perfectly for the others
            commands.append("GDES")
            commands.append("TGAP") 
            commands.append("0.002") 
            commands.append("0.5") 
            commands.append("EXEC") 
            commands.append("\n")
            
            commands.append("MDES")
            commands.append("FILT")
            commands.append("EXEC")
            commands.append("\n")
            
            commands.append("PPAR")
            commands.append("N 160")
            commands.append("\n")
            commands.append("\n")
            
            commands.append("OPER")
            commands.append(f"VISC {reynolds}")
            commands.append("M 0.0")
            commands.append("ITER 300")
            commands.append("PACC")
            commands.append(f"{output_file_base}.polar")
            commands.append(f"{output_file_base}.dump")
            
            # Standard ASEQ
            min_a = min(alpha_list)
            max_a = max(alpha_list)
            commands.append(f"ASEQ {min_a} {max_a} 1.0")

        commands.append("PACC")
        commands.append("\n")
        commands.append("QUIT")
        
        return "\n".join(commands) + "\n"

    def run_xfoil_command(self, script: str, airfoil_name: str):
        try:
            process = subprocess.Popen(
                ['xfoil'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.base_dir 
            )
            stdout, stderr = process.communicate(input=script, timeout=45)
            return True
        except Exception:
            return False
    
    def parse_results(self, airfoil: str, polar_file: str):
        if not os.path.exists(polar_file):
            print("  ⚠️ No polar file generated.")
            self.results[airfoil] = pd.DataFrame()
            return

        data = []
        with open(polar_file, 'r') as f:
            lines = f.readlines()
            
        start_parsing = False
        for line in lines:
            if "---" in line:
                start_parsing = True
                continue
            if start_parsing and line.strip():
                try:
                    parts = line.split()
                    data.append({
                        'alpha': float(parts[0]),
                        'CL': float(parts[1]),
                        'CD': float(parts[2]),
                        'CM': float(parts[4]),
                        'L/D': float(parts[1]) / float(parts[2]) if float(parts[2]) != 0 else 0
                    })
                except: continue
        
        if data:
            df = pd.DataFrame(data).drop_duplicates(subset=['alpha']).sort_values('alpha')
            self.results[airfoil] = df
            dest = os.path.join('results/xfoil_results/polar_files', f'{airfoil}.polar')
            shutil.copy(polar_file, dest)
            print(f"  ✅ Success: {len(df)} data points.")
        else:
            print("  ⚠️ Analysis ran but file was empty.")
            self.results[airfoil] = pd.DataFrame()

    def plot_results(self):
        valid = {k: v for k, v in self.results.items() if not v.empty}
        if not valid: return

        print("\nGenerating Plots...")
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        for name, df in valid.items():
            axes[0,0].plot(df['alpha'], df['CL'], 'o-', label=name)
            axes[0,1].plot(df['alpha'], df['CD'], 's-', label=name)
            axes[1,0].plot(df['alpha'], df['L/D'], '^-', label=name)
            axes[1,1].plot(df['alpha'], df['CM'], 'd-', label=name)

        axes[0,0].set_title('Lift Coefficient (CL)')
        axes[0,1].set_title('Drag Coefficient (CD)')
        axes[1,0].set_title('Lift/Drag Ratio (L/D)')
        axes[1,1].set_title('Moment Coefficient (CM)')

        for ax in axes.flat:
            ax.grid(True)
            ax.legend()
            ax.set_xlabel('Alpha (deg)')

        plt.tight_layout()
        plt.savefig('results/xfoil_results/summary_plots/results.png')
        print("✅ Plot saved: results/xfoil_results/summary_plots/results.png")

    def run_analysis(self, airfoils: List[str], alpha_list: List[float]):
        if not self.check_xfoil_available(): return
        
        mu = 1.7894e-5
        reynolds = self.rho * self.V_cr * self.chord / mu
        print(f"Starting Analysis | Re={reynolds:.2e} | Source: {self.data_dir}")
        
        for airfoil in airfoils:
            print(f"\n--- {airfoil} ---")
            if not self.prepare_airfoil_file(airfoil): continue
            
            output_base = os.path.join(self.base_dir, f"{airfoil}_results")
            script = self.create_xfoil_script(airfoil, alpha_list, reynolds, output_base)
            
            if self.run_xfoil_command(script, airfoil):
                polar_file = f"{output_base}.polar"
                self.parse_results(airfoil, polar_file)
            
            temp_dat = os.path.join(self.base_dir, f"{airfoil}.dat")
            if os.path.exists(temp_dat): os.remove(temp_dat)
            if os.path.exists(f"{output_base}.dump"): os.remove(f"{output_base}.dump")
            if os.path.exists(f"{output_base}.polar"): os.remove(f"{output_base}.polar")

if __name__ == "__main__":
    airfoils = [
        "naca0010", "naca0012", "naca23012", "naca2412", 
        "naca4412", "naca4415", "naca63012a"
    ]
    
    # --- FIXED LIST: Added -4 and 12 ---
    alpha_list = [-4, -2, 0, 2, 4, 6, 8, 10, 12]
    
    analyzer = AirfoilCFDAnalyzer()
    analyzer.run_analysis(airfoils, alpha_list)
    analyzer.plot_results()