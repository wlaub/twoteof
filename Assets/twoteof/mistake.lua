

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
    local hero = getFlag('eow_sd_active')


    wait(2)
    if hero then
        miniTextbox('waldmo_BadEnd_3')
        setFlag('hero_achievement')
    else
        if second_time then
            miniTextbox('waldmo_BadEnd_2')
        else
            miniTextbox('waldmo_BadEnd')
        end
    end

    wait(5)


end


function onEnd(room, wasSkipped)
    completeArea(true, false, true)
end

