from escarpolette.extensions import db
from escarpolette.models.base_model_mixin import BaseModelMixin


class Playlist(BaseModelMixin, db.Model):
    items = db.relationship("Item", back_populates="playlist",)
