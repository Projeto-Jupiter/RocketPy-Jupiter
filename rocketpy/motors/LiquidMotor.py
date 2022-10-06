# -*- coding: utf-8 -*-

__author__ = "Giovani Hidalgo Ceotto, Oscar Mauricio Prada Ramirez, João Lemes Gribel Soares, Mateus Stano and Pedro Henrique Marinho Bressan"
__copyright__ = "Copyright 20XX, RocketPy Team"
__license__ = "MIT"

from abc import ABC, abstractmethod

import numpy as np
from scipy import integrate

from rocketpy.Function import Function
from rocketpy.motors import Motor
from rocketpy.supplement import Disk, Cylinder, Hemisphere

# @Stano
class LiquidMotor(Motor):
    def __init__(
        self,
        thrustSource,
        burnOut,
        nozzleRadius,
        throatRadius,
        reshapeThrustCurve=False,
        interpolationMethod="linear",
    ):

        super.__init__()
        self.tanks = []
        pass

    def evaluateMassFlowRate(self):
        pass

    def evaluateCenterOfMass(self):
        pass

    def evaluateInertiaTensor(self):
        pass

    def addTank(self, tank, position):
        self.tanks.append({"tank": tank, "position": position})


class Tank(ABC):
    def __init__(self, name, diameter, height, gas, liquid=0, endcap="flat"):
        self.name = name
        self.diameter = diameter
        self.height = height
        self.gas = gas
        self.liquid = liquid

        self.capMap = {
            "flat": Disk(diameter / 2),
            "spherical": Hemisphere(diameter / 2),
        }
        self.cylinder = Cylinder(diameter / 2, height)
        self.cap = self.capMap.get(endcap)
        pass

    @abstractmethod
    def mass(self, t):
        """Returns the total mass of liquid and gases inside the tank as a
        function of time.

        Parameters
        ----------
        time : float
            Time in seconds.

        Returns
        -------
        Function
            Mass of the tank as a function of time. Units in kg.
        """
        pass

    @abstractmethod
    def netMassFlowRate(self, t):
        """Returns the net mass flow rate of the tank as a function of time.
        Net mass flow rate is the mass flow rate exiting the tank minus the
        mass flow rate entering the tank, including liquids and gases.

        Parameters
        ----------
        time : float
            Time in seconds.

        Returns
        -------
        Function
            Net mass flow rate of the tank as a function of time.
        """
        pass

    @abstractmethod
    def liquidVolume(self, t):
        """Returns the volume of liquid inside the tank as a function
        of time.

        Parameters
        ----------
        time : float
            Time in seconds.

        Returns
        -------
        Function
            Tank's liquid volume as a function of time.
        """
        pass

    def centerOfMass(self, t):
        """Returns the center of mass of the tank's fluids as a function of
        time.

        Parameters
        ----------
        time : float
            Time in seconds.

        Returns
        -------
        Function
            Center of mass of the tank's fluids as a function of time.
        """
        liquid_volume = self.liquidVolume(t)
        if liquid_volume < self.cap.volume:
            self.cap.filled_volume = liquid_volume
            return self.cap.filled_centroid
        else:
            self.cylinder.filled_volume = liquid_volume - self.cap.volume

            cylinder_mass = self.cylinder.filled_volume * self.liquid.density
            cap_mass = self.cap.volume * self.liquid.density

            return (
                self.cap.centroid * cap_mass + self.cylinder.centroid * cylinder_mass
            ) / (cap_mass + cylinder_mass)

    def inertiaTensor(self, t):
        """Returns the inertia tensor of the tank's fluids as a function of
        time.

        Parameters
        ----------
        time : float
            Time in seconds.

        Returns
        -------
        Function
            Inertia tensor of the tank's fluids as a function of time.
        """

        liquid_volume = self.liquidVolume(t)
        self.cylinder.filled_volume = liquid_volume - self.cap.volume

        cylinder_mass = self.cylinder.filled_volume * self.liquid.density

        # for a solid cylinder, ixx = iyy = mr²/4 + ml²/12
        self.inertiaI = cylinder_mass * (self.diameter**2 + self.cylinder.filled_height**2 / 12)

        # fluids considered inviscid so no shear resistance from torques in z axis
        self.inertiaZ = 0

        return [self.inertiaI, self.inertiaZ]


