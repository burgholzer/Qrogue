
import game.map.tiles as tiles
from game.actors.factory import EnemyFactory, DummyFightDifficulty
from game.actors.player import Player as PlayerActor
from game.callbacks import CallbackPack
from game.map.navigation import Coordinate, Direction
from game.map.rooms import Room, Area
from game.map.tutorial import Tutorial, TutorialPlayer
from util.config import MapConfig
from util.logger import Logger
from util.my_random import RandomManager


class Map:
    WIDTH = 5
    HEIGHT = 3

    def __init__(self, seed: int, width: int, height: int, player: PlayerActor, cbp: CallbackPack):
        self.__player = tiles.Player(player)
        self.__cbp = cbp
        self.__enemy_factory = EnemyFactory(cbp.start_fight, DummyFightDifficulty())

        if seed == MapConfig.tutorial_seed():
            self.__build_tutorial_map()
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

    def __build_tutorial_map(self):
        self.__player = tiles.Player(TutorialPlayer())
        self.__rooms, spawn_point = Tutorial().build_tutorial_map(self.__player, self.__cbp)
        self.__cur_area = self.__rooms[spawn_point.y][spawn_point.x]
        self.__player_pos = Map.__calculate_pos(spawn_point, Coordinate(Room.MID_X, Room.MID_Y))
        self.__cur_area.enter(Direction.North)

    def __tile_at(self, x: int, y: int) -> tiles.Tile:
        #"""
        in_hallway = None
        width = Room.OUTER_WIDTH + 1
        height = Room.OUTER_HEIGHT + 1
        x_mod = x % width
        y_mod = y % height
        # position is in Hallway
        if x_mod == Room.OUTER_WIDTH:
            if y_mod == Room.OUTER_HEIGHT:
                return Area.void()
            x_mod -= 1
            in_hallway = Direction.East
        elif y_mod == Room.OUTER_HEIGHT:
            y_mod -= 1
            in_hallway = Direction.South

        room_x = int(x / width)
        room_y = int(y / height)
        room = self.__rooms[room_y][room_x]
        if room is None:
            return Area.void()

        if in_hallway:
            hallway = room.get_hallway(in_hallway)
            if hallway.is_horizontal():
                return hallway.at(x_mod, 0)
            else:
                return hallway.at(0, y_mod)
        else:
            return room.at(x_mod, y_mod)
        #"""
        #area, pos = self.__get_area(x, y)
        #if area is None:
        #    return Area.void()
        #return area.at(pos.x, pos.y)

    def __get_area(self, x: int, y: int) -> (Area, tiles.Tile):
        """
        Calculates and returns the Room and in-room Coordinates of the given Map position.
        :param x: x position on the Map
        :param y: y position on the Map
        :return: Room and in-room Coordinate corresponding to the x and y position
        """
        in_hallway = None
        width = Room.OUTER_WIDTH + 1
        height = Room.OUTER_HEIGHT + 1
        x_mod = x % width
        y_mod = y % height
        # position is in Hallway
        if x_mod == Room.OUTER_WIDTH:
            if y_mod == Room.OUTER_HEIGHT:
                return None, Area.void()
            x_mod -= 1
            in_hallway = Direction.East
        elif y_mod == Room.OUTER_HEIGHT:
            y_mod -= 1
            in_hallway = Direction.South

        room_x = int(x / width)
        room_y = int(y / height)
        room = self.__rooms[room_y][room_x]
        if room is None:
            return None, Area.void()

        if in_hallway:
            hallway = room.get_hallway(in_hallway)
            if hallway.is_horizontal():
                return hallway, hallway.at(x_mod, 0)
            else:
                return hallway, hallway.at(0, y_mod)
        else:
            return room, room.at(x_mod, y_mod)

    @staticmethod
    def __calculate_pos(pos_of_room: Coordinate, pos_in_room: Coordinate) -> Coordinate:    # todo fix
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
        return Map.HEIGHT * (Room.OUTER_HEIGHT + 1) - 1

    @property
    def width(self) -> int:
        return Map.WIDTH * (Room.OUTER_WIDTH + 1) - 1

    def tile_at(self, x: int, y: int) -> tiles.Tile:
        """

        :param x: horizontal position on the Map
        :param y: vertical position on the Map
        :return: Tile at the corresponding position
        """
        if x == self.__player_pos.x and y == self.__player_pos.y:
            return self.__player

        if 0 <= x < self.width and 0 <= y < self.height:
            return self.__tile_at(x, y)
        else:
            Logger.instance().error(f"Error! Invalid position: {x}|{y}")
            return tiles.Invalid()

    def at(self, x: int, y: int) -> (Area, tiles.Tile):
        """

        :param x: horizontal position on the Map
        :param y: vertical position on the Map
        :param force: whether we force to get the real Tile or not (e.g. Fog of war, Player in front)
        :return: Area and Tile at the corresponding position
        """
        area, tile = self.__get_area(x, y)
        if area is not None:
            return area, tile
        else:
            Logger.instance().error(f"Error! Invalid position: {x}|{y}")
            return None, tiles.Invalid()

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

        area, tile = self.at(x=new_pos.x, y=new_pos.y)
        if tile.is_walkable(direction, self.__player.player):
            if area != self.__cur_area: # todo what if area is None?
                self.__cur_area.leave(direction)
                self.__cur_area = area
                self.__cur_area.enter(direction)

            if isinstance(tile, tiles.WalkTriggerTile):
                tile.on_walk(direction, self.player.player)

            self.__player_pos = new_pos
            return True
        else:
            return False
