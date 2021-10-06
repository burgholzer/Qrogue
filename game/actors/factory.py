
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
    A class that handles all parameters that define the difficulty of a fight.
    """

    def __init__(self, instruction_pool: "list of Instructions", num_of_instructions: int, reward_pool):
        """

        :param instruction_pool: list of the instructions to choose from to create a statevector
        :param num_of_instructions: num of instructions used to create a statevector
        :param reward_pool: list of possible rewards for winning against an enemy of this difficulty
        """
        #self.__instruction_pool = instruction_pool
        self.__num_of_instructions = num_of_instructions

    def create_statevector(self, player: PlayerActor) -> StateVector:
        """
        Creates a StateVector that is reachable for the player.

        :param player: defines the number of qubits and usable instructions for creating the statevector
        :return: the created StateVector
        """
        num_of_qubits = player.num_of_qubits
        circuit = QuantumCircuit(num_of_qubits, num_of_qubits)
        rand = RandomManager.instance()
        qubits = [i for i in range(num_of_qubits)]
        cbits = [i for i in range(num_of_qubits)]

        # choose random circuits on random qubits and cbits
        for i in range(self.__num_of_instructions):
            instruction = rand.get_element(player.get_available_instructions())
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
        return StateVector(job.result().get_statevector())


class DummyFightDifficulty(FightDifficulty):
    """
    Dummy implementation of a FightDifficulty class for testing.
    """

    def __init__(self):
        super(DummyFightDifficulty, self).__init__([HGate(0), HGate(1)], 2, [Coin(1), Coin(3)])


class EnemyFactory:
    """
    This class produces enemies (actors) with a certain difficulty.
    It is used by enemy tiles to trigger a fight.
    """

    def __init__(self, start_fight_callback: OnWalkCallback, difficulty: FightDifficulty):
        """

        :param start_fight_callback: a method for starting a fight
        :param difficulty: difficulty of the enemy we produce
        """
        self.__start_fight_callback = start_fight_callback
        self.__difficulty = difficulty

    @property
    def callback(self):
        """
        :return: the callback method to start a fight
        """
        return self.__start_fight_callback

    def get_enemy(self, player: PlayerActor) -> EnemyActor:
        """
        Creates an enemy based on the number of qubits the provided player has.

        :param player: the player the enemy should fight against
        :return: a freshly created enemy
        """
        stv = self.__difficulty.create_statevector(player)

        return DummyEnemy(stv)
