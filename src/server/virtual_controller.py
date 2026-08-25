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

            # Map buttons
            btn_map = [
                (0, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_A),
                (1, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_B),
                (2, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_X),
                (3, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_Y),
                (4, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER),
                (5, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER),
                (8, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK),
                (9, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_START),
                (10, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB),
                (11, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB),
                (12, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP),
                (13, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN),
                (14, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT),
                (15, self.vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT),
            ]

            for btn_idx, btn_code in btn_map:
                if btn_idx < len(buttons) and buttons[btn_idx]:
                    self.gamepad.press_button(btn_code)
                else:
                    self.gamepad.release_button(btn_code)

            # Triggers (6: Left Trigger LT/L2, 7: Right Trigger RT/R2)
            if len(buttons) > 6:
                lt_val = int(buttons[6] * 255) if isinstance(buttons[6], (int, float)) else (255 if buttons[6] else 0)
                self.gamepad.left_trigger(value=lt_val)

            if len(buttons) > 7:
                rt_val = int(buttons[7] * 255) if isinstance(buttons[7], (int, float)) else (255 if buttons[7] else 0)
                self.gamepad.right_trigger(value=rt_val)

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
