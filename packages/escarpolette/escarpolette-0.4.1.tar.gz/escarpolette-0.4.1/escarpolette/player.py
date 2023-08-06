from enum import Enum
from subprocess import Popen
from typing import Dict, List, Optional
import json
import logging
import select
import socket

from escarpolette.settings import Config


logger = logging.getLogger(__name__)


class State(str, Enum):
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


class PlayerCommandError(ValueError):
    pass


class Player:
    """Control mpv using IPC."""

    _command_id = 0
    _mpv_ipc_socket = "/tmp/mpv-socket"
    _state = State.STOPPED
    mpv: Optional[Popen] = None
    mpv_socket: Optional[socket.socket] = None

    def init_app(self, config: Config) -> None:
        self._mpv_ipc_socket = config.MPV_IPC_SOCKET or self._mpv_ipc_socket
        self.mpv = Popen(
            [
                "mpv",
                "--idle",
                "--no-terminal",
                f"--input-ipc-server={self._mpv_ipc_socket}",
            ]
        )

    def shutdown(self) -> None:
        if self.mpv_socket is not None:
            self.mpv_socket.close()

        if self.mpv is not None:
            # TODO: find why MPV does not respond to a SIGTERM signal
            self.mpv.kill()

    def add_item(self, url: str) -> None:
        """Add a new item to the playlist.

        If the player was stopped, play the music.
        """
        if self._state == State.STOPPED:
            self._send_command("loadfile", url, "append-play")
            self._state = State.PLAYING
        else:
            self._send_command("loadfile", url, "append")

    def get_current_item_title(self) -> Optional[str]:
        """Get the current playing item's title."""
        response = self._send_command("get_property", "metadata")
        if response is not None:
            return response["data"]["title"]

        return None

    def get_state(self) -> State:
        return self._state

    def play(self) -> None:
        """Play the current playlist."""
        if self._state == State.PLAYING:
            return
        elif self._state == State.STOPPED:
            raise PlayerCommandError("The player is stopped. Add an item to play it.")
        else:
            self._send_command("cycle", "pause")

        self._state = State.PLAYING

    def pause(self) -> None:
        """Pause the current playlist."""
        if self._state == State.PAUSED:
            return
        elif self._state == State.STOPPED:
            raise PlayerCommandError("The player is stopped.")

        self._send_command("cycle", "pause")
        self._state = State.PAUSED

    @property
    def _connection(self) -> socket.socket:
        if self.mpv_socket is None:
            self.mpv_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.mpv_socket.connect(self._mpv_ipc_socket)

        return self.mpv_socket

    def _get_command_id(self) -> int:
        self._command_id += 1
        return self._command_id

    def _send_command(self, *command: str) -> Optional[Dict]:
        """Send a command to MPV and return the response."""
        command_id = self._get_command_id()
        msg = {"command": command, "request_id": command_id}
        logger.debug("Sending MPV commanv %s", msg)

        data = json.dumps(msg).encode("utf8") + b"\n"
        self._connection.sendall(data)

        return self._read_response(command_id)

    def _read_response(self, command_id: int) -> Optional[Dict]:
        data = b""
        while True:
            r, _, _ = select.select([self._connection], [], [], 1)
            if not r:
                # timeout
                return None

            data += self._connection.recv(1024)

            newline = data.find(b"\n")
            if newline == -1:
                next

            response = data[:newline]
            data = data[newline:]

            msg = json.loads(response.decode("utf8"))
            logger.debug("Received MPV response %s", msg)
            if msg.get("request_id", -1) == command_id:
                return msg


_current_player = Player()


def get_player():
    return _current_player
