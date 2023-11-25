
local room_struct = require("structs.room")
local tiles_struct = require("structs.tiles")
local logging = require("logging")
local state = require("loaded_state")
local map_item_utils = require("map_item_utils")
local utils = require("utils")

local script = {
    name = "import_room",
    displayName = "Import Room",
    parameters = {
        source_fg = "",
        source_bg = "",
        },
    fieldInformation = {
        source_fg = {
            fieldType = "loennScripts.directFilepath",
            extension = "*"
            },
        source_bg = {
            fieldType = "loennScripts.directFilepath",
            extension = "*"
            },
 
        },
    tooltip = "Create a room from a file containing dimensions and a string of tiles"
}

function script.run(room, args)

    local file = io.open(args.source_fg)
    local raw_fg = file:read("*a")
    file:close()


    file = io.open(args.source_bg)
    local raw_bg = file:read("*a")
    file:close()

    local room_name = 'g-import'

    local new_room = state.getRoomByName(room_name)
    if new_room == nil then
        new_room = utils.deepcopy(room)
    end

    new_room.name = room_name
    new_room.entities = {}
    new_room.triggers = {}
    new_room.decalsFg = {}
    new_room.decalsBg = {}

    room_struct.directionalResize(new_room, "up", -room.height/8)
    room_struct.directionalResize(new_room, "left", -room.width/8)

    logging.info(raw)

    local tiles = tiles_struct.decode({innerText = raw_fg})
    local w,h = tiles.matrix:size()

    room_struct.directionalResize(new_room, "up", h)
    room_struct.directionalResize(new_room, "left", w)

    new_room["tilesFg"] = tiles

    tiles = tiles_struct.decode({innerText = raw_bg})
    w,h = tiles.matrix:size()

    new_room["tilesBg"] = tiles


    map_item_utils.addRoom(state.map, new_room)

end

return script
