
from abc import ABC, abstractmethod

import qiskit.circuit.library.standard_gates as gates
from qiskit import QuantumCircuit

from game.collectibles.collectible import Collectible, CollectibleType


class Instruction(Collectible, ABC):
    """
    Wrapper class for gates from qiskit.circuit.library with their needed arguments (qubits/cbits to apply it on)
    """
    MAX_ABBREVIATION_LEN = 5

    def __init__(self, instruction, qargs: "list of ints", cargs: "list of ints" = None):
        super().__init__(CollectibleType.Gate)
        self.__instruction = instruction
        self._qargs = qargs
        self.__used = False
        if cargs is None:
            self.__cargs = []
        else:
            self.__cargs = cargs

    def is_used(self) -> bool:
        return self.__used

    def set_used(self, used: bool):
        self.__used = used

    def append_to(self, circuit: QuantumCircuit):
        circuit.append(self.__instruction, self._qargs, self.__cargs)

    def qargs_iter(self) -> "Iterator":
        return iter(self._qargs)

    def qargs_enum(self) -> "Enumerator":
        return enumerate(self._qargs)

    @property
    def cargs(self):
        return self.__cargs

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def abbreviation(self, qubit: int = 0):
        pass

    @abstractmethod
    def copy(self) -> "Instruction":
        pass

    def __str__(self):
        text = f"{self.name()} ({self._qargs}, {self.__cargs})"
        if self.is_used():
            return f"({text})"
        else:
            return text


class HGate(Instruction):
    def __init__(self, qubit: int):
        super().__init__(gates.HGate(), qargs=[qubit])

    def name(self):
        return "Hadamard"

    def abbreviation(self, qubit: int = 0):
        return " H "

    def copy(self) -> "Instruction":
        return HGate(self._qargs[0])


class SwapGate(Instruction):
    def __init__(self, q0: int, q1: int):
        super().__init__(gates.SwapGate(), qargs=[q0, q1])

    def name(self):
        return "Swap"

    def abbreviation(self, qubit: int = 0):
        if qubit == self._qargs[0]:
            return " S0 "
        else:
            return " S1 "

    def copy(self) -> "Instruction":
        return SwapGate(self._qargs[0], self._qargs[1])
