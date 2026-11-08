# HDBaseT Matrix for Home Assistant

Local control of the **Foxun 4x4 4K HDBaseT HDMI Matrix** (and other white-label 4x4 HDBaseT matrices
built on the same hardware) whose web page is titled "HDBaseT Matrix" and is driven by
`TimSendCmd.CGI` / `VIDDivSta.CGI` style CGI endpoints.

Developed and tested against a Foxun 4x4 4K HDBaseT matrix.

The integration **reads the matrix's real state** (routing, output power, audio, EDID), so changes made from the
front panel or IR remote show up in Home Assistant.

## Features

Per output:
- `media_player` with power on/off and source (input) selection
- `select` for the routed input
- `switch` for output power
- `switch` for output audio (config)

Per input:
- `select` for EDID (Default EDID 1-12, User EDID 1-3, copy from output). On the units tested, EDID 10 is 4K and EDID 1 is 1080p.

Every command response from the matrix carries fresh status, so entities update immediately; the matrix is also polled
(default every 10 s) to catch changes from elsewhere.

## Install

**HACS:** add this repository as a custom repository (category *Integration*), install, restart Home Assistant.

**Manual:** copy `custom_components/hdbaset_matrix` into your `config/custom_components/` and restart.

Then *Settings -> Devices & services -> Add integration -> HDBaseT Matrix* and enter the matrix IP address.

## Options

*Configure* on the integration lets you name the 4 inputs and 4 outputs (entity names and source lists use these) and
set the poll interval.

## Protocol notes

| Request | Response |
|---|---|
| `GET /VIDDivSta.CGI?<rnd>` | `VidSta=O1OFF&O2ON&O3ON&O4OFF&O1I1&O2I1&O3I2&O4I1` |
| `GET /AUDDivSta.CGI?<rnd>` | `AudSta=O1AOFF&O2AOFF&O3AOFF&O4AON` |
| `GET /EDIDDivSta.CGI?<rnd>` | `EdidSta=EDIDD1&EDIDU1&EDIDD2&EDIDD2` (per input) |
| `GET /NETDivSta.CGI?<rnd>` | `NetSta=<mac>&<ip>&<mask>&<gw>&<port>&STATICIP` |
| `GET /TimSendCmd.CGI?button=O2I3+<rnd>` | route output 2 to input 3 (`O2ON` / `O2OFF` for power) |
| `GET /AudSendCmd.CGI?button=O2AON+<rnd>` | output audio on/off |
| `GET /EdidsendCmd.CGI?button=EDIDD10IN1+<rnd>` | set input 1 EDID |

The device has no authentication; keep it on a trusted network.

## License

MIT
