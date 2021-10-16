from game.collectibles.factory import GateFactories
from game.map.tiles import *
from game.map.tiles import Enemy as EnemyTile
from util.my_random import RandomManager as RM


class Room(ABC):
    INNER_WIDTH = 5                 # width inside the room, i.e. without walls and hallways
    INNER_HEIGHT = INNER_WIDTH      # height inside the room, i.e. without walls and hallways
    OUTER_WIDTH = INNER_WIDTH + 3   # width of the whole room area, i.e. with walls and hallways
    OUTER_HEIGHT = INNER_HEIGHT + 3 # height of the whole room area, i.e. with walls and hallways
    ROOM_WIDTH = INNER_WIDTH + 2    # width of the whole room, i.e. with walls but without hallways
    ROOM_HEIGHT = INNER_HEIGHT + 2  # height of the whole room, i.e. with walls but without hallways
    MID_X = int(ROOM_WIDTH / 2)     # middle of the room on the x-axis
    MID_Y = int(ROOM_HEIGHT / 2)    # middle of the room on the y-axis

    @staticmethod
    def get_empty_room_tile_list() -> "list of Tiles":
        return [Floor()] * (Room.INNER_WIDTH * Room.INNER_HEIGHT)

    @staticmethod
    def dic_to_tile_list(tile_dic: "dic of Coordinate and Tile") -> "list of Tiles":
        tile_list = Room.get_empty_room_tile_list()
        if tile_dic is not None:
            for coordinate, tile in tile_dic.items():
                index = coordinate.y * Room.INNER_WIDTH + coordinate.x
                if 0 <= index < len(tile_list):
                    tile_list[index] = tile
                else:
                    raise IndexError(f"Invalid Index ({index} for tile_list of length {len(tile_list)}!")
        return tile_list

    def __init__(self, tile_list: "list of Tiles", east_door: Door = None, south_door: Door = None,
                 west_door: bool = False, north_door: bool = False):
        self.__tiles = []
        top = [ Wall() for t in range(Room.ROOM_WIDTH) ]
        # Add an additional invisible Tile so we have space for hallways. We only need this on the right side and
        # bottom of a room since the hallways at the top or left of the room will be displayed in the neighbouring
        # room.
        top.append(Void())
        self.__tiles.append(top)

        # fence the room tiles with Walls
        for y in range(Room.INNER_HEIGHT):
            row = [Wall()]
            for x in range(Room.INNER_WIDTH):
                if tile_list is not None:
                    index = x + y * Room.INNER_WIDTH
                    if index < len(tile_list):
                        row.append(tile_list[index])
                else:
                    row.append(Floor())
            row.append(Wall())
            row.append(Void()) # again append an invisible Tile to the right
            self.__tiles.append(row)

        room_bottom = [ Wall() for t in range(Room.ROOM_WIDTH) ]
        room_bottom.append(Void())
        # append the visible row at the bottom for potential hallways
        bottom = [ Void() for t in range(Room.OUTER_WIDTH)]

        self.__tiles.append(room_bottom)
        self.__tiles.append(bottom)
        self.__is_in_sight = False
        self.__is_visible = False
        self.__was_visited = False

        # North and West doors must be defined in the neighboring room, because that room creates the hallway
        # South and East doors are created and placed into a hallway
        if north_door:
            self.__tiles[0][Room.MID_X] = Floor()
        if west_door:
            self.__tiles[Room.MID_Y][0] = Floor()
        if east_door is not None:
            if east_door.direction != Direction.East:
                Logger.instance().error(f"Found room with a east_door not pointing East!\n{self}")
            self.__tiles[Room.MID_Y-1][Room.ROOM_WIDTH] = Wall()
            self.__tiles[Room.MID_Y][Room.ROOM_WIDTH-1] = Floor()   # remove the wall in front of the hallway
            self.__tiles[Room.MID_Y][Room.ROOM_WIDTH] = east_door
            self.__tiles[Room.MID_Y+1][Room.ROOM_WIDTH] = Wall()
        if south_door is not None:
            if south_door.direction != Direction.South:
                Logger.instance().error(f"Found room with a south_door not pointing South!\n{self}")
            self.__tiles[Room.ROOM_HEIGHT][Room.MID_X-1] = Wall()
            self.__tiles[Room.ROOM_HEIGHT-1][Room.MID_X] = Floor()  # remove the wall in front of the hallway
            self.__tiles[Room.ROOM_HEIGHT][Room.MID_X] = south_door
            self.__tiles[Room.ROOM_HEIGHT][Room.MID_X+1] = Wall()

    def _set_tile(self, tile: Tile, x: int, y: int) -> bool:
        """

        :param tile: the Tile we want to place
        :param x: horizontal position of the Tile
        :param y: vertical position of the Tile
        :return: whether we could place the Tile at the given position or not
        """
        if 0 <= x < Room.OUTER_WIDTH and 0 <= y < Room.OUTER_HEIGHT:
            self.__tiles[y][x] = tile
            return True
        return False

    def get_row(self, y: int) -> "list of Tiles":
        if 0 <= y < Room.OUTER_HEIGHT:
            row = []
            for x in range(len(self.__tiles[y])):
                row.append(self.at(x = x, y = y))
            return row
        else:
            return Room.OUTER_HEIGHT * [Invalid()]

    def at(self, x: int, y: int, force: bool = False) -> Tile:
        """

        :param x: horizontal position of the Tile we want to know
        :param y: vertical position of the Tile we want to know
        :param force: whether we return the real Tile or not (e.g. invisible Rooms usually return Fog)
        :return: the Tile at the requested position
        """
        if 0 <= x < Room.OUTER_WIDTH and 0 <= y < Room.OUTER_HEIGHT:
            if self.__is_visible or force:
                return self.__tiles[y][x]
            elif x < Room.ROOM_WIDTH and y < Room.ROOM_HEIGHT:
                return FogOfWar()
            else:
                return Void()   # don't display possible hallways
        else:
            return Invalid()

    def in_sight(self):     # todo use later to display hallways of neighbouring rooms
        self.__is_in_sight = True

    def enter(self):
        self.__is_visible = True
        self.__was_visited = True

    def leave(self, direction: Direction):
        pass

    @abstractmethod
    def __str__(self):
        pass


