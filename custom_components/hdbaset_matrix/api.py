"""Minimal async client for the HDBaseT 4x4 matrix web/CGI interface.

The matrix exposes:
  GET /VIDDivSta.CGI?<rnd>   -> VidSta=O1OFF&O2ON&O3ON&O4OFF&O1I1&O2I1&O3I2&O4I1
  GET /AUDDivSta.CGI?<rnd>   -> AudSta=O1AOFF&O2AOFF&O3AOFF&O4AON
  GET /EDIDDivSta.CGI?<rnd>  -> EdidSta=EDIDD1&EDIDU1&EDIDD2&EDIDD2   (per input)
  GET /NETDivSta.CGI?<rnd>   -> NetSta=<mac>&<ip>&<mask>&<gw>&<tcpport>&STATICIP
  GET /TimSendCmd.CGI?button=O2I1+<rnd>   (route / O2ON / O2OFF)  -> VidSta=...
  GET /AudSendCmd.CGI?button=O2AON+<rnd>                         -> AudSta=...
  GET /EdidsendCmd.CGI?button=EDIDD10IN1+<rnd>                   -> EdidSta=...
"""
from __future__ import annotations

import asyncio
import random
import re
from dataclasses import dataclass, field

import aiohttp

from .const import EDID_OPTIONS, NUM_PORTS

_TIMEOUT = aiohttp.ClientTimeout(total=5)
_ROUTE_RE = re.compile(r"^O([1-4])I([1-4])$")
_POWER_RE = re.compile(r"^O([1-4])(ON|OFF)$")
_AUDIO_RE = re.compile(r"^O([1-4])A(ON|OFF)$")
_HOST_RE = re.compile(r"^[A-Za-z0-9.\-]+(:\d{1,5})?$")


class MatrixError(Exception):
    """Raised when the matrix cannot be reached or answers unexpectedly."""


@dataclass
class MatrixState:
    """Current state of the matrix. Ports are 1-based."""

    power: dict[int, bool] = field(default_factory=dict)  # output -> on
    route: dict[int, int] = field(default_factory=dict)  # output -> input
    audio: dict[int, bool] = field(default_factory=dict)  # output -> audio on
    edid: dict[int, str] = field(default_factory=dict)  # input -> EDID code

    def apply(self, text: str) -> None:
        """Merge any *Sta=... response into this state."""
        key, _, body = text.strip().partition("=")
        parts = [p for p in body.split("&") if p]
        if key == "VidSta":
            for p in parts:
                if m := _ROUTE_RE.match(p):
                    self.route[int(m[1])] = int(m[2])
                elif m := _POWER_RE.match(p):
                    self.power[int(m[1])] = m[2] == "ON"
        elif key == "AudSta":
            for p in parts:
                if m := _AUDIO_RE.match(p):
                    self.audio[int(m[1])] = m[2] == "ON"
        elif key == "EdidSta":
            for i, p in enumerate(parts[:NUM_PORTS], start=1):
                self.edid[i] = p
        else:
            raise MatrixError(f"Unexpected response: {text[:80]!r}")


def validate_host(host: str) -> str:
    host = host.strip()
    if not _HOST_RE.match(host):
        raise ValueError("invalid host")
    return host


class MatrixClient:
    """Talks to the matrix over HTTP. Commands are serialized (the device is slow/single-threaded)."""

    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        self._session = session
        self._base = f"http://{validate_host(host)}"
        self._lock = asyncio.Lock()

    async def _get(self, path: str) -> str:
        url = f"{self._base}/{path}"
        async with self._lock:
            try:
                async with self._session.get(url, timeout=_TIMEOUT) as resp:
                    resp.raise_for_status()
                    return (await resp.text(encoding="latin-1")).strip()
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                raise MatrixError(f"Error talking to matrix: {err}") from err

    @staticmethod
    def _rnd() -> str:
        return f"{random.random():.16f}"

    async def get_mac(self) -> str:
        text = await self._get(f"NETDivSta.CGI?{self._rnd()}")
        key, _, body = text.partition("=")
        if key != "NetSta" or not body:
            raise MatrixError(f"Unexpected response: {text[:80]!r}")
        return body.split("&")[0].lower()

    async def get_state(self) -> MatrixState:
        state = MatrixState()
        for ep in ("VIDDivSta", "AUDDivSta", "EDIDDivSta"):
            state.apply(await self._get(f"{ep}.CGI?{self._rnd()}"))
        return state

    async def _cmd(self, cgi: str, button: str) -> str:
        return await self._get(f"{cgi}.CGI?button={button}+{self._rnd()}")

    @staticmethod
    def _port(n: int) -> int:
        n = int(n)
        if not 1 <= n <= NUM_PORTS:
            raise ValueError(f"port must be 1-{NUM_PORTS}")
        return n

    async def set_route(self, output: int, input_: int) -> str:
        return await self._cmd("TimSendCmd", f"O{self._port(output)}I{self._port(input_)}")

    async def set_power(self, output: int, on: bool) -> str:
        return await self._cmd("TimSendCmd", f"O{self._port(output)}{'ON' if on else 'OFF'}")

    async def set_audio(self, output: int, on: bool) -> str:
        return await self._cmd("AudSendCmd", f"O{self._port(output)}A{'ON' if on else 'OFF'}")

    async def set_edid(self, input_: int, edid: str) -> str:
        if edid not in EDID_OPTIONS:
            raise ValueError(f"unknown EDID {edid}")
        return await self._cmd("EdidsendCmd", f"{edid}IN{self._port(input_)}")
