from fastapi import APIRouter, Depends, HTTPException

from escarpolette.player import State, get_player, Player
from escarpolette.schemas import PlayerSchema

router = APIRouter()


@router.get("/", response_model=PlayerSchema)
def get(player: Player = Depends(get_player)) -> PlayerSchema:
    data = PlayerSchema(state=player.get_state().name)
    return data


@router.patch("/", responses={400: {}})
def patch(data: PlayerSchema, player: Player = Depends(get_player)) -> None:
    if data.state == State.PLAYING:
        player.play()
    elif data.state == State.PAUSED:
        player.pause()
    else:
        raise HTTPException(
            status_code=400, detail=f"The state {data.state} cannot be set"
        )
