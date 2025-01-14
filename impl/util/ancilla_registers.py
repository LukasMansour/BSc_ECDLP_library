from api.CircuitNotSupportedError import CircuitNotSupportedError


def setup_anc_registers(
        required_dirty: int,
        required_clean: int,
        dirty_register: [],
        clean_register: [],
        prefer_clean=False,
) -> ([], [], [], []):
    if required_clean > len(clean_register):
        raise CircuitNotSupportedError("Required clean qubits exceeds number of clean qubits available.")

    final_clean_register = clean_register[:required_clean]
    leftover_clean_register = clean_register[required_clean:]

    if required_dirty > len(dirty_register) + len(leftover_clean_register):
        raise CircuitNotSupportedError("Required dirty qubits exceeds number of possibly dirty qubits available.")

    borrow_from_clean = max(required_dirty - len(dirty_register), 0)
    borrow_from_dirty = max(required_dirty - borrow_from_clean, 0)

    if prefer_clean:
        final_dirty_register = list(clean_register[:borrow_from_clean]) + list(dirty_register[:borrow_from_dirty])
    else:
        final_dirty_register = list(dirty_register[:borrow_from_dirty]) + list(clean_register[:borrow_from_clean])

    leftover_clean_register = leftover_clean_register[borrow_from_clean:]
    leftover_dirty_register = dirty_register[borrow_from_dirty:]

    return final_dirty_register, final_clean_register, leftover_dirty_register, leftover_clean_register
