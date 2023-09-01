
local room_struct = require("structs.room")
local tiles_struct = require("structs.tiles")
local logging = require("logging")

local script = {
    name = "chevycave",
    displayName = "Populate the selected room with a randomly generated cave"
}

function script.run(room)
    s,e =  string.find(room.name,"f") 
    if s ~= 1 then
        return
    end

    local matrix = room["tilesFg"].matrix
    local width, height = matrix:size()

    logging.info("test")

    max_bounds = {0,width,0, height}
    cx = math.floor((max_bounds[1] + max_bounds[2]) / 2)
    cy = math.floor((max_bounds[4] + max_bounds[3]) / 2)
    iterations = 0
    cells = {}
    cells[{cx,cy}] = true
    dead_cells = {}
    bounds = {cx, cx, cy, cy}
    no_options = false
    while iterations<20 and not no_options do
        pending = {}
        no_options = true
        operation_set = {}
        for cell,_ in pairs(cells) do
            if not dead_cells[cell] then
                operation_set[cell] = true
            end
        end
        expand = 0.3
        die = 0.2
        if #operation_set > 0 then
            a = 5
            expand = (a + 1) / (a + #operation_set)
        end
        for cell,_ in pairs(operation_set) do
            local x, y = cell[1], cell[2]
            if #operation_set > 1 and math.random() < die then
                dead_cells[cell] = true
            else
                for _, direction in pairs({{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) do
                    local dx, dy = direction[1], direction[2]
                    local tx, ty = x + dx, y + dy

                    if cells[{tx, ty}] then
                        goto continue
                    end
                    if tx <= max_bounds[1] or tx >= max_bounds[2] or ty <= max_bounds[3] or ty >= max_bounds[4] then
                        goto continue
                    end
                    no_options = false
                    local exp_eff
                    if tx ~= 0 then
                        exp_eff = expand
                    else
                        exp_eff = expand / 4
                    end
                    if math.random() < exp_eff then
                        pending[{tx,ty}] = true
                        bounds[1] = math.min(bounds[1], tx)
                        bounds[2] = math.max(bounds[2], tx)
                        bounds[3] = math.min(bounds[3], ty)
                        bounds[4] = math.max(bounds[4], ty)
                    end
                    ::continue::
                end
            end
        end
        for cell,_ in pairs(pending) do
            cells[cell] = true
        end
        iterations = iterations + 1
        if no_options then
            break
        end
    end    


    for cell,_ in pairs(cells) do
        matrix:setInbounds(cell[1], cell[2], "0")
    end


--    for y = 1, height do
--        for x = 1, width do
--            if y == 20 then
--                matrix:setInbounds(x,y,"0")
--            end
--        end
--    end

end

return script
