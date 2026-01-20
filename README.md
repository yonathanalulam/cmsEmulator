# CERN CMS Particle Explorer ⚛️

I built this Python app to visualize **real** high-energy physics collisions from the Large Hadron Collider (LHC).

Instead of just looking at numbers, this tool renders actual sensor data from the CMS experiment in 3D. It applies real physics math (the Lorentz Force) to show how subatomic particles move through magnetic fields.

## 🚀 What It Does
* **3D Replay:** Visualizes verified collision events where muons were detected.
* **Physics Analysis:** Automatically calculates the mass of the "invisible" parent particle (like the **Z-Boson** or **J/Psi Meson**).
* **Educational Context:** Tells you exactly what you're looking at and why it matters scientifically.

## 🔬 The Science
The CMS detector is basically a giant, 14,000-tonne camera.
* It uses a massive magnet to bend the path of charged particles.
* **Straight lines** = High energy (Heavy particles).
* **Curled spirals** = Low energy (Lighter particles).

**Data Source:** Verified [Dimuon Dataset](http://opendata.cern.ch/record/545) from the CERN Open Data Portal.

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone [https://github.com/yonathanalulam/cmsEmulator.git](https://github.com/yonathanalulam/cmsEmulator.git)
cd cmsEmulator

# 2. Install requirements
pip install -r requirements.txt

# 3. Launch!
python app.py
