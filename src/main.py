from physics_engine import DataLoader


def verify_simulation():
    loader = DataLoader()

    try:
        events = loader.load_cern_data("Dimuon_DoubleMu.csv")
    except FileNotFoundError:
        print("Error: Data file not found. Run data_manager.py first.")
        return

    sample_event = events[0]
    calculated_mass = sample_event.calculate_invariant_mass()

    print("-" * 30)
    print(f"Event ID: {sample_event.id}")
    print(f"Particle 1 Energy: {sample_event.particles[0].E} GeV")
    print(f"Particle 2 Energy: {sample_event.particles[1].E} GeV")
    print("-" * 30)
    print(f"CALCULATED INVARIANT MASS: {calculated_mass:.4f} GeV")
    print("-" * 30)

    if 2.0 < calculated_mass < 120.0:
        print("✅ PHYSICS ENGINE STATUS: VERIFIED")
    else:
        print("❌ PHYSICS ENGINE STATUS: FAILED")


if __name__ == "__main__":
    verify_simulation()