# 2D-Aerodynamic-Analysis-Framework
Automated multi-fidelity framework for 2D airfoil analysis bridging XFOIL and Panel Methods. Features robust geometry refinement, smart sequencing for laminar airfoils, and thesis-ready visualization.
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
.
├── scripts/                     # 🧠 Core Analysis Pipeline
│   ├── 1_generate_naca_files.py # Generates raw coordinates
│   ├── 2_refine_airfoils.py     # B-Spline smoothing & re-paneling
│   ├── 3_xfoil_analyzer.py      # Viscous solver (XFOIL wrapper)
│   ├── 4_xfoil_debug.py         # Diagnostic tool for binary checks
│   └── 5_panel_method_comparison_full.py # Hybrid visualization engine
│
├── airfoil_data_clean/          # Generated raw geometries
├── airfoil_data_refined/        # Optimization-ready geometries
└── results/                     # 📊 Output Artifacts

