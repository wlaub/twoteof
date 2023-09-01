
local room_struct = require("structs.room")
local tiles_struct = require("structs.tiles")

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
    print(width, height)

    max_bounds = {0,width,0, height}
    cx = math.floor((max_bounds[1] + max_bounds[0]) / 2)
    cy = math.floor((max_bounds[2] + max_bounds[3]) / 2)
    iterations = 0
    cells = {}
    cells[{cx,cy}] = true
    dead_cells = {}
    bounds = {cx, cx, cy, cy}
    while true do
        pending = {}
        no_options = true
        operation_set = {}
        expand = 0.3
        die = 0.2
        if #operation_set > 0 then
            a = 5
            expand = (a + 1) / (a + #operation_set)
        end
        for _, cell in pairs(operation_set) do
            local x, y = cell[1], cell[2]
            if #operation_set > 1 and math.random() < die then
                self.dead_cells[cell] = true
            else
                for _, direction in pairs({{1, 0}, {-1, 0}, {0, 1}, {0, -1}}) do
                    local dx, dy = direction[1], direction[2]
                    local tx, ty = x + dx, y + dy
                    if self.cells[tx, ty] then
                        goto continue
                    end
                    if self:test_maxbounds(tx, ty) then
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
                        pending[#pending + 1] = {tx, ty}
                        self:expand_bounds(tx, ty)
                    end
                    ::continue::
                end
            end
        end
        for _, cell in pairs(pending) do
            self.cells[cell] = true
        end
        iterations = iterations + 1
        if no_options or iterations > 1000 then
            break
        end
    end    





    for y = 1, height do
        for x = 1, width do
            if y == 20 then
                matrix:setInbounds(x,y,"0")
            end
        end
    end

end

return script
