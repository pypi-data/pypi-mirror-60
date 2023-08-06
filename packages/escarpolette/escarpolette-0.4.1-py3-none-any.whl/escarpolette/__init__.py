from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from escarpolette import db, routers
from escarpolette.models import Playlist
from escarpolette.settings import Config
from escarpolette.player import get_player


def create_new_playlist(db: Session):
    playlist = Playlist()
    db.add(playlist)
    db.commit()


def create_app(config: Config):
    app = FastAPI(
        title="Escarpolette",
        version="0.1",
        description="Manage your party's playlist without friction",
    )

    routers.init_app(app)
    db.init_app(config)
    get_player().init_app(config)

    @app.on_event("shutdown")
    def shutdown():
        get_player().shutdown()

    with db.get_db() as db_session:
        create_new_playlist(db_session)

    app.add_middleware(
        CORSMiddleware, allow_credentials=True, allow_methods=["*"], allow_origins=["*"]
    )

    return app
