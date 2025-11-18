import os
import numpy as np

def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

def write_dat_file(filename, name, x, y):
    """Writes X, Y arrays to a formatted XFOIL .dat file"""
    ensure_dir(filename)
    with open(filename, 'w') as f:
        f.write(f"{name}\n")
        for i in range(len(x)):
            f.write(f" {x[i]:.6f}   {y[i]:.6f}\n")
    print(f"✅ Created: {filename}")

def get_cosine_spacing(n_points):
    """Generates 0 to 1 spacing clustered at ends"""
    beta = np.linspace(0, np.pi, int(n_points/2) + 1)
    return 0.5 * (1 - np.cos(beta))

def calculate_thickness(x, t):
    """Standard NACA thickness distribution"""
    return 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 +
                    0.2843 * x**3 - 0.1015 * x**4)

def naca4_digit(code, n_points=200):
    """Math for 4-Digit Series (e.g. 2412)"""
    m = int(code[0]) / 100.0
    p = int(code[1]) / 10.0
    t = int(code[2:]) / 100.0
    
    x = get_cosine_spacing(n_points)
    yt = calculate_thickness(x, t)
    
    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)
    
    for i in range(len(x)):
        if m == 0:
            yc[i], dyc_dx[i] = 0, 0
        else:
            if x[i] < p:
                yc[i] = (m / p**2) * (2 * p * x[i] - x[i]**2)
                dyc_dx[i] = (2 * m / p**2) * (p - x[i])
            else:
                yc[i] = (m / (1 - p)**2) * ((1 - 2 * p) + 2 * p * x[i] - x[i]**2)
                dyc_dx[i] = (2 * m / (1 - p)**2) * (p - x[i])

    theta = np.arctan(dyc_dx)
    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)
    
    return np.concatenate((xu[::-1], xl[1:])), np.concatenate((yu[::-1], yl[1:]))

def naca5_digit(code, n_points=200):
    """
    Math for 5-Digit Series (Specifically 23012 class).
    Ref: Theory of Wing Sections, Abbott & Von Doenhoff
    """
    # Parameters for the "230" Mean Line
    # Design CL = 0.3 (The '2' and '30' combined implies specific constants)
    m = 0.2025
    p = 0.15
    k1 = 15.957
    
    t = int(code[3:]) / 100.0 # Last two digits are thickness (12 -> 0.12)
    
    x = get_cosine_spacing(n_points)
    yt = calculate_thickness(x, t)
    
    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)
    
    for i in range(len(x)):
        if x[i] < p:
            yc[i] = (k1 / 6.0) * (x[i]**3 - 3*m*x[i]**2 + (m**2)*(3-m)*x[i])
            dyc_dx[i] = (k1 / 6.0) * (3*x[i]**2 - 6*m*x[i] + (m**2)*(3-m))
        else:
            yc[i] = (k1 * (m**3) / 6.0) * (1 - x[i])
            dyc_dx[i] = - (k1 * (m**3) / 6.0)
            
    theta = np.arctan(dyc_dx)
    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)
    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)
    
    return np.concatenate((xu[::-1], xl[1:])), np.concatenate((yu[::-1], yl[1:]))

# --- HARDCODED 6-SERIES (Math for this is very complex, sticking to data) ---
# This is a CLEANED version of 63-012A (Closed TE, Smooth LE)
NACA63012A_COORDS = """
1.000000 0.000000
0.997200 0.000200
0.985000 0.001800
0.970000 0.004500
0.950000 0.007200
0.900000 0.014400
0.800000 0.028400
0.700000 0.041500
0.600000 0.052500
0.500000 0.060000
0.400000 0.063000
0.350000 0.062000
0.300000 0.059600
0.250000 0.055600
0.200000 0.050400
0.150000 0.043700
0.100000 0.035200
0.075000 0.030100
0.050000 0.024200
0.025000 0.016700
0.012500 0.011600
0.005000 0.007200
0.001000 0.003000
0.000000 0.000000
0.001000 -0.003000
0.005000 -0.007200
0.012500 -0.011600
0.025000 -0.016700
0.050000 -0.024200
0.075000 -0.030100
0.100000 -0.035200
0.150000 -0.043700
0.200000 -0.050400
0.250000 -0.055600
0.300000 -0.059600
0.350000 -0.062000
0.400000 -0.063000
0.500000 -0.060000
0.600000 -0.052500
0.700000 -0.041500
0.800000 -0.028400
0.900000 -0.014400
0.950000 -0.007200
0.985000 -0.001800
1.000000 0.000000
"""

def write_hardcoded(filename, name, data_str):
    ensure_dir(filename)
    with open(filename, 'w') as f:
        f.write(f"{name}\n")
        for line in data_str.strip().split('\n'):
            parts = line.split()
            if len(parts) == 2:
                f.write(f" {float(parts[0]):.6f}   {float(parts[1]):.6f}\n")
    print(f"✅ Created: {filename}")

if __name__ == "__main__":
    # NOTE: We save directly to 'airfoil_data_clean'
    # The refiner will assume this is the source.
    output_dir = os.path.join(os.getcwd(), "airfoil_data_clean")
    
    print(f"--- Generating High-Res Mathematical Airfoils ---")
    
    # 1. Generate 4-Digit (Math)
    for code in ["0010", "0012", "2412", "4412", "4415"]:
        X, Y = naca4_digit(code, n_points=240)
        write_dat_file(os.path.join(output_dir, f"naca{code}.dat"), f"NACA {code}", X, Y)
        
    # 2. Generate 5-Digit (Math - NEW!)
    # Specifically for 23012
    X, Y = naca5_digit("23012", n_points=240)
    write_dat_file(os.path.join(output_dir, "naca23012.dat"), "NACA 23012", X, Y)
    
    # 3. Write 6-Series (Hardcoded but cleaned)
    write_hardcoded(os.path.join(output_dir, "naca63012a.dat"), "NACA 63012A", NACA63012A_COORDS)
    
    print("\nGeneration Complete. Run the Refiner script next.")