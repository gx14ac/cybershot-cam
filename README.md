# CyberShot Cam

A small DIY digital camera built on an ESP32-S3 board. It has a 1.8" screen as a viewfinder, a joystick for the menu, and one shutter button. Photos go to a microSD card. You can glitch them on the camera and download them over Wi-Fi.

The firmware is by [cebola4444](https://github.com/cebola4444/cybershot-cam) (@cebolander / @lixofuturista). This fork adds:

- a wiring and soldering guide
- battery power
- a few build fixes

**Wiring guide:** https://gx14ac.github.io/cybershot-cam/wiring-guide/ (Japanese)

## Hardware

| Part | Notes |
| --- | --- |
| Freenove ESP32-S3 WROOM CAM, N16R8 | 16 MB flash, 8 MB PSRAM, OV2640 camera, onboard microSD slot |
| 1.8" SPI TFT, ST7735, 128×160 | viewfinder |
| KY-023 joystick | menu |
| Momentary push button | shutter |
| 5 mm red LED + 100 Ω resistor | flash (optional) |
| microSD card | any size |

For battery power, this fork adds:

| Part | Notes |
| --- | --- |
| 18650 cell + holder | |
| TP4056 module with protection, USB-C | charging |
| Rocker switch | power |
| MT3608 boost converter | set to 5.0 V before connecting to the board |

You also need female-female jumper wires, a soldering iron, solder, heat-shrink tubing, and a multimeter.

## Wiring

| From | To |
| --- | --- |
| LCD CS / RESET / A0 / SDA / SCK | GPIO 43 / 21 / 14 / 45 / 47 |
| LCD VCC, LED | 3V3 |
| Joystick VRx / VRy / SW | GPIO 1 / 2 / 42 |
| Joystick +5V | **3V3**, not 5V (the ADC is 3.3 V) |
| Shutter button | GPIO 41 and GND |
| Flash LED | GPIO 48 → 100 Ω → LED → GND |
| MT3608 VOUT+ / VOUT- | board 5V / GND |

The board has only one 3V3 pin and one GND pin, so splice the wires that need them at a junction. The guide shows each step in 3D.

## Build and flash

You need [PlatformIO](https://platformio.org/).

```sh
pio run              # build
pio run -t upload    # flash over USB-C
```

Turn the power switch off while the board is on USB.

To test the bare board before the LCD and joystick are wired, flash the `bench` build:

```sh
pio run -e bench -t upload
```

It opens an open access point called `CYBERSHOT` at boot (when no Wi-Fi is saved) and ignores the joystick in the viewfinder. Join it and open `http://192.168.4.1/log` for the boot log, or `/galeria` for the photos. To take a photo, briefly connect GPIO 41 to GND with a jumper wire.

GPIO 43 is both the serial TX pin and the LCD CS pin, so the serial monitor shows garbage. Read the log at `http://<camera-ip>/log` instead.

## Controls

| Input | Action |
| --- | --- |
| Shutter, short press | take a photo |
| Shutter, hold > 0.8 s | open / close the menu |
| Joystick up / down | move through the menu |
| Joystick left / right | change a value |
| Joystick press | back |

The menu has:

- viewfinder colors
- long exposure (3 / 5 / 10 s)
- self-timer
- JPEG glitch effects
- Wi-Fi setup
- SD card formatting

## Wi-Fi

1. In the menu, go to **WIFI → CONFIGURE**. This starts an access point called `CyberShot-Setup`.
2. Join it from your phone and open `192.168.4.1`.
3. Enter your home Wi-Fi details.
4. Open the gallery at `http://cybershot.local`.

## If something is wrong

- **"CAM FAIL" on screen:** the camera did not start. Check the ribbon cable. The board restarts after 3 seconds.
- **White screen:** check the LCD wires.
- **Wrong colors or a stripe at the edge of the screen:** change `INITR_BLACKTAB` in `src/main.cpp` to `INITR_GREENTAB`.
- **Resets on battery:** add a 220–470 µF capacitor across the MT3608 output.

## Changes in this fork

- `platformio.ini`
  - removed the Windows-only `build_dir`
  - pinned the library versions: Adafruit ST7735 1.12.0, Adafruit GFX 1.13.0, JPEGDEC 1.8.5
  - `bench` environment for testing the bare board (`BENCH_AP`, `BENCH_NO_JOY` in `src/main.cpp`)
- `docs/wiring-guide/`
  - step-by-step wiring guide (served on GitHub Pages)
  - `render_steps.py`, the Blender script that renders the guide images

The original repository has no license file. Ask the author before reusing the firmware.
