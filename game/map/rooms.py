from game.collectibles.factory import GateFactories
from game.map.tiles import *
from game.map.tiles import Enemy as EnemyTile
from util.my_random import RandomManager as RM


class Area(ABC):
    __ID = 1
    __FOG = FogOfWar()
    __VOID = Void()

    @staticmethod
    def void() -> Void:
        return Area.__VOID

    def __init__(self, tile_matrix: "list[list[Tile]]"):
        self.__id = Area.__ID
        Area.__ID += 1

        self.__tiles = tile_matrix
        self.__width = len(tile_matrix[0])
        self.__height = len(tile_matrix)

        self.__is_in_sight = False
        self.__is_visible = False
        self.__was_visited = False

    @property
    def _id(self) -> int:
        return self.__id

    def at(self, x: int, y: int, force: bool = False) -> Tile:
        """

        :param x: horizontal position of the Tile we want to know
        :param y: vertical position of the Tile we want to know
        :param force: whether we return the real Tile or not (e.g. invisible Rooms usually return Fog)
        :return: the Tile at the requested position
        """
        if 0 <= x < self.__width and 0 <= y < self.__height:
            if self.__is_visible or force:
                return self.__tiles[y][x]
            else:
                if self.__is_in_sight:
                    return Area.__FOG
                else:
                    return Area.void()
        else:
            return Invalid()

    def make_visible(self):
        self.__is_in_sight = True
        self.__is_visible = True

    def in_sight(self):
        self.__is_in_sight = True

    def enter(self, direction: Direction):
        self.__is_visible = True
        self.__was_visited = True

    def leave(self, direction: Direction):
        pass


class Hallway(Area):
    MID_X = int(7 / 2)  # todo
    MID_Y = int(7 / 2)

    def __init__(self, door: Door):
        self.__door = door
        self.__room1 = None
        self.__room2 = None
        missing_half = int((Room.OUTER_WIDTH - 3) / 2)
        if self.is_horizontal():
            row = [Void()] * missing_half + [Wall(), door, Wall()] + [Void()] * missing_half
            super(Hallway, self).__init__([row])
        else:
            tiles = [[Void()]] * missing_half + [[Wall()], [door], [Wall()]] + [[Void()]] * missing_half
            super(Hallway, self).__init__(tiles)

    def at(self, x: int, y: int, force: bool = False) -> Tile:
        return super(Hallway, self).at(x, y, force)

    def set_room(self, room: "Room", first: bool):
        """

        :param room:
        :param first:  Rooms to the North or West are stored in room1 while the other is stored in room2
        :return:
        """
        if first:
            if self.__room1 is not None:
                stop = True
            self.__room1 = room
        else:
            if self.__room2 is not None:
                stop = True
            self.__room2 = room

    def connects_horizontally(self) -> bool:
        """

        :return: whether the Hallway connects two Rooms horizontally or not
        """
        return self.__door.direction.is_horizontal()

    def is_horizontal(self) -> bool:
        """

        :return: True if the Hallway is a row, False if it is a column
        """
        return not self.connects_horizontally()

    def in_sight(self):
        self.make_visible()
        if self.__room1:
            self.__room1.in_sight()
        else:
            Popup.message("Debug", "room1 is None!")
        if self.__room2:
            self.__room2.in_sight()
        else:
            Popup.message("Debug", "room2 is None!")

    def enter(self, direction: Direction):
        self.__room1.make_visible()
        self.__room2.make_visible()

    def room(self, first: bool):
        if first:
            return self.__room1
        else:
            return self.__room2

    def __str__(self) -> str:
        if self.connects_horizontally():
            orientation = "-"
        else:
            orientation = "|"
        return f"{self._id} {orientation} {self.__room1}, {self.__room2}"


class Room(Area):
    INNER_WIDTH = 5                 # width inside the room, i.e. without walls and hallways
    INNER_HEIGHT = INNER_WIDTH      # height inside the room, i.e. without walls and hallways
    OUTER_WIDTH = INNER_WIDTH + 2   # width of the whole room area, i.e. with walls and hallways
    OUTER_HEIGHT = INNER_HEIGHT + 2 # height of the whole room area, i.e. with walls and hallways
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

    def __init__(self, tile_list: "list of Tiles", north_hallway: Hallway = None, east_hallway: Hallway = None,
                 south_hallway: Hallway = None, west_hallway: Hallway = None):
        self.__tiles = []
        top = [ Wall() for t in range(Room.ROOM_WIDTH) ]
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
            #row.append(Void()) # again append an invisible Tile to the right
            self.__tiles.append(row)

        room_bottom = [ Wall() for t in range(Room.ROOM_WIDTH) ]
        #room_bottom.append(Void())
        # append the visible row at the bottom for potential hallways
        #bottom = [ Void() for t in range(Room.OUTER_WIDTH)]

        self.__tiles.append(room_bottom)
        #self.__tiles.append(bottom)

        self.__hallways = {}
        if north_hallway is not None and not north_hallway.connects_horizontally():
            self.__tiles[0][Room.MID_X] = Floor()
            self.__hallways[Direction.North] = north_hallway
            # this room is to the south of north_hallway and therefore its second room
            north_hallway.set_room(self, False)
        if east_hallway is not None and east_hallway.connects_horizontally():
            self.__tiles[Room.MID_Y][Room.ROOM_WIDTH-1] = Floor()
            self.__hallways[Direction.East] = east_hallway
            # this room is to the west of east_hallway and therefore its first room
            east_hallway.set_room(self, True)
        if south_hallway is not None and not south_hallway.connects_horizontally():
            self.__tiles[Room.ROOM_HEIGHT-1][Room.MID_X] = Floor()
            self.__hallways[Direction.South] = south_hallway
            # this room is to the north of south_hallway and therefore its first room
            south_hallway.set_room(self, True)
        if west_hallway is not None and west_hallway.connects_horizontally():
            self.__tiles[Room.MID_Y][0] = Floor()
            self.__hallways[Direction.West] = west_hallway
            # this room is to the east of west_hallway and therefore its second room
            west_hallway.set_room(self, False)

        super(Room, self).__init__(self.__tiles)

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

    def get_hallway(self, direction: Direction) -> Hallway:
        try:
            return self.__hallways[direction]   # todo what if direction is no valid key?
        except KeyError:
            dic = [str(self.__hallways[k]) for k in self.__hallways]
            print(f"{direction} not in {dic}")
            for key in self.__hallways:
                return self.__hallways[key]

    def enter(self, direction: Direction):
        super(Room, self).enter(direction)
        for key in self.__hallways:
            hallway = self.__hallways[key]
            hallway.in_sight()

    @abstractmethod
    def abbreviation(self) -> str:
        pass

    def __str__(self) -> str:
        return self.abbreviation() + str(self._id)


