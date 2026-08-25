"""
P0.3 — Virtual Xbox 360 Controller Prototype
=============================================
VALIDATES: Can we programmatically create a virtual gamepad on Windows
           and inject input that games will recognize?

Uses ViGEmBus + vgamepad to create a virtual Xbox 360 controller,
then runs through a sequence of simulated inputs.

Prerequisites:
  1. Install ViGEmBus driver: https://github.com/nefarius/ViGEmBus/releases
  2. pip install vgamepad

Platform: Windows only
Verify: Open https://gamepad-tester.com in a browser to see the virtual controller.
"""

import sys
import time

try:
    import vgamepad as vg
except ImportError:
    sys.exit("ERROR: pip install vgamepad  (also install ViGEmBus driver first)")


def main():
    print("=== P0.3: Virtual Controller ===\n")
    print("NOTE: ViGEmBus driver must be installed!")
    print("      https://github.com/nefarius/ViGEmBus/releases\n")
    print("Open https://gamepad-tester.com to see the virtual controller.\n")

    pad = vg.VX360Gamepad()
    print("[+] Virtual Xbox 360 controller created.\n")
    time.sleep(1)

    steps = [
        ("Press A button", lambda: (pad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A), pad.update())),
        ("Release A button", lambda: (pad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A), pad.update())),
        ("Press B button", lambda: (pad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B), pad.update())),
        ("Release B button", lambda: (pad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B), pad.update())),
        ("Left stick full left", lambda: (pad.left_joystick_float(-1.0, 0.0), pad.update())),
        ("Left stick center", lambda: (pad.left_joystick_float(0.0, 0.0), pad.update())),
        ("Left stick full up", lambda: (pad.left_joystick_float(0.0, 1.0), pad.update())),
        ("Left stick center", lambda: (pad.left_joystick_float(0.0, 0.0), pad.update())),
        ("Right trigger full", lambda: (pad.right_trigger_float(1.0), pad.update())),
        ("Right trigger release", lambda: (pad.right_trigger_float(0.0), pad.update())),
        ("Left trigger full", lambda: (pad.left_trigger_float(1.0), pad.update())),
        ("Left trigger release", lambda: (pad.left_trigger_float(0.0), pad.update())),
        ("Press X + move right stick", lambda: (
            pad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X),
            pad.right_joystick_float(0.7, -0.3),
            pad.update()
        )),
        ("Release all", lambda: (pad.reset(), pad.update())),
        ("D-Pad up", lambda: (pad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP), pad.update())),
        ("D-Pad release", lambda: (pad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP), pad.update())),
    ]

    for i, (desc, action) in enumerate(steps, 1):
        print(f"  [{i:2d}/{len(steps)}] {desc}")
        action()
        time.sleep(2)

    pad.reset()
    pad.update()
    print("\n[+] Done. Virtual controller cleaned up.")


if __name__ == "__main__":
    main()
