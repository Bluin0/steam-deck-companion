"""
Virtual Controller Module for Steam Deck Companion.

Wraps vgamepad (ViGEmBus) to inject Xbox 360 inputs into Windows.
"""

import sys

class VirtualController:
    def __init__(self):
        self.gamepad = None
        self.available = False
        self._init_device()

    def _init_device(self):
        try:
            import vgamepad as vg
            self.vg = vg
            self.gamepad = vg.VX360Gamepad()
            self.available = True
            print("[VirtualController] Virtual Xbox 360 Controller initialized successfully.")
        except Exception as e:
            print(f"[VirtualController] Warning: Could not initialize vgamepad ({e}).")
            self.available = False

    def update_input(self, state):
        """
        Updates virtual controller state.
        state dict expected format:
        {
          "buttons": [... list of bools or 0/1 ...],
          "axes": [... list of floats -1.0 to 1.0 ...]
        }
        """
        if not self.available or not self.gamepad:
            return

        try:
            # Map standard HTML5 Gamepad buttons to Xbox 360 controller
            # 0: A, 1: B, 2: X, 3: Y, 4: LB, 5: RB, 6: LT, 7: RT, 8: Back, 9: Start, 10: L3, 11: R3, 12: DUp, 13: DDown, 14: DLeft, 15: DRight, 16: Guide
            buttons = state.get("buttons", [])
            axes = state.get("axes", [])

            # Reset / Update buttons
            btn_map = [
                self.vg.XUSB_BUTTON.XUSB_GAMEPAD_A,             # 0
                self.vg.XUSB_BUTTON.XUSB_GAMEPAD_B,             # 1
                self.vg.XUSB_BUTTON.XUSB_GAMEPAD_X,             # 2
                self.vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,             # 3
                self.vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER, # 4
                self.vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,# 5
            ]

            for idx, btn_code in enumerate(btn_map):
                if idx < len(buttons) and buttons[idx]:
                    self.gamepad.press_button(btn_code)
                else:
                    self.gamepad.release_button(btn_code)

            # D-Pad
            dpad_map = [
                (12, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP),
                (13, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN),
                (14, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT),
                (15, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT),
            ]
            for idx, btn_code in dpad_map:
                if idx < len(buttons) and buttons[idx]:
                    self.gamepad.press_button(btn_code)
                else:
                    self.gamepad.release_button(btn_code)

            # Axes (Left stick: axes[0], axes[1]; Right stick: axes[2], axes[3])
            if len(axes) >= 4:
                # Left Joystick
                lx = int(axes[0] * 32767)
                ly = int(-axes[1] * 32767) # Invert Y for Xbox standard
                self.gamepad.left_joystick(x_value=lx, y_value=ly)

                # Right Joystick
                rx = int(axes[2] * 32767)
                ry = int(-axes[3] * 32767) # Invert Y
                self.gamepad.right_joystick(x_value=rx, y_value=ry)

            self.gamepad.update()
        except Exception as e:
            print(f"[VirtualController] Error updating controller state: {e}")
