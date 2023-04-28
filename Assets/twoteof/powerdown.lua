

function onBegin()
    setFlag('twoteof_powerdown', true)
    disableMovement()
    sound = celeste.Audio.Play('event:/new_content/game/10_farewell/fakeheart_get')

    instantTeleportTo(40.0, player.Position.Y)


    player.Dashes=1
--    player.Hair.Color=player.UsedHairColor
    player.DummyGravity=false
    player.DummyAutoAnimate=false
    engine.TimeRate=0.2
    player.Sprite:Play('spin',false,false)
    player.Speed.Y=0
    setPlayerState(11)
    player.Speed.Y=0
 
    wait(0.25)
    engine.TimeRate=0.35
    player.Speed.Y=0   
    wait(0.5)
    engine.TimeRate=0.5
    player.Speed.Y=0   
    wait(0.5)
    engine.TimeRate=0.75
    wait(1.0)
    engine.TimeRate=1
    player.Speed.X=-100   
    wait(1.5)
    setBloomStrength(0.1)
    engine.TimeRate=2
    wait(2.5)
    setBloomStrength(0.2)
    engine.TimeRate=4
    wait(9)
    setBloomStrength(0.3)   
    engine.TimeRate=8
    wait(20)
    setBloomStrength(10.0)       

--    celeste.Audio.Play('event:/game/06_reflection/boss_spikes_burst')
--    wait(.5)


    wait(4)
    wait(1)

    player.Sprite:Play('fallSlow',false,false)
    wait(1)
    player.DummyGravity=true
    celeste.Audio.Stop(sound)       

    engine.TimeRate=0.1
    player.Dashes=0
    waitUntilOnGround()
    setPlayerState(0)   
end


function onEnd(room, wasSkipped)
    player.Dashes=0
    setFlag('_twoteof_powerdown', false)
    setBloomStrength(0.0)       
    engine.TimeRate=1
    enableMovement()
    celeste.Audio.Stop(sound)   
end

