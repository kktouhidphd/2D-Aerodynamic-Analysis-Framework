import numpy as np
import matplotlib.pyplot as plt
from scipy import linalg, interpolate
import os
import pandas as pd
from typing import List, Dict, Tuple

# Force Headless Mode
import matplotlib
matplotlib.use('Agg')
import warnings
warnings.filterwarnings("ignore")

# --- CORE SOLVER CLASS ---
class PanelMethodAirfoil:
    def __init__(self, num_panels=160):
        self.num_panels = num_panels
        
    def read_airfoil_dat(self, filename: str) -> Tuple[np.ndarray, np.ndarray]:
        try:
            with open(filename, 'r') as f: lines = f.readlines()
            x, y = [], []
            for line in lines:
                line = line.strip()
                if not line or any(c.isalpha() for c in line): continue
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        x.append(float(parts[0]))
                        y.append(float(parts[1]))
                    except ValueError: continue
            return np.array(x), np.array(y)
        except: return np.array([]), np.array([])

    def create_panels(self, x: np.ndarray, y: np.ndarray) -> List[Dict]:
        if not (np.isclose(x[0], x[-1]) and np.isclose(y[0], y[-1])):
            x = np.append(x, x[0])
            y = np.append(y, y[0])
        
        dist = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
        t_original = np.concatenate(([0], np.cumsum(dist)))
        t_original /= t_original[-1]
        
        fx = interpolate.interp1d(t_original, x, kind='cubic')
        fy = interpolate.interp1d(t_original, y, kind='cubic')
        
        t_new = 0.5 * (1 - np.cos(np.linspace(0, np.pi, self.num_panels + 1)))
        x_p, y_p = fx(t_new), fy(t_new)
        
        panels = []
        for i in range(self.num_panels):
            x1, y1, x2, y2 = x_p[i], y_p[i], x_p[i+1], y_p[i+1]
            length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            theta = np.arctan2(y2-y1, x2-x1)
            panels.append({
                'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                'xc': (x1+x2)/2, 'yc': (y1+y2)/2,
                'length': length, 'theta': theta, 'beta': theta + np.pi/2
            })
        return panels
    
    def solve_flow(self, panels: List[Dict], alpha_deg: float, V_inf: float = 1.0) -> Dict:
        alpha = np.radians(alpha_deg)
        n = len(panels)
        A = np.zeros((n, n))
        b = np.zeros(n)
        
        for i, p in enumerate(panels):
            b[i] = -V_inf * (np.cos(alpha)*np.cos(p['beta']) + np.sin(alpha)*np.sin(p['beta']))
            
        for i, p_i in enumerate(panels):
            for j, p_j in enumerate(panels):
                if i == j:
                    A[i, j] = 0.5
                    continue
                X = (p_i['xc'] - p_j['x1']) * np.cos(p_j['theta']) + (p_i['yc'] - p_j['y1']) * np.sin(p_j['theta'])
                Y = -(p_i['xc'] - p_j['x1']) * np.sin(p_j['theta']) + (p_i['yc'] - p_j['y1']) * np.cos(p_j['theta'])
                r1_sq, r2_sq = X**2 + Y**2, (X - p_j['length'])**2 + Y**2
                phi1, phi2 = np.arctan2(Y, X), np.arctan2(Y, X - p_j['length'])
                vn = ((X - p_j['length'])*np.log(r2_sq + 1e-12) - X*np.log(r1_sq + 1e-12) + 2*Y*(phi2-phi1)) / (4*np.pi)
                A[i, j] = vn / p_j['length']

        try: sigma = linalg.solve(A, b)
        except: return None

        V_t, Cp = np.zeros(n), np.zeros(n)
        for i, p in enumerate(panels):
            vt_inf = V_inf * (np.cos(alpha)*-np.sin(p['beta']) + np.sin(alpha)*np.cos(p['beta']))
            V_t[i] = vt_inf + sigma[i]/2
            Cp[i] = 1 - (V_t[i]/V_inf)**2
            
        return {'sigma': sigma, 'Cp': Cp, 'panels': panels}

    def compute_flow_field(self, result: Dict, alpha_deg: float, res: int = 50):
        alpha = np.radians(alpha_deg)
        panels = result['panels']
        sigma = result['sigma']
        
        x = np.linspace(-0.5, 1.5, res)
        y = np.linspace(-0.6, 0.6, res)
        X, Y = np.meshgrid(x, y)
        
        U = np.ones_like(X) * np.cos(alpha)
        V = np.ones_like(Y) * np.sin(alpha)
        
        for k, p in enumerate(panels):
            dx, dy = X - p['x1'], Y - p['y1']
            X_loc = dx * np.cos(p['theta']) + dy * np.sin(p['theta'])
            Y_loc = -dx * np.sin(p['theta']) + dy * np.cos(p['theta'])
            r1_sq, r2_sq = X_loc**2 + Y_loc**2, (X_loc - p['length'])**2 + Y_loc**2
            theta1, theta2 = np.arctan2(Y_loc, X_loc), np.arctan2(Y_loc, X_loc - p['length'])
            J = 0.5 * np.log((r2_sq + 1e-10)/(r1_sq + 1e-10))
            I = theta2 - theta1
            
            u_loc = (J*np.cos(p['theta']) - I*np.sin(p['theta'])) * sigma[k]/(2*np.pi)
            v_loc = (J*np.sin(p['theta']) + I*np.cos(p['theta'])) * sigma[k]/(2*np.pi)
            U += u_loc; V += v_loc
            
        V_mag = np.sqrt(U**2 + V**2)
        Cp_field = 1 - V_mag**2
        return {'X': X, 'Y': Y, 'U': U, 'V': V, 'V_mag': V_mag, 'Cp': Cp_field}
    
    def load_xfoil_polar(self, airfoil_name: str):
        # Uses absolute path to guarantee file finding
        polar_path = os.path.abspath(os.path.join('results', 'xfoil_results', 'polar_files', f'{airfoil_name}.polar'))
        if not os.path.exists(polar_path): 
            print(f"    ⚠️ File not found: {polar_path}")
            return None
        try:
            data = []
            with open(polar_path, 'r') as f: lines = f.readlines()
            parsing = False
            for line in lines:
                if "---" in line: parsing = True; continue
                if parsing and line.strip():
                    try:
                        p = line.split()
                        if len(p) < 5: continue 
                        data.append({
                            'alpha': float(p[0]), 'CL': float(p[1]), 
                            'CD': float(p[2]), 'CM': float(p[4]),
                            'L/D': float(p[1])/float(p[2]) if float(p[2])!=0 else 0
                        })
                    except: continue
            if not data: 
                print(f"    ⚠️ File exists but parsed 0 points: {airfoil_name}")
                return None
            print(f"    ✅ Loaded {len(data)} XFOIL points for {airfoil_name}")
            return pd.DataFrame(data).sort_values('alpha')
        except Exception as e: 
            print(f"    ❌ Error reading {airfoil_name}: {e}")
            return None

