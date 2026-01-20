import numpy as np
import pandas as pd


class Particle:
    def __init__(self, E, px, py, pz, charge):
        self.E = E
        self.px = px
        self.py = py
        self.pz = pz
        self.charge = charge
        # Initial position at the collision point (0,0,0)
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def mass(self):
        m2 = self.E ** 2 - (self.px ** 2 + self.py ** 2 + self.pz ** 2)
        return np.sqrt(max(0, m2))

    def propagate(self, b_field_z, dt, steps):
        """
        Simulates the particle's path in a magnetic field.
        Returns arrays of X, Y, Z coordinates.
        """
        trajectory_x = [self.x]
        trajectory_y = [self.y]
        trajectory_z = [self.z]

        # Constants
        c = 299792458  # Speed of light (m/s)


        # Current momentum
        curr_px = self.px
        curr_py = self.py
        curr_pz = self.pz

        # Magnetic field strength factor (simplified for simulation scale)
        # Lorentz Force causes rotation in X-Y plane
        # 0.3 is a conversion factor for B(Tesla) * R(meters) to p(GeV)
        omega = (0.3 * b_field_z * self.charge) / self.E

        for _ in range(steps):
            # Rotate momentum (Magnetic field affects direction, not speed)
            # This is a rotation matrix application for small dt
            d_phi = omega * dt  # Angle change

            new_px = curr_px * np.cos(d_phi) - curr_py * np.sin(d_phi)
            new_py = curr_px * np.sin(d_phi) + curr_py * np.cos(d_phi)

            curr_px = new_px
            curr_py = new_py

            # Update Position
            # dx = v * dt. In high energy, v approx c approx 1 (normalized)
            self.x += (curr_px / self.E) * dt
            self.y += (curr_py / self.E) * dt
            self.z += (curr_pz / self.E) * dt

            trajectory_x.append(self.x)
            trajectory_y.append(self.y)
            trajectory_z.append(self.z)

        return trajectory_x, trajectory_y, trajectory_z


class Event:
    def __init__(self, event_id):
        self.id = event_id
        self.particles = []
        self.invariant_mass = 0.0

    def add_particle(self, particle):
        self.particles.append(particle)

    def calculate_invariant_mass(self):
        if len(self.particles) < 2:
            return 0.0

        p1 = self.particles[0]
        p2 = self.particles[1]

        E_tot = p1.E + p2.E
        px_tot = p1.px + p2.px
        py_tot = p1.py + p2.py
        pz_tot = p1.pz + p2.pz

        m2 = E_tot ** 2 - (px_tot ** 2 + py_tot ** 2 + pz_tot ** 2)

        self.invariant_mass = np.sqrt(max(0, m2))
        return self.invariant_mass


class DataLoader:
    def load_cern_data(self, filepath):
        df = pd.read_csv(filepath)
        events = []

        # Limit to 1000 events for faster loading during testing
        print(f"Parsing first 1000 events from CERN data...")
        df_subset = df.head(1000)

        for index, row in df_subset.iterrows():
            event = Event(int(row['Event']))

            p1 = Particle(row['E1'], row['px1'], row['py1'], row['pz1'], row['Q1'])
            p2 = Particle(row['E2'], row['px2'], row['py2'], row['pz2'], row['Q2'])

            event.add_particle(p1)
            event.add_particle(p2)
            events.append(event)

        return events