
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
        source = "",
        room_name = "",
        },
    fieldInformation = {
        source = {
            fieldType = "loennScripts.directFilepath",
            extension = "*"
            }
        },
    tooltip = "Create a room from a file containing dimensions and a string of tiles"
}

function script.run(room, args)

    local file = io.open(args.source)
    local raw = file:read("*a")
    file:close()

    if state.getRoomByName(args.room_name) ~= nil then
        return
    end

    local new_room = utils.deepcopy(room)
    new_room.name = args.room_name
    new_room.entities = {}
    new_room.triggers = {}
    new_room.decalsFg = {}
    new_room.decalsBg = {}

    room_struct.directionalResize(new_room, "up", -room.height/8)
    room_struct.directionalResize(new_room, "left", -room.width/8)

    logging.info(raw)

    local tiles = tiles_struct.decode({innerText = raw})
    local w,h = tiles.matrix:size()

    room_struct.directionalResize(new_room, "up", h)
    room_struct.directionalResize(new_room, "left", w)

    new_room["tilesFg"] = tiles
    new_room["tilesBg"] = tiles


    map_item_utils.addRoom(state.map, new_room)

end

return script
