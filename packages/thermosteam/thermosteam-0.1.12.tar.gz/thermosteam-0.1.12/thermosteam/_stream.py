# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 02:34:56 2019

@author: yoelr
"""
import numpy as np
from . import indexer
from . import equilibrium as eq
from . import functional as fn
from .base import units_of_measure as thermo_units, convert
from .exceptions import DimensionError
from ._thermal_condition import ThermalCondition
from .utils import Cache, assert_same_chemicals, thermo_user, registered

__all__ = ('Stream', )


# %% Utilities

mol_units = indexer.ChemicalMolarFlowIndexer.units
mass_units = indexer.ChemicalMassFlowIndexer.units
vol_units = indexer.ChemicalVolumetricFlowIndexer.units

# %%
@thermo_user
@registered(ticket_name='s')
class Stream:
    """
    Create a Stream object that defines material flow rates
    along with its thermodynamic state. Thermodynamic and transport
    properties of a stream are available as properties, while
    thermodynamic equilbrium (e.g. VLE, and bubble and dew points)
    are available as methods. 

    Parameters
    ----------
    ID='' : str, defaults to a unique ID
        A unique identification. If ID is None, stream will not be
        registered.

    flow=() : tuple, optional
        All flow rates corresponding to chemical `IDs`.

    phase='l' : {'l', 'g', 's'}, optional
        Either gas ("g"), liquid ("l"), or solid ("s").

    T=298.15 : float, optional
        Temperature (K).

    P=101325 : float, optional
        Pressure (Pa).

    units='kmol/hr' : str, optional
        Flow rate units of measure (only mass, molar, and
        volumetric flow rates are valid)

    price=0 : float, optional
        Price in USD/kg.
    
    thermo=() : Thermo, defaults to settings.thermo
        Thermodynamic equilibrium package.
    
    **chemical_flows : float
                   ID - flow pairs
    
    Examples
    --------
    Before creating a stream, first set the chemicals:
        
    >>> import thermosteam as tmo
    >>> chemicals = tmo.Chemicals(['Water', 'Ethanol'])
    >>> tmo.settings.set_thermo(chemicals)
    
    Create a stream, defining the thermodynamic condition and flow rates:
        
    >>> s1 = tmo.Stream(ID='s1',
    ...                 Water=20, Ethanol=10, units='kg/hr',
    ...                 T=298.15, P=101325, phase='l')
    >>> s1.show(flow='kg/hr') # Use the show method to select units of display
    Stream: s1
     phase: 'l', T: 298.15 K, P: 101325 Pa
     flow (kg/hr): Water    20
                   Ethanol  10
    
    All flow rates are stored as an array in the `mol` attribute:
    
    >>> s1.mol # Molar flow rates [kmol/hr]
    array([1.11 , 0.217])
    
    The temperature, pressure and phase are attributes as well:
    
    >>> (s1.T, s1.P, s1.phase)
    (298.15, 101325, 'l')
    
    The most convinient way to get and set flow rates is through
    the `get_flow` and `set_flow` methods:
    
    >>> # Set flow
    >>> s1.set_flow(1, 'gpm', 'Water')
    >>> s1.get_flow('gpm', 'Water')
    1.0
    >>> # Set multiple flows
    >>> s1.set_flow([10, 20], 'kg/hr', ('Ethanol', 'Water'))
    >>> s1.get_flow('kg/hr', ('Ethanol', 'Water'))
    array([10., 20.])
    
    Thermodynamic properties are available as stream properties:
    
    >>> s1.H # Enthalpy (kJ/hr)
    0.0
    
    Note that the reference enthalpy is 0.0 at the reference
    temperature and pressure of 298.15 K, and 101325 Pa.
    Retrive the enthalpy at a 1 C.
    
    >>> s1.T += 10
    >>> s1.H
    1083.4675869330183
    
    Other thermodynamic properties are temperature and pressure dependent as well:
    
    >>> s1.rho # Density [kg/m3]
    916.3494714517071
    
    It may be more convinient to get properties with different units:
        
    >>> s1.get_property('rho', 'g/cm3')
    0.9163494714517073
    
    It is also possible to set some of the properties in different units:
        
    >>> s1.set_property('T', 40, 'degC')
    >>> s1.T
    313.15
    
    Bubble point and dew point computations can be performed through stream methods:
        
    >>> bp = s1.bubble_point_at_P() # Bubble point at constant pressure
    >>> bp
    BubblePointValues(T=357.0881141715846, P=101325, IDs=('Water', 'Ethanol'), z=[0.836 0.164], y=[0.49 0.51])
    
    The bubble point results contain all results as attributes:
    
    >>> bp.T # Temperature [K]
    357.0881141715846
    >>> bp.y # Vapor composition
    array([0.49, 0.51])
    
    Vapor-liquid equilibrium can be performed by setting 2 degrees of freedom from the following list:
    * T [Temperature; in K]
    * P [Pressure; in K]
    * V [Vapor fraction]
    * H [Enthalpy; in kJ/hr]
    
    Set vapor fraction and pressure of the stream:
        
    >>> s1.vle(P=101325, V=0.5)
    >>> s1.show()
    MultiStream: s1
     phases: ('g', 'l'), T: 364.8 K, P: 101325 Pa
     flow (kmol/hr): (g) Water     0.4721
                         Ethanol   0.1916
                     (l) Water     0.6381
                         Ethanol   0.02551
    
    Note that the stream is a now a MultiStream to manage multiple phases.
    Each phase can be accessed separately too:
    
    >>> s1['l'].show()
    Stream: 
     phase: 'l', T: 364.8 K, P: 101325 Pa
     flow (kmol/hr): Water    0.638
                     Ethanol  0.0255
    
    >>> s1['g'].show()
    Stream: 
     phase: 'g', T: 364.8 K, P: 101325 Pa
     flow (kmol/hr): Water    0.472
                     Ethanol  0.192
    
    """
    __slots__ = ('_ID', '_imol', '_TP', '_thermo', '_streams',
                 '_bubble_point_cache', '_dew_point_cache',
                 '_vle_cache', '_sink', '_source', 'price')
    line = 'Stream'
    
    #: [DisplayUnits] Units of measure for IPython display (class attribute)
    display_units = thermo_units.DisplayUnits(T='K', P='Pa',
                                              flow=('kmol/hr', 'kg/hr', 'm3/hr'),
                                              N=5)

    _flow_cache = {}

    def __init__(self, ID='', flow=(), phase='l', T=298.15, P=101325., units='kmol/hr',
                 price=0., thermo=None, **chemical_flows):
        self._TP = ThermalCondition(T, P)
        thermo = self._load_thermo(thermo)
        self._init_indexer(flow, phase, thermo.chemicals, chemical_flows)
        #: [float] Price in USD/kg
        self.price = price 
        if units != 'kmol/hr':
            name, factor = self._get_flow_name_and_factor(units)
            flow = getattr(self, name)
            flow[:] = self.mol * factor
        self._sink = self._source = None # For BioSTEAM
        self._init_cache()
        self._register(ID)
    
    def _init_indexer(self, flow, phase, chemicals, chemical_flows):
        """Initialize molar flow rates."""
        if flow is ():
            if chemical_flows:
                imol = indexer.ChemicalMolarFlowIndexer(phase, chemicals=chemicals, **chemical_flows)
            else:
                imol = indexer.ChemicalMolarFlowIndexer.blank(phase, chemicals)
        else:
            assert not chemical_flows, ("may specify either 'flow' or "
                                        "'chemical_flows', but not both")
            if isinstance(flow, indexer.ChemicalMolarFlowIndexer):
                imol = flow 
                imol.phase = phase
            else:
                imol = indexer.ChemicalMolarFlowIndexer.from_data(
                    np.asarray(flow, dtype=float), phase, chemicals)
        self._imol = imol

    def _init_cache(self):
        self._bubble_point_cache = Cache(eq.BubblePoint)
        self._dew_point_cache = Cache(eq.DewPoint)

    @classmethod
    def _get_flow_name_and_factor(cls, units):
        cache = cls._flow_cache
        if units in cache:
            name, factor = cache[units]
        else:
            dimensionality = thermo_units.get_dimensionality(units)
            if dimensionality == mol_units.dimensionality:
                name = 'mol'
                factor = mol_units.conversion_factor(units)
            elif dimensionality == mass_units.dimensionality:
                name = 'mass'
                factor = mass_units.conversion_factor(units)
            elif dimensionality == vol_units.dimensionality:
                name = 'vol'
                factor = vol_units.conversion_factor(units)
            else:
                raise DimensionError(f"dimensions for flow units must be in molar, "
                                     f"mass or volumetric flow rates, not '{dimensionality}'")
            cache[units] = name, factor
        return name, factor

    ### Property getters ###

    def get_flow(self, units, IDs=...):
        """
        Return an array of flow rates in requested units.
        
        Parameters
        ----------
        units : str
            Units of measure.
        IDs : Iterable[str] or str, optional
            Chemical identifiers.

        Examples
        --------
        >>> import thermosteam as tmo
        >>> chemicals = tmo.Chemicals(['Water', 'Ethanol'])
        >>> tmo.settings.set_thermo(chemicals)
        >>> s1 = tmo.Stream('s1', Water=20, Ethanol=10, units='kg/hr')
        >>> s1.get_flow('kg/hr', 'Water')
        20.0

        """
        name, factor = self._get_flow_name_and_factor(units)
        indexer = getattr(self, 'i' + name)
        return factor * indexer[IDs]
    
    def set_flow(self, data, units, IDs=...):
        """
        Set flow rates in given units.

        Parameters
        ----------
        data : 1d ndarray or float
            Flow rate data.
        units : str
            Units of measure.
        IDs : Iterable[str] or str, optional
            Chemical identifiers.

        Examples
        --------
        >>> import thermosteam as tmo
        >>> chemicals = tmo.Chemicals(['Water', 'Ethanol'])
        >>> tmo.settings.set_thermo(chemicals)
        >>> s1 = tmo.Stream(ID='s1',
        ...                 Water=20, Ethanol=10, units='kg/hr',
        ...                 T=298.15, P=101325, phase='l')
        >>> s1.set_flow(10, 'kg/hr', 'Water')
        >>> s1.get_flow('kg/hr', 'Water')
        10.0

        """
        name, factor = self._get_flow_name_and_factor(units)
        indexer = getattr(self, 'i' + name)
        indexer[IDs] = np.asarray(data, dtype=float) / factor
    
    def get_total_flow(self, units):
        """
        Get total flow rate in given units.

        Parameters
        ----------
        units : str
            Units of measure.

        Examples
        --------
        >>> import thermosteam as tmo
        >>> chemicals = tmo.Chemicals(['Water', 'Ethanol'])
        >>> tmo.settings.set_thermo(chemicals)
        >>> s1 = tmo.Stream('s1', Water=20, Ethanol=10, units='kg/hr')
        >>> s1.get_total_flow('kg/hr')
        30.0

        """
        name, factor = self._get_flow_name_and_factor(units)
        flow = getattr(self, 'F_' + name)
        return factor * flow
    
    def set_total_flow(self, value, units):
        """
        Set total flow rate in given units keeping the composition constant.

        Parameters
        ----------
        value : float
            New total flow rate.
        units : str
            Units of measure.

        Examples
        --------
        >>> import thermosteam as tmo
        >>> chemicals = tmo.Chemicals(['Water', 'Ethanol'])
        >>> tmo.settings.set_thermo(chemicals)
        >>> s1 = tmo.Stream('s1', Water=20, Ethanol=10, units='kg/hr')
        >>> s1.set_total_flow(1.0,'kg/hr')
        >>> s1.get_total_flow('kg/hr')
        0.9999999999999999

        """
        name, factor = self._get_flow_name_and_factor(units)
        setattr(self, 'F_' + name, value / factor)
    
    def get_property(self, name, units):
        """
        Return property in requested units.

        Parameters
        ----------
        name : str
            Name of stream property.
        units : str
            Units of measure.

        Examples
        --------
        >>> import thermosteam as tmo
        >>> chemicals = tmo.Chemicals(['Water', 'Ethanol'])
        >>> tmo.settings.set_thermo(chemicals) 
        >>> s1 = tmo.Stream('s1', Water=20, Ethanol=10, units='kg/hr')
        >>> s1.get_property('sigma', 'N/m') # Surface tension
        0.06384967976396348

        """
        units_dct = thermo_units.stream_units_of_measure
        if name in units_dct:
            original_units = units_dct[name]
        else:
            raise ValueError(f"no property with name '{name}'")
        value = getattr(self, name)
        factor = original_units.conversion_factor(units)
        return value * factor
    
    def set_property(self, name, value, units):
        """
        Set property in given units.

        Parameters
        ----------
        name : str
            Name of stream property.
        value : str
            New value of stream property.
        units : str
            Units of measure.

        Examples
        --------
        >>> import thermosteam as tmo
        >>> chemicals = tmo.Chemicals(['Water', 'Ethanol'])
        >>> tmo.settings.set_thermo(chemicals) 
        >>> s1 = tmo.Stream('s1', Water=20, Ethanol=10, units='kg/hr')
        >>> s1.set_property('P', 2, 'atm')
        >>> s1.P
        202650.0

        """
        units_dct = thermo_units.stream_units_of_measure
        if name in units_dct:
            original_units = units_dct[name]
        else:
            raise ValueError(f"no property with name '{name}'")
        if name == 'T':
            value = convert(value, units, 'K')
        else:
            factor = original_units.conversion_factor(units)
            value /= factor
        setattr(self, name, value)
    
    ### Stream data ###

    @property
    def thermal_condition(self):
        """ [ThermalCondition] Contains the temperature and pressure conditions of the stream."""
        return self._TP

    @property
    def T(self):
        """[float] Temperature in Kelvin."""
        return self._TP.T
    @T.setter
    def T(self, T):
        self._TP.T = T
    
    @property
    def P(self):
        """[float] Pressure in Pascal."""
        return self._TP.P
    @P.setter
    def P(self, P):
        self._TP.P = P
    
    @property
    def phase(self):
        """Phase of stream."""
        return self._imol._phase.phase
    @phase.setter
    def phase(self, phase):
        self._imol._phase.phase = phase
    
    @property
    def mol(self):
        """[array] Molar flow rates in kmol/hr."""
        return self._imol._data
    @mol.setter
    def mol(self, value):
        mol = self.mol
        if mol is not value:
            mol[:] = value
    
    @property
    def mass(self):
        """[property_array] Mass flow rates in kg/hr."""
        return self.imass._data
    @mass.setter
    def mass(self, value):
        mass = self.mass
        if mass is not value:
            mass[:] = value
    
    @property
    def vol(self):
        """[property_array] Volumetric flow rates in m3/hr."""
        return self.ivol._data
    @vol.setter
    def vol(self, value):
        vol = self.vol
        if vol is not value:
            vol[:] = value
        
    @property
    def imol(self):
        """[ChemicalMolarFlowIndexer] Flow rate indexer with data in kmol/hr."""
        return self._imol
    @property
    def imass(self):
        """[ChemicalMassFlowIndexer] Flow rate indexer with data in kg/hr."""
        return self._imol.by_mass()
    @property
    def ivol(self):
        """[ChemicalVolumetricFlowIndexer] Flow rate indexer with data in m3/hr."""
        return self._imol.by_volume(self._TP)
    
    ### Net flow properties ###
    
    @property
    def cost(self):
        """[float] Total cost of stream in USD/hr."""
        return self.price * self.F_mass
    
    @property
    def F_mol(self):
        """[float] Total molar flow rate in kmol/hr."""
        return self._imol._data.sum()
    @F_mol.setter
    def F_mol(self, value):
        F_mol = self.F_mol
        if not F_mol: raise AttributeError("undefined composition; cannot set flow rate")
        self._imol._data[:] *= value/F_mol
    @property
    def F_mass(self):
        """[float] Total mass flow rate in kg/hr."""
        return (self.chemicals.MW * self.mol).sum()
    @F_mass.setter
    def F_mass(self, value):
        F_mass = self.F_mass
        if not F_mass: raise AttributeError("undefined composition; cannot set flow rate")
        self.imol._data[:] *= value/F_mass
    @property
    def F_vol(self):
        """[float] Total volumetric flow rate in m3/hr."""
        return 1000. * self.mixture.V_at_TP(self.phase, self.mol, self._TP)
    @F_vol.setter
    def F_vol(self, value):
        F_vol = self.F_vol
        if not F_vol: raise AttributeError("undefined composition; cannot set flow rate")
        self.ivol._data[:] *= value / F_vol / 1000.
    
    @property
    def H(self):
        """[float] Enthalpy flow rate in kJ/hr."""
        return self.mixture.H_at_TP(self.phase, self.mol, self._TP)
    @H.setter
    def H(self, H):
        self.T = self.mixture.solve_T(self.phase, self.mol, H, self.T, self.P)

    @property
    def S(self):
        """[float] Entropy flow rate in kJ/hr."""
        return self.mixture.S_at_TP(self.phase, self.mol, self._TP)
    
    @property
    def Hf(self):
        """[float] Enthalpy of formation flow rate in kJ/hr."""
        return (self.chemicals.Hf * self.mol).sum()
    @property
    def Hc(self):
        """[float] Enthalpy of combustion flow rate in kJ/hr."""
        return (self.chemicals.Hc * self.mol).sum()    
    @property
    def Hvap(self):
        """[float] Enthalpy of vaporization flow rate in kJ/hr."""
        return self.mixture.Hvap_at_TP(self.mol, self._TP)
    
    @property
    def C(self):
        """[float] Heat capacity flow rate in kJ/hr."""
        return self.mixture.Cn_at_TP(self.phase, self.mol, self._TP)
    
    ### Composition properties ###
    
    @property
    def z_mol(self):
        """[1d array] Molar composition."""
        mol = self.mol
        z = mol / mol.sum()
        z.setflags(0)
        return z
    @property
    def z_mass(self):
        """[1d array] Mass composition."""
        mass = self.chemicals.MW * self.mol
        z = mass / mass.sum()
        z.setflags(0)
        return z
    @property
    def z_vol(self):
        """[1d array] Volumetric composition."""
        vol = self.vol.value
        z = vol / vol.sum()
        z.setflags(0)
        return z
    
    @property
    def MW(self):
        """[float] Overall molecular weight."""
        return self.F_mass / self.F_mol
    @property
    def V(self):
        """[float] Molar volume [m^3/mol]."""
        mol = self.mol
        return self.mixture.V_at_TP(self.phase, mol / mol.sum(), self._TP)
    @property
    def kappa(self):
        """[float] Thermal conductivity [W/m/k]."""
        mol = self.mol
        return self.mixture.kappa_at_TP(self.phase, mol / mol.sum(), self._TP)
    @property
    def Cn(self):
        """[float] Molar heat capacity [J/mol/K]."""
        mol = self.mol
        return self.mixture.Cn_at_TP(self.phase, mol / mol.sum(), self._TP)
    @property
    def mu(self):
        """[float] Hydrolic viscosity [Pa*s]."""
        mol = self.mol
        return self.mixture.mu_at_TP(self.phase, mol / mol.sum(), self._TP)
    @property
    def sigma(self):
        """[float] Surface tension [N/m]."""
        mol = self.mol
        return self.mixture.sigma_at_TP(mol / mol.sum(), self._TP)
    @property
    def epsilon(self):
        """[float] Relative permittivity [-]."""
        mol = self.mol
        return self.mixture.epsilon_at_TP(mol / mol.sum(), self._TP)
    
    @property
    def Cp(self):
        """[float] Heat capacity [J/g/K]."""
        return self.Cn / self.MW
    @property
    def alpha(self):
        """[float] Thermal diffusivity [m^2/s]."""
        return fn.alpha(self.kappa, self.rho, self.Cp)
    @property
    def rho(self):
        """[float] Density [kg/m^3]."""
        return fn.V_to_rho(self.V, self.MW)
    @property
    def nu(self):
        """[float] Kinematic viscosity [-]."""
        return fn.mu_to_nu(self.mu, self.rho)
    @property
    def Pr(self):
        """[float] Prandtl number [-]."""
        return fn.Pr(self.Cp, self.mu, self.k)
    
    ### Stream methods ###
    
    def mix_from(self, others):
        """
        Mix all other streams into this one, ignoring its initial contents.
        
        Examples
        -------
        >>> import thermosteam as tmo
        >>> chemicals = tmo.Chemicals(['Water', 'Ethanol'])
        >>> tmo.settings.set_thermo(chemicals) 
        >>> s1 = tmo.Stream('s1', Water=20, Ethanol=10, units='kg/hr')
        >>> s2 = s1.copy()
        >>> s1.mix_from([s1, s2])
        >>> s1.show(flow='kg/hr')
        Stream: s1
         phase: 'l', T: 298.15 K, P: 101325 Pa
         flow (kg/hr): Water    40
                       Ethanol  20
        
        """
        others = [i for i in others if i]
        if len(others) == 1:
            self.copy_like(others[0])
        else:
            assert_same_chemicals(self, others)
            phase = others[0].phase
            self.phase = phase
            self.mol[:] = sum([i.mol for i in others])
            self.H = sum([i.H for i in others])
    
    def split_to(self, s1, s2, split):
        """
        Split molar flow rate from this stream to two others given
        the split fraction or an array of split fractions.
        
        Examples
        --------
        >>> import thermosteam as tmo
        >>> chemicals = tmo.Chemicals(['Water', 'Ethanol'])
        >>> tmo.settings.set_thermo(chemicals) 
        >>> s = tmo.Stream('s', Water=20, Ethanol=10, units='kg/hr')
        >>> s1 = tmo.Stream('s1')
        >>> s2 = tmo.Stream('s2')
        >>> split = chemicals.kwarray(dict(Water=0.5, Ethanol=0.1))
        >>> s.split_to(s1, s2, split)
        >>> s1.show(flow='kg/hr')
        Stream: s1
         phase: 'l', T: 298.15 K, P: 101325 Pa
         flow (kg/hr): Water    10
                       Ethanol  1
        
        >>> s2.show(flow='kg/hr')
        Stream: s2
         phase: 'l', T: 298.15 K, P: 101325 Pa
         flow (kg/hr): Water    10
                       Ethanol  9
        
        
        """
        mol = self.mol
        s1.mol[:] = dummy = mol * split
        s2.mol[:] = mol - dummy
        
    def link_with(self, other, flow=True, phase=True, TP=False):
        assert isinstance(other, self.__class__), "other must be of same type to link with"
        
        if TP and flow and phase:
            self._imol._data_cache = other._imol._data_cache
        else:
            self._imol._data_cache.clear()
        
        if TP:
            self._TP = other._TP
        if flow:
            self._imol._data = other._imol._data
        if phase:
            self._imol._phase = other._imol._phase
            
    def unlink(self):
        self._imol._data_cache.clear()
        self._TP = self._TP.copy()
        self._imol._data = self._imol._data.copy()
        self._imol._phase = self._imol._phase.copy()
        self._init_cache()
    
    def copy_like(self, other):
        self._imol.copy_like(other._imol)
        self._TP.copy_like(other._TP)
    
    def copy_flow(self, stream, IDs=..., *, remove=False, exclude=False):
        """Copy flow rates of stream to self.
        
        Parameters
        ----------
        stream : Stream
            Flow rates will be copied from here.
        IDs=... : iterable[str], defaults to all chemicals.
            Chemical IDs. 
        remove=False: bool, optional
            If True, copied chemicals will be removed from `stream`.
        exclude=False: bool, optional
            If True, exclude designated chemicals when copying.
        
        """
        chemicals = self.chemicals
        mol = stream.mol
        if exclude:
            IDs = chemicals.get_index(IDs)
            index = np.ones(chemicals.size, dtype=bool)
            index[IDs] = False
        else:
            index = chemicals.get_index(IDs)
        
        self.mol[index] = mol[index]
        if remove: 
            if isinstance(stream, ms.MultiStream):
                mol[..., index] = 0
            else:
                mol[index] = 0
    
    def copy(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new._sink = new._source = new._ID = None
        new._thermo = self._thermo
        new._imol = self._imol.copy()
        new._TP = self._TP.copy()
        new._init_cache()
        new.price = 0
        return new
    __copy__ = copy
    
    def flow_proxy(self):
        cls = self.__class__
        new = cls.__new__(cls)
        new._sink = new._source = new._ID = None
        new.price = 0
        new._thermo = self._thermo
        new._imol = imol = self._imol._copy_without_data(self._imol)
        imol._data = self._imol._data
        new._TP = self._TP.copy()
        new._init_cache()
        return new
    
    def empty(self):
        self._imol._data[:] = 0
    
    ### Equilibrium ###

    @property
    def vle(self):
        self.phases = 'gl'
        return self.vle

    @property
    def equilibrim_chemicals(self):
        chemicals = self.chemicals
        chemicals_tuple = chemicals.tuple
        indices = chemicals.get_equilibrium_indices(self.mol != 0)
        return [chemicals_tuple[i] for i in indices]
    
    def get_bubble_point(self, IDs=None):
        chemicals = self.chemicals.retrieve(IDs) if IDs else self.equilibrim_chemicals
        bp = self._bubble_point_cache.reload(chemicals, self._thermo)
        return bp
    
    def get_dew_point(self, IDs=None):
        chemicals = self.chemicals.retrieve(IDs) if IDs else self.equilibrim_chemicals
        dp = self._dew_point_cache.reload(chemicals, self._thermo)
        return dp
    
    def bubble_point_at_T(self, T=None, IDs=None):
        bp = self.get_bubble_point(IDs)
        z = self.get_molar_composition(bp.IDs)
        return bp(z, T=T or self.T)
    
    def bubble_point_at_P(self, P=None, IDs=None):
        bp = self.get_bubble_point(IDs)
        z = self.get_molar_composition(bp.IDs)
        return bp(z, P=P or self.P)
    
    def dew_point_at_T(self, T=None, IDs=None):
        dp = self.get_dew_point(IDs)
        z = self.get_molar_composition(dp.IDs)
        return dp(z, T=T or self.T)
    
    def dew_point_at_P(self, P=None, IDs=None):
        dp = self.get_dew_point(IDs)
        z = self.get_molar_composition(dp.IDs)
        return dp(z, P=P or self.P)
    
    def get_normalized_mol(self, IDs):
        z = self.imol[IDs]
        z /= z.sum()
        return z
    
    def get_normalized_mass(self, IDs):
        z = self.imass[IDs]
        z /= z.sum()
        return z
    
    def get_normalized_vol(self, IDs):
        z = self.ivol[IDs]
        z /= z.sum()
        return z
    
    def get_molar_composition(self, IDs):
        return self.imol[IDs]/self.F_mol
    
    def get_mass_composition(self, IDs):
        return self.imass[IDs]/self.F_mass
    
    def get_volumetric_composition(self, IDs):
        return self.ivol[IDs]/self.F_vol
    
    def get_concentration(self, IDs):
        return self.imol[IDs]/self.F_vol
    
    def recieve_vent(self, other):
        bp = other.bubble_point_at_T()
        index = self.chemicals.get_index(bp.IDs)
        mol = self.mol
        mol_old = mol[index]
        mol[index] = mol_new = self.F_mol * bp.y * bp.P / self.P
        other.mol[index] += mol_old - mol_new 
    
    ### Casting ###
    
    @property
    def phases(self):
        raise AttributeError(f"'{type(self).__name__}' object has no attribute 'phases'")
    @phases.setter
    def phases(self, phases):
        self.__class__ = ms.MultiStream
        self._imol = self._imol.to_material_indexer(phases)
        self._streams = {}
        self._vle_cache = Cache(eq.VLE, self._imol, self._TP, thermo=self._thermo,
                                bubble_point_cache=self._bubble_point_cache,
                                dew_point_cache=self._dew_point_cache)
    
    ### Representation ###
    
    def _basic_info(self):
        return type(self).__name__ + ': ' + (self.ID or '') + '\n'
    
    def _info_phaseTP(self, phase, T_units, P_units):
        T = thermo_units.convert(self.T, 'K', T_units)
        P = thermo_units.convert(self.P, 'Pa', P_units)
        s = '' if isinstance(phase, str) else 's'
        return f" phase{s}: {repr(phase)}, T: {T:.5g} {T_units}, P: {P:.6g} {P_units}\n"
    
    def _info(self, T, P, flow, N):
        """Return string with all specifications."""
        from .indexer import nonzeros
        basic_info = self._basic_info()
        IDs = self.chemicals.IDs
        data = self.imol.data
        IDs, data = nonzeros(IDs, data)
        IDs = tuple(IDs)
        display_units = self.display_units
        T_units = T or display_units.T
        P_units = P or display_units.P
        flow_units = flow or display_units.flow
        N = N or display_units.N
        basic_info += self._info_phaseTP(self.phase, T_units, P_units)
        len_ = len(IDs)
        if len_ == 0:
            return basic_info + ' flow: 0' 
        
        # Start of third line (flow rates)
        name, factor = self._get_flow_name_and_factor(flow_units)
        indexer = getattr(self, 'i' + name)
        beginning = f' flow ({flow_units}): '
            
        # Remaining lines (all flow rates)
        new_line_spaces = len(beginning) * ' '
        flow_array = factor * indexer[IDs]
        flowrates = ''
        lengths = [len(i) for i in IDs]
        maxlen = max(lengths) + 1
        _N = N - 1
        for i in range(len_-1):
            spaces = ' ' * (maxlen - lengths[i])
            if i == _N:
                flowrates += '...\n' + new_line_spaces
                break
            flowrates += IDs[i] + spaces + f' {flow_array[i]:.3g}\n' + new_line_spaces
        spaces = ' ' * (maxlen - lengths[len_-1])
        flowrates += IDs[len_-1] + spaces + f' {flow_array[len_-1]:.3g}'
        return (basic_info 
              + beginning
              + flowrates)

    def show(self, T=None, P=None, flow=None, N=None):
        """Print all specifications.
        
        Parameters
        ----------
        T: str, optional
            Temperature units.
        P: str, optional
            Pressure units.
        flow: str, optional
            Flow rate units.
        N: int, optional
            Number of compounds to display.
        
        Notes
        -----
        Default values are stored in `Stream.display_units`.
        
        """
        print(self._info(T, P, flow, N))
    _ipython_display_ = show
    
    def print(self):
        from .utils import repr_IDs_data, repr_kwarg
        chemical_flows = repr_IDs_data(self.chemicals.IDs, self.mol)
        price = repr_kwarg('price', self.price)
        print(f"{type(self).__name__}(ID={repr(self.ID)}, phase={repr(self.phase)}, T={self.T:.2f}, "
              f"P={self.P:.6g}{price}{chemical_flows})")
        
from . import _multi_stream as ms
del registered