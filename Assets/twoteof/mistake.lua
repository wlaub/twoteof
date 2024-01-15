

function onBegin()
    disableMovement()
    disableRetry()
    disablePause()

    setPlayerState(11)

    player.DummyGravity=false
    player.DummyAutoAnimate=false
    player.DummyMoving=false
    player.Speed.Y = 0
    player.Speed.X = 0

    local second_time = getFlag('Ch1_twoteof_bad_end')

    wait(2)
    if second_time then
        miniTextbox('waldmo_BadEnd_2')
    else
        miniTextbox('waldmo_BadEnd')
    end

    wait(5)


end


function onEnd(room, wasSkipped)
    completeArea(true, false, true)
end

