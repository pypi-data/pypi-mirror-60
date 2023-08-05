from datetime import datetime
from sqlalchemy import text

from escarpolette.extensions import db


class BaseModelMixin:
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime,
        default=datetime.now,
        server_default=text("datetime()"),
        index=True,
        nullable=False,
    )