class SpecialRoom(Room, ABC):
    def __init__(self, hallway: Hallway, first: bool, tile_dic: "dic of Coordinate and Tile"):
        """

        :param hallway:
        :param first: whether the Hallway is to the East or South of this Room (and hence the Room is West or North of
                        Hallway)
        :param tile_dic:
        """
        tile_list = Room.dic_to_tile_list(tile_dic)
        if first:
            if hallway.connects_horizontally():
                super(SpecialRoom, self).__init__(tile_list, east_hallway=hallway)
            else:
                super(SpecialRoom, self).__init__(tile_list, south_hallway=hallway)
        else:
            if hallway.connects_horizontally():
                super(SpecialRoom, self).__init__(tile_list, west_hallway=hallway)
            else:
                super(SpecialRoom, self).__init__(tile_list, north_hallway=hallway)


class SpawnRoom(Room):
    def __init__(self, player: Player, tile_dic: "dic of Coordinate and Tile" = None, east_hallway: Hallway = None,
                 south_hallway: Hallway = None, west_hallway: Hallway = None, north_hallway: Hallway = None):
        # todo add type to player; always spawn at center?
        tile_list = Room.dic_to_tile_list(tile_dic)
        super().__init__(tile_list, north_hallway, east_hallway, south_hallway, west_hallway)

    def abbreviation(self):
        return "SR"


class WildRoom(Room):
    def __init__(self, factory: EnemyFactory, chance: float = 0.4, north_hallway: Hallway = None,
                 east_hallway: Hallway = None, south_hallway: Hallway = None, west_hallway: Hallway = None):
        """

        :param factory:
        :param chance:
        :param east_door: the Door connecting to the Room to the East of this one
        :param south_door: the Door connecting to the Room to the South of this one
        :param west_door: whether the Room to the West is having an east_door or not
        :param north_door:  whether the Room to the North is having a south_door or not
        """
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

        super().__init__(tile_list, north_hallway, east_hallway, south_hallway, west_hallway)

    def abbreviation(self):
        return "WR"

    def get_tiles_by_id(self, id: int) -> "list of EnemyTiles":
        return self.__dictionary[id]


class GateRoom(SpecialRoom):
    def __init__(self, hallway: Hallway, first: bool, tile_dic: "dic of Coordinate and Tile" = None):
        super().__init__(hallway, first, tile_dic)
        factory = GateFactories.standard_factory()
        self._set_tile(Collectible(factory), x=Room.MID_X, y=Room.MID_Y)

    def abbreviation(self) -> str:
        return "GR"


class RiddleRoom(SpecialRoom):
    def __init__(self, hallway: Hallway, first: bool, riddle: Riddle, open_riddle_callback: "void(Player, Riddle)",
                 tile_dic: "dic of Coordinate and Tile" = None):
        super().__init__(hallway, first, tile_dic)
        self._set_tile(Riddler(open_riddle_callback, riddle), Room.MID_X, Room.MID_Y)

    def abbreviation(self):
        return "RR"


class ShopRoom(SpecialRoom):
    def __init__(self, hallway: Hallway, first: bool, inventory: "list of ShopItems",
                 visit_shop_callback: "void(Player, list of ShopItems)", tile_dic: "dic of Coordinate and Tile" = None):
        super().__init__(hallway, first, tile_dic)
        self._set_tile(ShopKeeper(visit_shop_callback, inventory), Room.MID_X, Room.MID_Y)

    def abbreviation(self):
        return "$R"


class TreasureRoom(SpecialRoom):
    pass


class BossRoom(SpecialRoom):
    def __init__(self, hallway: Hallway, first: bool, boss: Boss, tile_dic: "dic of Coordinate and Tile" = None):
        super().__init__(hallway, first, tile_dic)
        self._set_tile(boss, x=Room.MID_X, y=Room.MID_Y)

    def abbreviation(self) -> str:
        return "BR"
