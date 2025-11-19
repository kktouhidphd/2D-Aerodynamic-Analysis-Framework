<h1 align="center">2D Aerodynamic Airfoil Analysis Framework</h1>

<h4 align="center">
  <a href="https://github.com/kktouhidphd/2D-Aerodynamic-Analysis-Framework/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.8%2B-green.svg" alt="Python">
  </a>
  <a href="https://web.mit.edu/drela/Public/web/xfoil/">
    <img src="https://img.shields.io/badge/Backend-XFOIL-red.svg" alt="XFOIL">
  </a>
</h4>

<div align="center">
  <span class="author-block">
    <a href="https://github.com/kktouhidphd">Khwaja Mohamed Khalid</a>
  </span>
</div>

---

## 🎯 Overview

The **2D Aerodynamic Analysis Framework** is a comprehensive Python-based toolkit designed to automate the generation, analysis, and visualization of 2D airfoils. It bridges the gap between inviscid flow visualization (Panel Method) and viscous performance estimation (XFOIL).

This framework specifically addresses stability issues in analyzing laminar flow airfoils by implementing robust "Smart Sequencing" algorithms and geometry refinement techniques, making it ideal for academic research and thesis work.

## ✨ Highlights

- **🤖 Automated Geometry Generation**: Mathematically generates precise coordinates for standard NACA 4-digit and 5-digit airfoils.
- **🔧 Advanced Refinement**: Uses parametric B-Splines to eliminate discretization noise and "knife-edge" singularities that typically crash CFD solvers.
- **🧠 Smart XFOIL Interface**: A robust wrapper that handles laminar separation bubbles using:
    - **Reynolds Ramping**: Gradual stability stepping.
    - **Geometry Surgery**: Automatic adjustment of trailing edge gaps.
- **📊 Multi-Fidelity Visualization**: Combines viscous drag data with inviscid pressure field visualization.

## 📁 Project Structure

```text
├── init_project.py              # Setup script (Run this first!)
├── README.md                    # Documentation
├── CITATION.cff                 # Citation file
├── LICENSE                      # License file
├── requirements.txt             # Pip dependencies
├── environment.yml              # Conda dependencies
│
├── scripts/                     # 🧠 Core Analysis Pipeline
│   ├── 1_generate_naca_files.py # Generates raw coordinates
│   ├── 2_refine_airfoils.py     # B-Spline smoothing & re-paneling
│   ├── 3_xfoil_analyzer.py      # Viscous solver (XFOIL wrapper)
│   ├── 4_xfoil_debug.py         # Diagnostic tool for binary checks
│   └── 5_plots.py               # Hybrid visualization engine
│
├── airfoil_data_clean/          # Generated raw geometries
├── airfoil_data_refined/        # Optimization-ready geometries
└── results/                     # 📊 Output Artifacts
    ├── xfoil_results/           # Raw polar files & convergence logs
    ├── plots_separated/         # Individual high-res performance curves
    └── comparisons_full/        # Grid visualizations (Streamlines/Pressure)
```
## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/kktouhidphd/2D-Aerodynamic-Analysis-Framework.git](https://github.com/kktouhidphd/2D-Aerodynamic-Analysis-Framework.git)
cd 2D-Aerodynamic-Analysis-Framework
```
### 2. Install Python Dependencies
Option A: Conda (Recommended)
```bash
conda env create -f environment.yml
conda activate aero_analysis
```
Option B: Pip
```bash
pip install -r requirements.txt
```
### 3. Install XFOIL (Critical)
The backend requires the ```xfoil``` binary to be executable in your system path.

🐧 Linux / WSL:
```bash
sudo apt-get update
sudo apt-get install xfoil
```
🍎 macOS:
```bash
brew install xfoil
```
🪟 Windows:
1. Download XFOIL from the MIT Website.

2. Extract the zip file.

3. Copy ```xfoil.exe``` and place it in the root folder of this project (same folder as this README).
### 4. Initialization
Run the setup script to verify your environment and create data folders:
```bash
python init_project.py
```
🔬 Execution Workflow
Run the scripts in the ```scripts/ directory``` in numerical order to perform the full analysis pipeline.

Step 1: Geometry Generation
```bash
python scripts/1_generate_naca_files.py
```
Step 2: Geometry Refinement

Applies Parametric B-Splines to smooth the leading edge and re-distributes panel density (N=160) using cosine clustering to capture high-gradient flow regions.
```bash
python scripts/2_refine_airfoils.py
```
Step 3: Viscous Analysis (XFOIL)
Runs the automated CFD sweep. This script automatically detects 6-series airfoils and switches to "Nuclear Stability Mode" (Geometry Surgery + Damped Solver) to ensure convergence.
```bash
python scripts/3_xfoil_analyzer.py
```
Step 4: Diagnostics (Optional)

If Step 3 fails silently or crashes, run this diagnostic tool to check if XFOIL is reachable.
```bash
python scripts/4_xfoil_debug.py
```
Step 5: Hybrid Visualization
```bash
python scripts/5_panel_method_comparison_full.py
```
## 📊 Output Examples

The `results/` directory will contain:

* **Performance Curves:** High-resolution comparison of Lift Coefficient, Drag Coefficient, Moment Coefficient and L/D vs Angle of Attack (AoA).
    * *Location:* `results/plots_separated/Comparison_Efficiency.png`
* **Flow Field Grids:** Side-by-side comparison of streamlines and velocity magnitude for all airfoils at specific angles.
    * *Location:* `results/comparisons_full/Comp_Grid_Velocity_a4.0.png`
* **Raw Data:** `.polar` files compatible with Excel or other plotting tools.
    * *Location:* `results/xfoil_results/polar_files/`

## 📄 Citation

If you use this framework in your research or academic work, please cite it as:

```bibtex
@software{AeroFramework2025,
  author = {Khalid, Khwaja Mohamed},
  title = {2D Aerodynamic Airfoil Analysis Framework},
  year = {2025},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{[https://github.com/kktouhidphd/2D-Aerodynamic-Analysis-Framework](https://github.com/kktouhidphd/2D-Aerodynamic-Analysis-Framework)}}
}
```
## 📧 Contact
For questions or collaboration:

    Author: Khwaja Mohamed Khalid
    GitHub: @kktouhidphd




