# 2D Aerodynamic Airfoil Analysis Framework

A comprehensive Python-based framework for automated 2D aerodynamic analysis. This project bridges the gap between inviscid flow visualization (Panel Method) and viscous performance estimation (XFOIL) to generate high-quality plots for academic thesis work.

## 🚀 Features

* **Automatic Geometry Generation:** Generates mathematically perfect NACA 4-digit and 5-digit airfoils.
* **Geometry Refinement:** Uses parametric B-Splines to fix jagged leading edges and ensure smooth convergence.
* **Robust XFOIL Interface:** Features a "Smart Sequencing" algorithm that prevents XFOIL crashes on sensitive Laminar Flow airfoils (e.g., NACA 6-series) using Reynolds ramping and geometry surgery.
* **Hybrid Analysis:** Combines XFOIL drag data with Panel Method pressure fields.
* **Thesis-Ready Plots:** Automatically generates separated, high-resolution plots for Lift, Drag, Efficiency, Streamlines, and Pressure Contours.

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/AeroAnalysisProject.git](https://github.com/yourusername/AeroAnalysisProject.git)
cd AeroAnalysisProject