# --- COMPARATOR CLASS ---
class AirfoilComparator:
    def __init__(self, airfoils, data_dir, output_dir):
        self.airfoils = airfoils
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.solver = PanelMethodAirfoil(num_panels=160)
        self.loaded_geometries = {}
        self.loaded_polars = {}
        
        print("\n--- Loading Data ---")
        for name in airfoils:
            path = os.path.join(data_dir, f"{name}.dat")
            if os.path.exists(path):
                self.loaded_geometries[name] = self.solver.read_airfoil_dat(path)
            
            polar = self.solver.load_xfoil_polar(name)
            if polar is not None:
                self.loaded_polars[name] = polar

    # --- PLOT TYPE 1: GEOMETRY GRID ---
    def plot_geometry_comparison_grid(self):
        print("  Generating Geometry Grid...")
        rows, cols = 4, 2
        fig, axes = plt.subplots(rows, cols, figsize=(16, 12))
        axes_flat = axes.flatten()
        fig.suptitle("Airfoil Geometry Comparison", fontsize=16)
        
        for i, name in enumerate(self.airfoils):
            if name not in self.loaded_geometries: continue
            ax = axes_flat[i]
            x, y = self.loaded_geometries[name]
            ax.fill(x, y, 'gray', alpha=0.3)
            ax.plot(x, y, 'k-', linewidth=1.5)
            ax.set_title(f"{name.upper()}", fontsize=10, fontweight='bold')
            ax.axis('equal')
            ax.grid(True, alpha=0.2)
            ax.set_xticks([])
            if i % 2 == 0: ax.set_ylabel("y/c")
            else: ax.set_yticks([])

        for j in range(len(self.airfoils), rows*cols): axes_flat[j].axis('off')
        try: plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        except: pass
        plt.savefig(os.path.join(self.output_dir, "Comparison_Grid_Geometry.png"), dpi=200)
        plt.close()

    # --- PLOT TYPE 2: INDIVIDUAL PERFORMANCE PLOTS (SEPARATED) ---
    def plot_metric_separate(self, x_key, y_key, title, xlabel, ylabel, filename):
        """Generic function to plot a single metric for all airfoils"""
        print(f"  Generating {filename}...")
        if not self.loaded_polars: return
        
        plt.figure(figsize=(10, 7))
        
        for name, df in self.loaded_polars.items():
            # Plot ALL available XFOIL data points
            plt.plot(df[x_key], df[y_key], 'o-', markersize=4, linewidth=1.5, label=name)
            
        plt.title(title, fontsize=14)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True, alpha=0.3)
        plt.legend()
        
        plt.savefig(os.path.join(self.output_dir, filename), dpi=300)
        plt.close()

    def plot_all_performance_metrics(self):
        # Calls the generic function for each specific graph you need
        self.plot_metric_separate('alpha', 'CL', 'Lift Curve (CL vs Alpha)', 'Alpha (deg)', 'CL', 'Comparison_Lift_Curve.png')
        self.plot_metric_separate('alpha', 'CD', 'Drag Curve (CD vs Alpha)', 'Alpha (deg)', 'CD', 'Comparison_Drag_Curve.png')
        self.plot_metric_separate('alpha', 'L/D', 'Aerodynamic Efficiency (L/D)', 'Alpha (deg)', 'L/D Ratio', 'Comparison_Efficiency.png')
        self.plot_metric_separate('alpha', 'CM', 'Moment Coefficient (CM)', 'Alpha (deg)', 'CM', 'Comparison_Moment_Curve.png')
        self.plot_metric_separate('CD', 'CL', 'Drag Polar (CL vs CD)', 'CD', 'CL', 'Comparison_Drag_Polar.png')

    # --- PLOT TYPE 3: CP LINE GRAPH ---
    def plot_overlapped_cp(self, alpha: float):
        plt.figure(figsize=(12, 8))
        for name, (x, y) in self.loaded_geometries.items():
            panels = self.solver.create_panels(x, y)
            res = self.solver.solve_flow(panels, alpha_deg=alpha)
            if res:
                xc = [p['xc'] for p in panels]
                plt.plot(xc, res['Cp'], linewidth=1.5, label=name)

        plt.gca().invert_yaxis()
        plt.title(f"Surface Pressure Comparison @ {alpha}°")
        plt.xlabel("x/c"); plt.ylabel("-Cp")
        plt.grid(True, alpha=0.3); plt.legend()
        plt.savefig(os.path.join(self.output_dir, f"Comp_Line_Cp_a{alpha}.png"), dpi=200)
        plt.close()

    # --- PLOT TYPE 4: FLOW FIELD GRIDS ---
    def plot_field_grid(self, alpha: float, plot_type: str):
        print(f"  Generating {plot_type} grid for Alpha {alpha}...")
        rows, cols = 4, 2
        fig, axes = plt.subplots(rows, cols, figsize=(16, 16))
        axes_flat = axes.flatten()
        fig.suptitle(f"Comparison of {plot_type.title()} @ Alpha = {alpha}°", fontsize=16)
        
        for i, name in enumerate(self.airfoils):
            if name not in self.loaded_geometries: continue
            ax = axes_flat[i]
            x, y = self.loaded_geometries[name]
            panels = self.solver.create_panels(x, y)
            res = self.solver.solve_flow(panels, alpha_deg=alpha)
            
            if res:
                ff = self.solver.compute_flow_field(res, alpha_deg=alpha, res=60)
                xp = [p['x1'] for p in panels] + [panels[-1]['x2']]
                yp = [p['y1'] for p in panels] + [panels[-1]['y2']]
                
                if plot_type == 'streamlines':
                    ax.streamplot(ff['X'], ff['Y'], ff['U'], ff['V'], density=1.0, color='b', linewidth=0.6)
                    ax.fill(xp, yp, 'k', zorder=10)
                elif plot_type == 'velocity':
                    c = ax.contourf(ff['X'], ff['Y'], ff['V_mag'], levels=40, cmap='viridis')
                    ax.fill(xp, yp, 'w', zorder=10)
                    if i == 1: plt.colorbar(c, ax=axes, fraction=0.02, pad=0.04)
                elif plot_type == 'pressure':
                    c = ax.contourf(ff['X'], ff['Y'], ff['Cp'], levels=40, cmap='jet')
                    ax.fill(xp, yp, 'w', zorder=10)
                    
                ax.plot(xp, yp, 'k-', linewidth=1)
                ax.set_title(f"{name}", fontsize=10)
                ax.axis('equal')
                ax.set_xticks([]); ax.set_yticks([])

        for j in range(len(self.airfoils), rows*cols): axes_flat[j].axis('off')
        try: plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        except: pass
        plt.savefig(os.path.join(self.output_dir, f"Comp_Grid_{plot_type.title()}_a{alpha}.png"), dpi=200)
        plt.close()

