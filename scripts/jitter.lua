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
    selection = selection_tool.getSelectionTargets() 
    for _, entity in ipairs(selection) do
        local offset_x = math.round(math.random()*2-1);
        local offset_y = math.round(math.random()*2-1);
        siu.moveSelection(room, layer, entity, offset_x, offset_y)
    end
    selection_util.redrawTargetLayers(room, selection)

end

return script
