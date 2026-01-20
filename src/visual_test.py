import matplotlib.pyplot as plt
import numpy as np
from src.physics_engine import DataLoader


def simulate_and_draw():
    # 1. Load the Data
    loader = DataLoader()
    events = loader.load_cern_data("Dimuon_DoubleMu.csv")

    # 2. Pick the verified event (Event ID: 74601703)
    target_event = events[0]

    print(f"Visualizing Event #{target_event.id}")

    # 3. Setup the 3D Plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # 4. Simulate each particle in the event
    colors = ['r', 'b']  # Red for particle 1, Blue for particle 2

    for i, p in enumerate(target_event.particles):



        # 1. Create lists to hold the path
        xs, ys, zs = [p.x], [p.y], [p.z]

        # 2. Simulation Parameters
        dt = 0.1  # Smaller time steps makes the curve look smoother
        max_steps = 2000
        detector_radius_limit = 7.5  # Meters (Approx outer limit of CMS)

        # 3. Manual Stepping Loop
        current_x, current_y, current_z = p.x, p.y, p.z
        curr_px, curr_py, curr_pz = p.px, p.py, p.pz

        # Angular velocity w = (q * B) / E
        # 0.3 is the conversion factor for natural units
        omega = (0.3 * 3.8 * p.charge) / p.E

        for _ in range(max_steps):
            # IMPORTANT: Check if we hit the wall
            r = (current_x ** 2 + current_y ** 2) ** 0.5
            if r > detector_radius_limit:
                break  # Particle has left the building!

            # Physics Math (Lorentz Force Rotation)
            # Rotating the momentum vector because magnetic fields only change direction
            d_phi = omega * dt
            new_px = curr_px * np.cos(d_phi) - curr_py * np.sin(d_phi)
            new_py = curr_px * np.sin(d_phi) + curr_py * np.cos(d_phi)
            curr_px, curr_py = new_px, new_py

            # Move Position
            # dx = (p/E) * dt  (since v = p/E in relativistic units)
            current_x += (curr_px / p.E) * dt
            current_y += (curr_py / p.E) * dt
            current_z += (curr_pz / p.E) * dt

            xs.append(current_x)
            ys.append(current_y)
            zs.append(current_z)

        ax.plot(xs, ys, zs, color=colors[i], linewidth=2, label=f'Muon {i + 1} (E={p.E:.1f} GeV)')

    # 5. Draw the Detector Reference (Simple Cylinder)
    # The CMS Tracker is roughly 2.4m diameter (radius 1.2m)
    # Drawing a simple circle to represent the beam pipe
    theta = np.linspace(0, 2 * np.pi, 100)
    xc = 10 * np.cos(theta)
    yc = 10 * np.sin(theta)
    ax.plot(xc, yc, 0, color='k', linestyle='--', alpha=0.3, label='Detector Wall')

    # Labels
    ax.set_xlabel('X (meters)')
    ax.set_ylabel('Y (meters)')
    ax.set_zlabel('Z (meters along beam)')
    ax.set_title(f'CMS Event Reconstruction: {target_event.id}')
    ax.legend()

    plt.show()


if __name__ == "__main__":
    simulate_and_draw()