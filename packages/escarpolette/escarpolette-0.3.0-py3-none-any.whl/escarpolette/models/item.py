from sqlalchemy import text

from escarpolette.extensions import db
from escarpolette.models.base_model_mixin import BaseModelMixin


class Item(BaseModelMixin, db.Model):
    artist = db.Column(db.String(255))
    duration = db.Column(db.Integer)
    played = db.Column(db.Boolean, default=False, server_default=text("FALSE"))
    title = db.Column(db.String(255))
    url = db.Column(db.String(255), unique=True)
    user_id = db.Column(db.String(36), index=True, nullable=False)
    playlist_id = db.Column(
        db.Integer,
        db.ForeignKey("playlist.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    playlist = db.relationship("Playlist", back_populates="items",)
