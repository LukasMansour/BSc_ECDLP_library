from typing import Callable


def default_name_filter(name: str) -> bool:
    # if name in {"BasicIncrementer", "BasicConstantAdderIP",
    #             "HRSComparator", "HRSConstantModularAdderIP",
    #             "TTKAdderIP", "FullSubtractionComparator",
    #             "RNSLModularAdderIP", "RNSLModularDoublerIP",
    #             "HRSConstantModularMultiplierOOP", "PZModularMultiplierOOP"
    #             "HRSConstantModularMultiplierIP", "FermatModularInversion", "RNSLECPointAdderIP"}:
    #     return True
    # else:
    #     return False
    return True


def custom_name_filter(names: set[str]) -> Callable[[str], float]:
    def delta(name: str) -> bool:
        if name in names:
            return True
        else:
            return False

    return delta
