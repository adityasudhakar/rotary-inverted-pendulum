from cadgen import step, stl
from geometry import make_fit_test

@step(out="../STEP/motor_fit_test.step")
@stl(out="../STL/motor_fit_test.stl", mesh_tolerance=0.0003)
def motor_fit_test():
    return make_fit_test()

if __name__ == "__main__":
    motor_fit_test()
