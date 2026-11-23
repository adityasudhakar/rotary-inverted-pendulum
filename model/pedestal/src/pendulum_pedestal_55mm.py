from cadgen import step, stl
from geometry import make_pedestal

@step(out="../STEP/pendulum_pedestal_55mm.step")
@stl(out="../STL/pendulum_pedestal_55mm.stl", mesh_tolerance=0.0003)
def pendulum_pedestal_55mm():
    return make_pedestal()

if __name__ == "__main__":
    pendulum_pedestal_55mm()
