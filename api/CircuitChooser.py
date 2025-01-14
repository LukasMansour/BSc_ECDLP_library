from typing import Callable

from qiskit import QiskitError

from api.CircuitComponent import CircuitComponent
from api.CircuitNotSupportedError import CircuitNotSupportedError
from api.Metrics import default_metric, gate_count_cache, gate_depth_cache, cz_count_cache, cz_depth_cache
from api.NameFilters import default_name_filter


class CircuitChooser:
    _instance = None
    _name_filter: Callable[[str], bool] = default_name_filter.__call__
    _metric: Callable[[CircuitComponent], float] = default_metric.__call__
    cache = {}

    def __new__(cls, *args, **kwargs):
        """Ensures only one instance of CircuitChooser is created (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(CircuitChooser, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.circuit_types = {}

        from impl.addition.qc.incrementer.BasicIncrementer import BasicIncrementer
        from impl.addition.qc.incrementer.HRSIncrementer import HRSIncrementer
        from impl.addition.qc.incrementer.HRSCleanIncrementer import HRSCleanIncrementer
        from impl.addition.qc.incrementer.GidneyIncrementer import GidneyIncrementer

        # Register all the circuit types we have.
        self.circuit_types["QCIncrementer"] = [
            type(BasicIncrementer(0, 0, 0, 0, 0)),
            type(HRSIncrementer(0, 0, 0, 0, 0)),
            type(HRSCleanIncrementer(0, 0, 0, 0, 0)),
            type(GidneyIncrementer(2, 0, 0, 0, 0))
        ]

        from impl.addition.qc.BasicConstantAdderIP import BasicConstantAdderIP
        from impl.addition.qc.HRSConstantAdderIP import HRSConstantAdderIP
        from impl.addition.qc.HRSCleanConstantAdderIP import HRSCleanConstantAdderIP
        from impl.addition.qc.copy_controlling.CopyCTRLConstantAdderIP import CopyCTRLConstantAdderIP

        self.circuit_types["QCAdderIP"] = [
            type(BasicConstantAdderIP(0, 0, 0, 0, 0)),
            type(HRSConstantAdderIP(0, 0, 0, 0, 0)),
            type(HRSCleanConstantAdderIP(0, 0, 0, 0, 0)),
            type(CopyCTRLConstantAdderIP(0, 0, 0, 0, 0)),
        ]

        from impl.comparator.qc.HRSComparator import HRSComparator
        from impl.comparator.qc.QiskitComparator import QiskitComparator

        self.circuit_types["QCComparator"] = [
            type(QiskitComparator(0, 0, 0, 0, 0)),
            type(HRSComparator(0, 0, 0, 0, 0)),
        ]

        from impl.addition.qc.modular.HRSConstantModularAdderIP import HRSConstantModularAdderIP
        from impl.addition.qc.modular.RCConstantModularAdderIP import RCConstantModularAdderIP

        self.circuit_types["QCModAdderIP"] = [
            type(HRSConstantModularAdderIP(0, 0, 0, 0, 0)),
            type(RCConstantModularAdderIP(0, 0, 0, 0, 0))
        ]

        from impl.addition.qq.TTKAdderIP import TTKAdderIP
        from impl.addition.qq.CDKMAdderIP import CDKMAdderIP
        from impl.addition.qq.DKRSAdderIP import DKRSAdderIP
        from impl.addition.qq.OTUSAdderIP import OTUSAdderIP

        self.circuit_types["QQAdderIP"] = [
            type(TTKAdderIP(0, 0, 0)),
            type(CDKMAdderIP(0, 1, 0)),
            type(DKRSAdderIP(0, 0, 0)),
            type(OTUSAdderIP(0, 0, 0)),
        ]

        from impl.comparator.qq.CDKMComparator import CDKMComparator
        from impl.comparator.qq.FullSubtractionComparator import FullSubtractionComparator
        from impl.comparator.qq.ParallelComparator import ParallelComparator
        from impl.comparator.qq.XLZLXComparator import XLZLXComparator

        self.circuit_types["QQComparator"] = [
            type(CDKMComparator(0, 0, 0, 0)),
            type(FullSubtractionComparator(0, 0, 0, 0)),
            type(ParallelComparator(0, 0, 0, 0)),
            type(XLZLXComparator(0, 0, 0, 0))
        ]

        from impl.addition.qq.modular.RNSLModularAdderIP import RNSLModularAdderIP

        self.circuit_types["QQModAdderIP"] = [
            type(RNSLModularAdderIP(0, 0, 0, 0, 0))
        ]

        from impl.multiplication.qc.modular.doubling.RNSLModularDoublerIP import RNSLModularDoublerIP

        self.circuit_types["QCModDoublerIP"] = [
            type(RNSLModularDoublerIP(0, 0, 0, 1, 0))
        ]

        from impl.multiplication.qc.modular.HRSConstantModularMultiplierOOP import HRSConstantModularMultiplierOOP
        from impl.multiplication.qc.modular.RCConstantModularMultiplierOOP import RCConstantModularMultiplierOOP

        self.circuit_types["QCModMulOOP"] = [
            type(HRSConstantModularMultiplierOOP(0, 0, 4, 3, 5, 0)),
            type(RCConstantModularMultiplierOOP(0, 0, 4, 3, 5, 0))
        ]

        from impl.multiplication.qc.modular.HRSConstantModularMultiplierIP import HRSConstantModularMultiplierIP

        self.circuit_types["QCModMulIP"] = [
            type(HRSConstantModularMultiplierIP(0, 5, 4, 3, 5, 0))
        ]

        from impl.multiplication.qq.inversion.FermatModularInversion import FermatModularInversion

        self.circuit_types["QQModInversionOOP"] = [
            type(FermatModularInversion(0, 0, 4, 7, 0))
        ]

        from impl.multiplication.qq.modular.PZModularMultiplierOOP import PZModularMultiplierOOP

        self.circuit_types["QQModMulOOP"] = [
            type(PZModularMultiplierOOP(0, 0, 0, 0, 0))
        ]

        from impl.multiplication.qc.modular.squaring.RNSLModularSquaringOOP import RNSLModularSquaringOOP

        self.circuit_types["QCModSquaringOOP"] = [
            type(RNSLModularSquaringOOP(0, 0, 0, 1, 0))
        ]

        from impl.addition.qc.modular.negation.RNSLModularNegationIP import RNSLModularNegationIP

        self.circuit_types["QCModularNegationIP"] = [
            type(RNSLModularNegationIP(0, 0, 0, 0, 0))
        ]

        from impl.exponentiation.qc.modular.HRSConstantModExpIP import HRSConstantModExpIP

        self.circuit_types["QCModExpIP"] = [
            type(HRSConstantModExpIP(0, 0, 0, 0, 7, 0))
        ]

        from impl.ec_point_addition.qc.RNSLECPointAdderIP import RNSLECPointAdderIP

        self.circuit_types["QCECPointAdderIP"] = [
            type(RNSLECPointAdderIP(0, 0, 0, (0, 0), 7))
        ]

    def choose_component(self, circuit_type, args: (), dirty_available: int = 0,
                         clean_available: int = 0) -> CircuitComponent:
        if self._metric is None:
            raise ValueError("Metric is not set")

        components_to_consider = []
        for constructor in self.circuit_types[circuit_type]:
            try:
                name = constructor.__name__
                if self._name_filter(name):
                    components_to_consider.append(constructor(dirty_available, clean_available, *args))
                else:
                    # print(f"{name} was not chosen due to name filter.")
                    continue
            except CircuitNotSupportedError as e:
                # print(e) # Debugging
                continue
            except Exception as e:
                # print(constructor) # Debugging
                # import traceback  # Debugging
                # traceback.print_exception(type(e), e, e.__traceback__)  # Debugging
                continue

        best_component = None
        best_value = float('inf')

        for component in components_to_consider:
            try:
                value = self._metric(component)
            except Exception as e:
                # print(component) # Debugging
                # import traceback  # Debugging
                # traceback.print_exception(type(e), e, e.__traceback__)  # Debugging
                continue
            # Check if there are even enough clean qubits
            # Then check the metric (expensive)
            # Minimize towards best circuit.
            if value <= best_value:
                best_value = value
                best_component = component
        if best_component is None:
            raise ValueError("No circuit could be found.")

        return best_component

    def clear_caches(self):
        self.cache.clear()

        gate_count_cache.clear()
        gate_depth_cache.clear()
        cz_count_cache.clear()
        cz_depth_cache.clear()