class SpecialRoom(Room, ABC):
    def __init__(self, door: Door, tile_dic: "dic of Coordinate and Tile"):
        tile_list = Room.dic_to_tile_list(tile_dic)
        if door.direction == Direction.East:
            super().__init__(tile_list, east_door=door)
        elif door.direction == Direction.South:
            super().__init__(tile_list, south_door=door)
        elif door.direction == Direction.West:
            super().__init__(tile_list, west_door=True)
        else:
            super().__init__(tile_list, north_door=True)


class SpawnRoom(Room):
    def __init__(self, player: Player, tile_dic: "dic of Coordinate and Tile" = None, east_door: Door = None,
                 south_door: Door = None, west_door: bool = False, north_door: bool = False):    # todo add type to player; always spawn at center?
        tile_list = Room.dic_to_tile_list(tile_dic)
        super().__init__(tile_list, east_door, south_door, west_door, north_door)

    def __str__(self):
        return "SR"


class WildRoom(Room):
    def __init__(self, factory: EnemyFactory, chance: float = 0.4, east_door: Door = None,
                 south_door: Door = None, west_door: bool = False, north_door: bool = False):
        self.__dictionary = { 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [] }
        tile_list = []
        rm = RM.create_new()
        for x in range(Room.INNER_WIDTH * Room.INNER_HEIGHT):
            if rm.get() < chance:
                id = rm.get_int(min=0, max=10)
                enemy = EnemyTile(factory, self.get_tiles_by_id, id)
                if id > 0:
                    self.__dictionary[id].append(enemy)
                tile_list.append(enemy)
            else:
                tile_list.append(Floor())

        super().__init__(tile_list, east_door, south_door, west_door, north_door)

    def __str__(self):
        return "WR"

    def get_tiles_by_id(self, id: int) -> "list of EnemyTiles":
        return self.__dictionary[id]


class GateRoom(SpecialRoom):
    def __init__(self, door: Door, tile_dic: "dic of Coordinate and Tile" = None):
        super().__init__(door, tile_dic)
        factory = GateFactories.standard_factory()
        self._set_tile(Collectible(factory), x=Room.MID_X, y=Room.MID_Y)

    def __str__(self) -> str:
        return "GR"


class RiddleRoom(Room):
    pass


class ShopRoom(SpecialRoom):
    def __init__(self, door: Door, inventory: "list of ShopItems",
                 visit_shop_callback: "void(Player, list of ShopItems)", tile_dic: "dic of Coordinate and Tile" = None):
        super().__init__(door, tile_dic)
        self._set_tile(ShopKeeper(visit_shop_callback, inventory), Room.MID_X, Room.MID_Y)

    def __str__(self):
        return "$R"


class TreasureRoom(SpecialRoom):
    pass


class BossRoom(SpecialRoom):
    def __init__(self, door: Door, boss: Boss, tile_dic: "dic of Coordinate and Tile" = None):
        super().__init__(door, tile_dic)
        self._set_tile(boss, x=Room.MID_X, y=Room.MID_Y)

    def __str__(self) -> str:
        return "BR"
