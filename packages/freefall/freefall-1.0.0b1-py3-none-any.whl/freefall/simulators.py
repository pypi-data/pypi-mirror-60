"""
simulators.py

A collection of simulators and termination functions.
"""

from collections import namedtuple


SimResult = namedtuple("SimResult", ["x", "y", "vx", "vy", "ax", "ay", "t"])


def terminate_vy_less_zero(x, y, vx, vy, ax, ay, t):
    """Returns True if the y velocity is less than zero, otherwise returns False"""
    return vy[-1] < 0


def terminate_y_less_zero(x, y, vx, vy, ax, ay, t):
    """Returns True if the y velocity is less than zero, otherwise returns False"""
    return y[-1] < 0


def simulate_earth_surface(
    target,
    x_initial,
    y_initial,
    vx_initial=0,
    vy_initial=0,
    epsilon=0.001,
    gravity=9.81,
    terminator=terminate_y_less_zero,
):
    """
    Simulates the motion of an FallingObject moving through the air near the Earth's surface
    and returns a SimResult object with the FallingObject's trajectory.

    Inputs:
        target (FallingObject type): Represents the object moving through the air
        x_initial, y_initial (float or int): The position of the falling object at t=0
        vx_initial, vy_initial (optional float or int): The velocity of the falling object at
            t=0 (default is 0)
        epsilon (optional float): The size of the time step (default is 1 ms)
        gravity (optional float): The acceleration of gravity in the negative y direction
            (default is 9.81 m/s)
        terminator (optional): A function that tells the simulator when it is time to stop

    Outputs:
        SimResult type object: Contains the results of the simulation

    This simulator uses leapfrog integration:
        acceleration:   [t=0.0] ------> [t=1.0] ------> [t=2.0] ------> [t=3.0]
        velocity:               [t=0.5] ------> [t=1.5] ------> [t=2.5]------> [t=3.5]
        position:       [t=0.0] ------> [t=1.0] ------> [t=2.0] ------> [t=3.0]

    The simulator assumes that gravity and air density are constant.  All parameters are
        specified in metric units (meters, kilograms, seconds, etc.).
    """

    # Simulation results are stored in lists.  Each list represents a state variable.
    x = list()  # position in the x direction
    y = list()  # position in the y direction
    vx = list()  # velocity in the x direction
    vy = list()  # velocity in the y direction
    ax = list()  # acceleration in the x direction
    ay = list()  # acceleration in the y direction
    t = list()  # simulator time (i.e. a kind of clock)

    # Setup the initial values of the simulations
    x.append(x_initial)  # at t=0
    y.append(y_initial)  # at t=0

    ax.append(0)  # at t=0
    ay.append(-gravity)  # at t=0

    vx.append(vx_initial + (epsilon / 2.0) * ax[-1])  # at t=0.5*epsilon
    vy.append(vy_initial + (epsilon / 2.0) * ay[-1])  # at t=0.5*epsilon

    t.append(0)  # t is zero at t=0

    # Loop through the simulation
    while True:

        # Find the next position values of the target
        x.append(x[-1] + epsilon * vx[-1])
        y.append(y[-1] + epsilon * vy[-1])

        # Since aerodynamic drag only slows down targets and never speeds them up, the
        # direction of the drag force depends on the direction of travel. Find the direction
        # in the x direction.
        if vx[-1] >= 0:
            direction = -1
        else:
            direction = 1

        # Apply the drag force (in the correct direction) to the target
        a = direction * vx[-1] ** 2 * target.drag / target.mass
        ax.append(a)

        # Repeat for the y direction
        if vy[-1] >= 0:
            direction = -1
        else:
            direction = 1

        # This time apply the drag force and the effect of gravity
        a = direction * vy[-1] ** 2 * target.drag / target.mass - gravity
        ay.append(a)

        # Find the new values of velocity
        vx.append(vx[-1] + epsilon * ax[-1])
        vy.append(vy[-1] + epsilon * ay[-1])

        # Store the current simulator time
        t.append(t[-1] + epsilon)

        # Use the terminator function decide if the simulation is complete.
        if terminator(x, y, vx, vy, ax, ay, t):
            break

    # Return the results which are packaged neatly in a SimResults object
    return SimResult(x=x, y=y, vx=vx, vy=vy, ax=ax, ay=ay, t=t)