# @MrGribel
class MassFlowRateBasedTank(Tank):
    def __init__(
        self,
        name,
        diameter,
        height,
        endcap,
        initial_liquid_mass,
        initial_gas_mass,
        liquid_mass_flow_rate_in,
        gas_mass_flow_rate_in,
        liquid_mass_flow_rate_out,
        gas_mass_flow_rate_out,
        liquid,
        gas,
    ):
        super().__init__(name, diameter, height, endcap, gas, liquid)

        self.initial_liquid_mass = initial_liquid_mass
        self.initial_gas_mass = initial_gas_mass

        self.gas_mass_flow_rate_in = Function(
            gas_mass_flow_rate_in,
            "Time (s)",
            "Inlet Gas Propellant Mass Flow Rate (kg/s)",
            "linear",
            "constant",
        )

        self.gas_mass_flow_rate_out = Function(
            gas_mass_flow_rate_out,
            "Time (s)",
            "Outlet Gas Propellant Mass Flow Rate (kg/s)",
            "linear",
            "constant",
        )

        self.liquid_mass_flow_rate_in = Function(
            liquid_mass_flow_rate_in,
            "Time (s)",
            "Inlet Liquid Propellant Mass Flow Rate (kg/s)",
            "linear",
            "constant",
        )

        self.liquid_mass_flow_rate_out = Function(
            liquid_mass_flow_rate_out,
            "Time (s)",
            "Outlet Liquid Propellant Mass Flow Rate (kg/s)",
            "linear",
            "constant",
        )

    def netMassFlowRate(self):
        """Returns the net mass flow rate of the tank as a function of time.
        Net mass flow rate is the mass flow rate exiting the tank minus the
        mass flow rate entering the tank, including liquids and gases.

        Parameters
        ----------
        time : float
            Time in seconds.

        Returns
        -------
        Function
            Net mass flow rate of the tank as a function of time.
        """

        self.liquid_net_mass_flow_rate = (
            self.liquid_mass_flow_rate_in - self.liquid_mass_flow_rate_out
        )

        self.gas_net_mass_flow_rate = (
            self.gas_mass_flow_rate_in - self.gas_mass_flow_rate_out
        )

        self.net_mass_flow_rate = (
            self.liquid_net_mass_flow_rate + self.gas_net_mass_flow_rate
        )

        return self.net_mass_flow_rate

    def mass(self):
        """Returns the total mass of liquid and gases inside the tank as a
        function of time.

        Parameters
        ----------
        time : float
            Time in seconds.

        Returns
        -------
        Function
            Mass of the tank as a function of time. Units in kg.
        """

        # solve ODE's for liquid and gas masses
        sol = integrate.solve_ivp(
            lambda t, y: (
                self.liquid_net_mass_flow_rate(t),
                self.gas_net_mass_flow_rate(t),
            ),
            (0, self.net_mass_flow_rate.source[:, 0][-1]),
            (self.initial_liquid_mass, self.initial_gas_mass),
            vectorized=True,
        )

        self.liquid_mass = Function(
            np.column_stack((sol.t, sol.y[0])),
            "Time (s)",
            "Liquid Propellant Mass In Tank (kg)",
        )

        self.gas_mass = Function(
            np.column_stack((sol.t, sol.y[1])),
            "Time (s)",
            "Gas Propellant Mass In Tank (kg)",
        )

        self.mass = self.liquid_mass + self.gas_mass

        return self.mass


# @phmbressan
class UllageBasedTank(Tank):
    def __init__(
        self,
        name,
        diameter,
        height,
        endcap,
        liquid,
        gas,
        ullage,
    ):
        super().__init__(name, diameter, height, endcap, gas, liquid)
        pass


# @ompro07
class MassBasedTank(Tank):
    def __init__(
        self,
        name,
        diameter,
        height,
        endcap,
        liquid_mass,
        gas_mass,
        liquid,
        gas,
    ):
        super().__init__(name, diameter, height, endcap, gas, liquid)
        pass