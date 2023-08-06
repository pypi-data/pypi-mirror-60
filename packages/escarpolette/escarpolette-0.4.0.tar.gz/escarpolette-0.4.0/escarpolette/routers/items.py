from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .dependencies import get_db, get_current_playlist
from escarpolette.login import get_current_user, User
from escarpolette.models import Item, Playlist
from escarpolette.player import get_player, Player
from escarpolette.schemas.item import ItemSchemaIn, ItemSchemaOut
from escarpolette.schemas.playlist import PlaylistSchemaOut
from escarpolette.tools import get_content_metadata
from escarpolette.rules import rules

router = APIRouter()


@router.get("/", response_model=PlaylistSchemaOut)
def get(db: Session = Depends(get_db)) -> PlaylistSchemaOut:
    playlist = PlaylistSchemaOut()

    for item in db.query(Item).order_by(Item.created_at).all():
        playlist.items.append(
            ItemSchemaOut(
                artist=item.artist,
                duration=item.duration,
                title=item.title,
                url=item.url,
            )
        )
        if item.played:
            playlist.idx += 1

    return playlist


@router.post("/", status_code=201, response_model=ItemSchemaOut)
def post(
    data: ItemSchemaIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    playlist: Playlist = Depends(get_current_playlist),
    player: Player = Depends(get_player),
) -> Item:
    metadata = get_content_metadata(data.url)
    item = Item(user_id=current_user.id, playlist=playlist, **metadata)

    if not rules.can_add_item(current_user, item, db):
        raise TooManyRequests

    playlist.items.append(item)
    db.add(playlist)
    db.flush()

    player.add_item(item.url)

    db.commit()

    return item
