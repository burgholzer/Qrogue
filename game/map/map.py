
import game.map.tiles as tiles
from game.actors.factory import EnemyFactory, DummyFightDifficulty
from game.map.navigation import Coordinate, Direction
from game.map.rooms import Room
from game.map.tutorial import Tutorial
from util.config import MapConfig
from util.logger import Logger
from util.my_random import RandomManager


class Map:
    WIDTH = 5
    HEIGHT = 5

    def __init__(self, seed: int, width: int, height: int, player: tiles.Player,
                 start_fight_callback: "void(Player, Enemy, Direction)",
                 visit_shop_callback: "void(Player, list of ShopItems)"):
        self.__player = player
        self.__start_fight_callback = start_fight_callback
        self.__visit_shop_callback = visit_shop_callback
        self.__enemy_factory = EnemyFactory(self.__start_fight_callback, DummyFightDifficulty())

        if seed == MapConfig.tutorial_seed():
            self.__build_tutorial_map(self.__player)
        else:
            rand = RandomManager.instance()
            for y in range(height):
                row = []
                for x in range(width):
                    if y == 0 or y == height - 1 or x == 0 or x == width - 1:
                        row.append(tiles.Wall())
                    else:
                        if rand.get_int(max=7) == 1:
                            row.append(tiles.Obstacle())
                        else:
                            row.append(tiles.Floor())
                self.__player_pos = Coordinate(2, 3)

    def __build_tutorial_map(self, player: tiles.Player):
        self.__rooms, spawn_point = Tutorial().create_tutorial_map(player, self.__start_fight_callback,
                                                                   self.__visit_shop_callback)
        self.__cur_room = self.__rooms[spawn_point.y][spawn_point.x]
        self.__player_pos = Map.__calculate_pos(spawn_point, Coordinate(Room.MID_X, Room.MID_Y))
        self.__cur_room.enter()

    def __get_room(self, x: int, y: int) -> (Room, Coordinate):
        """
        Calculates and returns the Room and in-room Coordinates of the given Map position.
        :param x: x position on the Map
        :param y: y position on the Map
        :return: Room and in-room Coordinate corresponding to the x and y position
        """
        room_x = int(x / Room.OUTER_WIDTH)
        room_y = int(y / Room.OUTER_HEIGHT)
        pos_x = int(x % Room.OUTER_WIDTH)
        pos_y = int(y % Room.OUTER_HEIGHT)

        return self.__rooms[room_y][room_x], Coordinate(x=pos_x, y=pos_y)

    @staticmethod
    def __calculate_pos(pos_of_room: Coordinate, pos_in_room: Coordinate) -> Coordinate:
        """
        Calculates and returns a Coordinate on the Map corresponding to the Cooridante of a Room on the Map and
        a Coordinate in the Room.

        :param pos_of_room: Coordinate of the Room on the Map
        :param pos_in_room: Coordinate in the Room
        :return: Coordinate on the Map
        """
        x = pos_of_room.x * Room.OUTER_WIDTH + pos_in_room.x
        y = pos_of_room.y * Room.OUTER_HEIGHT + pos_in_room.y
        return Coordinate(x, y)

    @property
    def height(self) -> int:
        return Map.HEIGHT * Room.OUTER_HEIGHT

    @property
    def width(self) -> int:
        return Map.WIDTH * Room.OUTER_WIDTH

    def at(self, x: int, y: int, force: bool = False) -> tiles.Tile:
        """

        :param x: horizontal position on the Map
        :param y: vertical position on the Map
        :param force: whether we force to get the real Tile or not (e.g. Fog of war, Player in front)
        :return: Tile at the corresponding position
        """
        if not force and x == self.__player_pos.x and y == self.__player_pos.y:
            return self.__player

        if 0 <= x < self.width and 0 <= y < self.height:
            room, pos = self.__get_room(x=x, y=y)
            if room is None:
                return tiles.Void()
            else:
                return room.at(x=pos.x, y=pos.y, force=force)
        else:
            Logger.instance().error(f"Error! Invalid position: {x}|{y}")
            return tiles.Invalid()

    @property
    def player(self) -> tiles.Player:
        return self.__player

    def move(self, direction: Direction) -> bool:
        """
        Tries to move the player into the given Direction.
        :param direction: in which direction the player should move
        :return: True if the player was able to move, False otherwise
        """
        new_pos = self.__player_pos + direction
        if new_pos.y < 0 or self.height <= new_pos.y or \
                new_pos.x < 0 or self.width <= new_pos.x:
            return False

        tile = self.at(x=new_pos.x, y=new_pos.y, force=True)
        if tile.is_walkable(direction, self.__player.player):
            room, pos = self.__get_room(new_pos.x, new_pos.y)
            if room != self.__cur_room: # todo what if room is None?
                self.__cur_room.leave(direction)
                self.__cur_room = room
                self.__cur_room.enter()

            if isinstance(tile, tiles.WalkTriggerTile):
                tile.on_walk(direction, self.player.player)

            self.__player_pos = new_pos
            return True
        else:
            return False
