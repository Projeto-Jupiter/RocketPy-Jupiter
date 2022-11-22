# -*- coding: utf-8 -*-

__author__ = "Giovani Hidalgo Ceotto"
__copyright__ = "Copyright 20XX, RocketPy Team"
__license__ = "MIT"

from rocketpy.Function import Function


class EmptyMotor:
    """Class that represents an empty motor with no mass and no thrust."""

    # TODO: This is a temporary solution. It should be replaced by a class that
    # inherits from the abstract Motor class. Currently cannot be done easily.
    def __init__(self):
        """Initializes an empty motor with no mass and no thrust."""
        self._csys = 1
        self.nozzleRadius = 0
        self.thrust = Function(0, "Time (s)", "Thrust (N)")
        self.mass = Function(0, "Time (s)", "Mass (kg)")
        self.massDot = Function(0, "Time (s)", "Mass Depletion Rate (kg/s)")
        self.burnOutTime = 1
        self.nozzlePosition = 0
        self.centerOfMass = Function(0, "Time (s)", "Mass (kg)")
        self.inertiaZ = Function(0, "Time (s)", "Moment of Inertia Z (kg m²)")
        self.inertiaI = Function(0, "Time (s)", "Moment of Inertia I (kg m²)")
        self.inertiaZDot = Function(0, "Time (s)", "Propellant Inertia Z Dot (kgm²/s)")
        self.inertiaIDot = Function(0, "Time (s)", "Propellant Inertia I Dot (kgm²/s)")