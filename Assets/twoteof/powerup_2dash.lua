

function onBegin()
    setFlag('twoteof_2dash', true)
    disableMovement()
--    sound = celeste.Audio.Play('event:/new_content/game/10_farewell/fakeheart_get')
    player.Dashes=1
    engine.TimeRate=0.1
    setPlayerState(11)  
    while(not player.onGround)
    do
    wait(.01)
    engine.TimeRate=0.1
    end

    waitUntilOnGround()
    setPlayerState(0)   
end


function onEnd(room, wasSkipped)
    player.Dashes=1
    setFlag('_twoteof_2dash', false)
    engine.TimeRate=1
    enableMovement()
--    celeste.Audio.Stop(sound)   
end

