
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
    def name(self) -> str:
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


####### Single Qubit Gates #######


class XGate(Instruction):
    def __init__(self, qubit: int):
        super(XGate, self).__init__(gates.XGate(), [qubit])

    def name(self) -> str:
        return "X"

    def abbreviation(self, qubit: int = 0):
        return " X "

    def description(self) -> str:
        return "An X Gate swaps the amplitudes of |0> and |1> - in the classical world it is an Inverter."

    def copy(self) -> "Instruction":
        return XGate(self._qargs[0])


class HGate(Instruction):
    def __init__(self, qubit: int):
        super().__init__(gates.HGate(), qargs=[qubit])

    def description(self) -> str:
        return "The Hadamard Gate is often used to get Qubits into Superposition."

    def name(self) -> str:
        return "Hadamard"

    def abbreviation(self, qubit: int = 0):
        return " H "

    def copy(self) -> "Instruction":
        return HGate(self._qargs[0])


####### Double Qubit Gates #######


class SwapGate(Instruction):
    def __init__(self, q0: int, q1: int):
        super().__init__(gates.SwapGate(), qargs=[q0, q1])

    def description(self) -> str:
        return "As the name suggests, Swap Gates swap the amplitude between two Qubits."

    def name(self) -> str:
        return "Swap"

    def abbreviation(self, qubit: int = 0):
        if qubit == self._qargs[0]:
            return " S0 "
        else:
            return " S1 "

    def copy(self) -> "Instruction":
        return SwapGate(self._qargs[0], self._qargs[1])


class CXGate(Instruction):
    def __init__(self, q0: int, q1: int):
        super().__init__(gates.CXGate(), [q0, q1])

    def name(self) -> str:
        return "CX"

    def abbreviation(self, qubit: int = 0):
        if qubit == self._qargs[0]:
            return " C "
        else:
            return " X "

    def copy(self) -> "Instruction":
        return CXGate(self._qargs[0], self._qargs[1])

    def description(self) -> str:
        return f"Applies an X Gate onto q{self._qargs[1]} if q{self._qargs[0]} is True."
