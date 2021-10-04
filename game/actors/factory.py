
from game.actors.player import Player as PlayerActor
from game.actors.enemy import Enemy as EnemyActor, DummyEnemy
from game.callbacks import OnWalkCallback
from game.collectibles.pickup import Coin
from game.logic.instruction import HGate
from game.logic.qubit import StateVector

from qiskit import transpile, QuantumCircuit
from qiskit.providers.aer import StatevectorSimulator

from util.my_random import RandomManager


class FightDifficulty:
    """
    A class that handles all parameters that define the difficulty of a fight
    """

    __SHOTS = 1

    def __init__(self, instruction_pool: "list of Instructions", num_of_instructions: int, reward_pool):
        """

        :param instruction_pool: list of the instructions to choose from to create a statevector
        :param num_of_instructions: num of instructions used to create a statevector
        """
        self.__instruction_pool = instruction_pool
        self.__num_of_instructions = num_of_instructions

    def create_statevector(self, num_of_qubits: int) -> StateVector:
        """

        :param num_of_qubits:
        :return:
        """
        circuit = QuantumCircuit(num_of_qubits, num_of_qubits)
        rand = RandomManager.instance()
        qubits = [i for i in range(num_of_qubits)]
        cbits = [i for i in range(num_of_qubits)]

        for i in range(self.__num_of_instructions):
            instruction = rand.get_element(self.__instruction_pool)
            inst_qubits = qubits.copy()
            inst_cbits = cbits.copy()
            for i in range(len(instruction.qargs)):
                qubit = rand.get_element(inst_qubits, remove=True)
                instruction.qargs[i] = qubit
            for i in range(len(instruction.cargs)):
                cubit = rand.get_element(inst_cbits, remove=True)
                instruction.cargs[i] = cubit

            instruction.append_to(circuit)
        simulator = StatevectorSimulator()
        compiled_circuit = transpile(circuit, simulator)
        # We only do 1 shot since we don't need any measurement but the StateVector
        job = simulator.run(compiled_circuit, shots=1)
        stv = StateVector(job.result().get_statevector())
        return stv


class DummyFightDifficulty(FightDifficulty):
    """
    Dummy implementation of a FightDifficulty class for testing.
    """

    def __init__(self):
        super(DummyFightDifficulty, self).__init__([HGate(0), HGate(1)], 2, [Coin(1), Coin(3)])


class EnemyFactory:
    def __init__(self, start_fight_callback: OnWalkCallback, difficulty: FightDifficulty):
        self.__start_fight_callback = start_fight_callback
        self.__difficulty = difficulty

    @property
    def callback(self):
        return self.__start_fight_callback

    def get_enemy(self, player: PlayerActor) -> EnemyActor:
        stv = self.__difficulty.create_statevector(player.num_of_qubits)

        return DummyEnemy(stv)
