require "math"
require "os"

local selection_tool = require("tools.selection")
local selection_util = require("selections")
local siu = require("selection_item_utils")

local script = {
    name = "jitter",
    displayName = "Jitter selection",
    tooltip = "Randomly move the selected objects",
}

function script.run(room, args)
    math.randomseed(os.time());
--    selection = selection_tool.getSelectionTargets() 
--    for _, entity in ipairs(selection) do
--        if entity._name == "VivHelper/CustomSpinner" and entity.ShatterFlag == "" then
--        if entity._name == "VivHelper/CustomSpinner" then
--        entity.ShatterFlag = "test"
--        if entity["ShatterFlag"] == "" then
--            local offset_x = math.round(math.random()*2-1);
--            local offset_y = math.round(math.random()*2-1);
--            siu.moveSelection(room, layer, entity, offset_x, offset_y)
--        end
--    end
--    selection_util.redrawTargetLayers(room, selection)

    for _,entity in ipairs(room.entities) do
        if entity._name == "VivHelper/CustomSpinner" and entity.ShatterFlag == "" then
            local offset_x = math.round(math.random()*2-1);
            local offset_y = math.round(math.random()*2-1);
            entity.x = entity.x+offset_x
            entity.y = entity.y+offset_y
        end

    end

end

return script
