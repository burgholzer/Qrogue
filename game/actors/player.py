"""
Author: Artner Michael
13.06.2021
"""

from abc import ABC, abstractmethod
from qiskit import QuantumCircuit, transpile
from qiskit.providers.aer import StatevectorSimulator

from game.collectibles.collectible import Collectible, CollectibleType
from game.collectibles.pickup import Coin
from game.logic.instruction import Instruction, HGate
from game.logic.qubit import QubitSet, EmptyQubitSet, DummyQubitSet, StateVector
# from jkq import ddsim
from util.logger import Logger


class PlayerAttributes:
    """
    Is used as storage for a bunch of attributes of the player
    """

    def __init__(self, qubits: QubitSet = EmptyQubitSet(), space: int = 3):
        """

        :param qubits: the set of qubits the player is currently using
        :param space: how many instructions the player can put on their circuit
        """
        self.__space = space
        self.__qubits = qubits

    @property
    def num_of_qubits(self):
        return self.__qubits.size()

    @property
    def space(self):
        return self.__space

    @property
    def qubits(self):
        return self.__qubits


class Backpack:
    """
    Stores the Instructions for the player to use.
    """
    __CAPACITY = 4

    def __init__(self, capacity: int = __CAPACITY, content: "list of Instructions" = []):
        """

        :param capacity: how many Instructions can be stored in this Backpack
        :param content: initially stored Instructions
        """
        self.__capacity = capacity
        self.__storage = content

    def __iter__(self) -> "BackpackIterator":
        return BackpackIterator(self)

    @property
    def capacity(self) -> int:
        return self.__capacity

    @property
    def size(self) -> int:
        return len(self.__storage)

    def get(self, index: int) -> Instruction:
        if 0 <= index < self.size:
            return self.__storage[index]

    def add(self, instruction: Instruction) -> bool:
        """
        Adds an Instruction to the backpack if possible.

        :param instruction: the Instruction to add
        :return: True if there is enough capacity left to store the Instruction, False otherwise
        """
        if len(self.__storage) < self.__capacity:
            self.__storage.append(instruction)
            return True
        return False

    def remove(self, instruction: Instruction) -> bool:
        """
        Removes an Instruction from the backpack if it's present.

        :param instruction: the Instruction we want to remove
        :return: True if the Instruction is in the backpack and we were able to remove it, False otherwise
        """
        for i in range(len(self.__storage)):
            if self.__storage[i] == instruction:
                self.__storage.remove(instruction)
                return True
        try:
            self.__storage.remove(instruction)
            return True
        except ValueError:
            return False


class BackpackIterator:
    """
    Allows us to easily iterate through all the Instructions in a backpack
    """
    def __init__(self, backpack: Backpack):
        self.__index = 0
        self.__backpack = backpack

    def __next__(self) -> Instruction:
        if self.__index < self.__backpack.size:
            item = self.__backpack.get(self.__index)
            self.__index += 1
            return item
        raise StopIteration


class Player(ABC):
    def __init__(self, attributes: PlayerAttributes = PlayerAttributes(), backpack: Backpack = Backpack()):
        # initialize qubit stuff (rows)
        self.__simulator = StatevectorSimulator()#ddsim.JKQProvider().get_backend('statevector_simulator')
        self.__stv = None
        self.__attributes = attributes
        self.__backpack = backpack
        self.__qubit_indices = []
        for i in range(0, attributes.num_of_qubits):
            self.__qubit_indices.append(i)

        # initialize gate stuff (columns)
        self.__next_col = 0

        # apply gates/instructions, create the circuit
        self.__generator = None
        self.__set_generator()
        self.__circuit = None
        self.__instructions = []
        self.__apply_instructions()
        self.update_statevector()  # to initialize the statevector

        # init other stats
        self.__coin_count = 0

    @property
    def backpack(self) -> Backpack:
        return self.__backpack

    @property
    def state_vector(self) -> StateVector:
        return self.__stv

    def circuit_enumerator(self):
        return enumerate(self.__instructions)

    def __set_generator(self, instructions: "list of Instructions" = None):
        num = self.__attributes.num_of_qubits
        if num > 0:
            self.__generator = QuantumCircuit(num, num)
            if instructions is None:        # default generator
                for i in range(num):
                    self.__generator.h(i)     # HGate on every qubit
            else:
                for inst in instructions:
                    inst.append_to(self.__generator)

    def update_statevector(self) -> StateVector:
        """
        Compiles and simulates the current circuit and saves and returns the resulting StateVector
        :return: an updated StateVector corresponding to the current circuit
        """
        compiled_circuit = transpile(self.__circuit, self.__simulator)
        job = self.__simulator.run(compiled_circuit, shots=1)
        result = job.result()
        self.__stv = StateVector(result.get_statevector(self.__circuit))
        return self.__stv

    def use_instruction(self, instruction_index: int) -> bool:
        """
        Tries to put the Instruction corresponding to the given index in the backpack into the player's circuit.
        If the Instruction is already in-use (put onto the circuit) it is removed instead.

        :param instruction_index: index of the Instruction we want to use in the backpack
        :return: True if we were able to use the Instruction in our circuit
        """
        if 0 <= instruction_index < self.__backpack.size:
            instruction = self.__backpack.get(instruction_index)
            if instruction.is_used():
                self.__remove_instruction(instruction)
            else:
                if self.__next_col < self.__attributes.space:
                    self.__append_instruction(instruction)
                else:
                    return False
            return self.__apply_instructions()
        return False

    def __append_instruction(self, instruction: Instruction):
        self.__instructions.append(instruction)
        instruction.set_used(True)
        self.__next_col += 1

    def __remove_instruction(self, instruction: Instruction):
        self.__instructions.remove(instruction)
        instruction.set_used(False)
        self.__next_col -= 1

    def get_available_instructions(self) -> "list of Instructions":
        """

        :return: all Instructions that are currently available to the player
        """
        data = [] #self.__instructions.copy()
        for instruction in self.backpack:
            data.append(instruction)
        return data

    def give_collectible(self, collectible: Collectible):
        if type(collectible) is Coin:
            self.__coin_count += collectible.amount

    @property
    def num_of_qubits(self) -> int:
        return self.__attributes.num_of_qubits

    @property
    def space(self) -> int:
        return self.__attributes.space

    def __apply_instructions(self):
        if self.__generator is None:
            return False
        circuit = self.__generator.copy(name="PlayerCircuit")
        for inst in self.__instructions:
            inst.append_to(circuit)
        self.__circuit = circuit
        return True

    @staticmethod
    def __counts_to_bit_list(counts):
        counts = str(counts)
        counts = counts[1:len(counts)-1]
        arr = counts.split(':')
        if int(arr[1][1:]) != 1:
            raise ValueError(f"Function only works for counts with 1 shot but counts was: {counts}")
        bits = arr[0]
        bits = bits[1:len(bits)-1]
        list = []
        for b in bits:
            list.append(int(b))
        list.reverse()   # so that list[i] corresponds to the measured value of qi
        return list


class DummyPlayer(Player):
    __ATTR = PlayerAttributes(DummyQubitSet())
    __BACKPACK = Backpack(3, [HGate(0), HGate(0), HGate(1), HGate(2)])

    def __init__(self):
        super(DummyPlayer, self).__init__(attributes=self.__ATTR, backpack=self.__BACKPACK)

    def get_img(self):
        return "P"
