

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

    wait(2)
    miniTextbox('waldmo_BadEnd')
    wait(5)


end


function onEnd(room, wasSkipped)
    completeArea(true, false, true)
end

