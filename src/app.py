import sys
import numpy as np
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                             QWidget, QLabel, QPushButton, QTextEdit)
from PyQt6.QtGui import QFont
from physics_engine import DataLoader


class CMS_Simulation_App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CERN CMS Explorer")
        self.resize(1600, 900)
        self.setStyleSheet("background-color: #1e1e1e; color: #eee; font-family: Segoe UI, Arial;")


        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)


        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)

        # 1. 3D Viewport
        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor('#080808')
        self.view.setCameraPosition(distance=35, elevation=30)
        self.left_layout.addWidget(self.view)

        # 2. Navigation Controls
        self.controls_layout = QHBoxLayout()
        self.btn_prev = QPushButton("<< Previous Event")
        self.btn_prev.clicked.connect(self.prev_event)
        self.btn_prev.setStyleSheet(
            "background-color: #444; padding: 12px; font-weight: bold; border-radius: 4px; border: 1px solid #555;")

        self.btn_next = QPushButton("Next Event >>")
        self.btn_next.clicked.connect(self.next_event)
        self.btn_next.setStyleSheet(
            "background-color: #0078d7; padding: 12px; font-weight: bold; border-radius: 4px; border: 1px solid #005a9e;")

        self.controls_layout.addWidget(self.btn_prev)
        self.controls_layout.addWidget(self.btn_next)
        self.left_layout.addLayout(self.controls_layout)


        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_panel.setFixedWidth(500)

        # 3. Histogram
        self.chart_label = QLabel("Invariant Mass Distribution (Global Data)")
        self.chart_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.right_layout.addWidget(self.chart_label)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#222')
        self.plot_widget.setTitle("Mass Spectrum (The 'Bump' Hunt)", color="w", size="10pt")
        self.plot_widget.setLabel('left', 'Count', color='#aaa')
        self.plot_widget.setLabel('bottom', 'Mass (GeV)', color='#aaa')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.right_layout.addWidget(self.plot_widget)

        # 4. Context Box (The Teacher)
        self.info_box = QTextEdit()
        self.info_box.setReadOnly(True)
        self.info_box.setStyleSheet(
            "background-color: #252525; color: #e0e0e0; font-size: 14px; padding: 15px; border: 1px solid #444; border-radius: 4px;")
        self.right_layout.addWidget(self.info_box)

        # Assemble Layout
        self.main_layout.addWidget(self.left_panel, stretch=2)
        self.main_layout.addWidget(self.right_panel, stretch=1)

        # State Management
        self.current_index = 0
        self.events = []
        self.detector_items = []
        self.mass_data = []
        self.current_marker = None

        # Initialize
        self.draw_realistic_detector()
        self.load_data()

    def draw_realistic_detector(self):
        # 1. Inner Tracker (Green)
        self.add_detector_layer(radius=1.2, length=8.0, color=(0, 1, 0, 0.15), label="Silicon Tracker")

        # 2. Outer Solenoid Magnet (Red)
        self.add_detector_layer(radius=3.8, length=14.0, color=(1, 0, 0, 0.1), label="Solenoid Magnet (3.8T)")

        # Beamline reference
        beamline = gl.GLLinePlotItem(pos=np.array([[0, 0, -10], [0, 0, 10]]), color=(1, 1, 1, 0.2), width=1)
        self.view.addItem(beamline)
        self.detector_items.append(beamline)

    def add_detector_layer(self, radius, length, color, label):
        z_steps = np.linspace(-length / 2, length / 2, 7)
        t = np.linspace(0, 2 * np.pi, 60)
        x_ring = radius * np.cos(t)
        y_ring = radius * np.sin(t)

        for z in z_steps:
            z_ring = np.full_like(x_ring, z)
            pts = np.vstack([x_ring, y_ring, z_ring]).transpose()
            ring = gl.GLLinePlotItem(pos=pts, color=color, width=1, antialias=True)
            self.view.addItem(ring)
            self.detector_items.append(ring)

        theta_steps = np.linspace(0, 2 * np.pi, 12, endpoint=False)
        for theta in theta_steps:
            x = radius * np.cos(theta)
            y = radius * np.sin(theta)
            pts = np.array([[x, y, -length / 2], [x, y, length / 2]])
            line = gl.GLLinePlotItem(pos=pts, color=color, width=1, antialias=True)
            self.view.addItem(line)
            self.detector_items.append(line)

        t_item = gl.GLTextItem(pos=(radius * 1.1, 0, length / 2 + 0.5), text=label, color=color,
                               font=QFont("Arial", 10))
        self.view.addItem(t_item)
        self.detector_items.append(t_item)

    def load_data(self):
        loader = DataLoader()
        try:
            self.events = loader.load_cern_data("Dimuon_DoubleMu.csv")
            self.mass_data = [e.calculate_invariant_mass() for e in self.events]

            y, x = np.histogram(self.mass_data, bins=np.linspace(0, 120, 120))
            curve = pg.PlotCurveItem(x, y, stepMode=True, fillLevel=0, brush=(0, 120, 255, 80), pen='#0078d7')
            self.plot_widget.addItem(curve)

            self.current_marker = pg.InfiniteLine(pos=0, angle=90, pen=pg.mkPen('#ff3333', width=2),
                                                  label='Current Event', labelOpts={'color': '#ff3333'})
            self.plot_widget.addItem(self.current_marker)

            self.show_event(0)

        except Exception as e:
            self.info_box.setText(f"System Error: {str(e)}")

    def show_event(self, index):
        if index < 0 or index >= len(self.events): return
        self.current_index = index
        event = self.events[index]
        mass = event.calculate_invariant_mass()

        for item in self.view.items[:]:
            if item not in self.detector_items:
                self.view.removeItem(item)

        colors = [(1, 0.2, 0.2, 1), (0.2, 0.6, 1, 1)]
        for i, p in enumerate(event.particles):
            pos = self.calculate_path(p)
            plt = gl.GLLinePlotItem(pos=pos, color=colors[i % 2], width=2.5, antialias=True)
            self.view.addItem(plt)

        self.current_marker.setPos(mass)
        self.update_info_text(event, mass)

    def update_info_text(self, event, mass):
        # --- ENHANCED LOGIC AND DESCRIPTIONS ---

        candidate = "Unknown / Background"
        color_hex = "#cccccc"
        reasoning = """
        <ul style="margin-top: 0px;">
            <li><b>Visuals:</b> The tracks are curving significantly, meaning these particles have relatively low momentum.</li>
            <li><b>Math:</b> The calculated mass (%.2f GeV) does not match any stable resonance pattern.</li>
        </ul>
        """ % mass
        significance = "This is likely a random crossing of particles ('soft QCD') rather than the decay of a specific heavy particle."

        # J/PSI LOGIC
        if 2.8 < mass < 3.4:
            candidate = "J/Psi Meson"
            color_hex = "#00ffff"  # Cyan
            reasoning = f"""
            <ul style="margin-top: 0px;">
                <li><b>Visuals:</b> Notice the tracks are <b>tightly curled spirals</b>. This indicates the muons have lower energy (~4-5 GeV), meaning they came from a lighter parent.</li>
                <li><b>Math:</b> The calculated mass ({mass:.2f} GeV) sits exactly on the J/Psi peak (3.09 GeV).</li>
            </ul>
            """
            significance = "The J/Psi is made of a Charm Quark and Anti-Charm Quark. Its discovery in 1974 proved the existence of the Charm quark."

        # UPSILON LOGIC
        elif 9.0 < mass < 10.5:
            candidate = "Upsilon Meson"
            color_hex = "#ff00ff"  # Magenta
            reasoning = f"""
            <ul style="margin-top: 0px;">
                <li><b>Visuals:</b> The tracks are less curved than the J/Psi, but still clearly bent by the magnetic field.</li>
                <li><b>Math:</b> The mass ({mass:.2f} GeV) aligns with the Upsilon resonance (9.46 GeV).</li>
            </ul>
            """
            significance = "The Upsilon is a bound state of a Bottom Quark and Anti-Bottom Quark. It is 3x heavier than the J/Psi."

        # Z BOSON LOGIC
        elif 80.0 < mass < 100.0:
            candidate = "Z Boson"
            color_hex = "#ffcc00"  # Gold
            reasoning = f"""
            <ul style="margin-top: 0px;">
                <li><b>Visuals:</b> If you take a close look at the tracks they are <b>almost perfectly straight lines</b>. This means the muons are moving incredibly fast (High Momentum), punching through the magnetic field.</li>
                <li><b>Math:</b> Only a massive particle like the Z Boson (91.2 GeV) has enough energy to launch muons this hard.</li>
            </ul>
            """
            significance = "The Z Boson is a heavy carrier of the Weak Force. It is one of the heaviest fundamental particles known."

        # HTML Structure
        html = f"""
        <h2>Event #{self.current_index} Analysis</h2>
        <hr style="border: 1px solid #444;">
        <p style="font-size: 16px;"><b>Invariant Mass:</b> <span style="color: yellow; font-weight: bold;">{mass:.4f} GeV</span></p>
        <p style="font-size: 16px;"><b>Likely Candidate:</b> <b style="color: {color_hex};">{candidate}</b></p>

        <br>
        <h3 style="color: #aaa; border-bottom: 1px solid #444; padding-bottom: 5px;">Reasoning:</h3>
        {reasoning}
        <br>
        <h3 style="color: #aaa; border-bottom: 1px solid #444; padding-bottom: 5px;">Significance:</h3>
        <p style="line-height: 1.4;">{significance}</p>
        """
        self.info_box.setHtml(html)

    def next_event(self):
        self.show_event(self.current_index + 1)

    def prev_event(self):
        self.show_event(self.current_index - 1)

    def calculate_path(self, p):
        dt = 0.1
        steps = 1000
        detector_limit = 9.0
        path = []
        x, y, z = 0, 0, 0
        px, py, pz = p.px, p.py, p.pz
        omega = (0.3 * 3.8 * p.charge) / p.E

        for _ in range(steps):
            if (x ** 2 + y ** 2) ** 0.5 > detector_limit or abs(z) > 15: break
            path.append([x, y, z])
            d_phi = omega * dt
            n_px = px * np.cos(d_phi) - py * np.sin(d_phi)
            n_py = px * np.sin(d_phi) + py * np.cos(d_phi)
            px, py = n_px, n_py
            x += (px / p.E) * dt
            y += (py / p.E) * dt
            z += (pz / p.E) * dt
        return np.array(path)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CMS_Simulation_App()
    window.show()
    sys.exit(app.exec())