if __name__ == "__main__":
    base_dir = os.getcwd()
    data_dir = os.path.join(base_dir, 'airfoil_data_refined')
    output_dir = os.path.join(base_dir, 'results', 'plots_separated')
    os.makedirs(output_dir, exist_ok=True)
    
    airfoils = [
        "naca0010", "naca0012", "naca23012", "naca2412", 
        "naca4412", "naca4415", "naca63012a"
    ]
    
    # --- FULL SWEEP (Plots everything) ---
    comparison_alphas = [-4, -2, 0, 2, 4, 6, 8, 10, 12]
    
    comparator = AirfoilComparator(airfoils, data_dir, output_dir)
    
    print("--- Starting Plot Generation ---")
    
    # 1. Grid Geometry Plot
    comparator.plot_geometry_comparison_grid()
    
    # 2. SEPARATED Performance Plots (The feature you requested)
    comparator.plot_all_performance_metrics()
    
    # 3. Loop through ALL angles for Flow Fields
    for alpha in comparison_alphas:
        print(f"\nProcessing Alpha = {alpha}...")
        comparator.plot_overlapped_cp(alpha)
        comparator.plot_field_grid(alpha, 'streamlines')
        comparator.plot_field_grid(alpha, 'velocity')
        comparator.plot_field_grid(alpha, 'pressure')

    print(f"\n✅ All plots saved to: {output_dir}")