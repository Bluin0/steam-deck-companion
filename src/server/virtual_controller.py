"""
Virtual Controller Module for Steam Deck Companion.

Cross-platform support:
- Windows: Uses vgamepad (ViGEmBus) for Xbox 360 controller emulation.
- Linux: Uses evdev (uinput kernel module) for Xbox 360 controller emulation.
- Fallback: Graceful companion-only mode if drivers are missing.
"""

import sys

class VirtualController:
    def __init__(self):
        self.backend = None # 'vgamepad', 'evdev', or None
        self.gamepad = None
        self.available = False
        self.error_msg = ""
        self._init_device()

    def _init_device(self):
        # 1. Try Windows vgamepad
        if sys.platform == "win32":
            try:
                import vgamepad as vg
                self.vg = vg
                self.gamepad = vg.VX360Gamepad()
                self.backend = 'vgamepad'
                self.available = True
                print("[VirtualController] Virtual Xbox 360 Controller (vgamepad/ViGEmBus) initialized successfully.")
                return
            except Exception as e:
                self.error_msg = str(e)
                print(f"[VirtualController] Notice: vgamepad not initialized ({e}).")

        # 2. Try Linux uinput / evdev
        if sys.platform.startswith("linux"):
            try:
                import evdev
                from evdev import ecodes, UInput, AbsInfo

                self.evdev = evdev
                self.ecodes = ecodes

                cap = {
                    ecodes.EV_KEY: [
                        ecodes.BTN_A, ecodes.BTN_B, ecodes.BTN_X, ecodes.BTN_Y,
                        ecodes.BTN_TL, ecodes.BTN_TR, ecodes.BTN_SELECT, ecodes.BTN_START,
                        ecodes.BTN_THUMBL, ecodes.BTN_THUMBR, ecodes.BTN_MODE
                    ],
                    ecodes.EV_ABS: [
                        (ecodes.ABS_X, AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0)),
                        (ecodes.ABS_Y, AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0)),
                        (ecodes.ABS_RX, AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0)),
                        (ecodes.ABS_RY, AbsInfo(value=0, min=-32768, max=32767, fuzz=0, flat=0, resolution=0)),
                        (ecodes.ABS_Z, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),   # LT
                        (ecodes.ABS_RZ, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),  # RT
                        (ecodes.ABS_HAT0X, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)), # DPad X
                        (ecodes.ABS_HAT0Y, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0))  # DPad Y
                    ]
                }
                self.gamepad = UInput(cap, name="Microsoft X-Box 360 pad", vendor=0x045e, product=0x028e, version=0x0110)
                self.backend = 'evdev'
                self.available = True
                print("[VirtualController] Virtual Xbox 360 Controller (Linux uinput/evdev) initialized successfully.")
                return
            except Exception as e:
                print(f"[VirtualController] Notice: Linux uinput/evdev not available ({e}).")

        # 3. Fallback
        self.available = False
        print("[VirtualController] Controller emulation disabled. Companion dashboard features (Guides, Maps, Notes, HLTB) are fully operational.")

    def update_input(self, state):
        """Updates virtual controller state across Windows and Linux backends."""
        if not self.available or not self.gamepad:
            return

        buttons = state.get("buttons", [])
        axes = state.get("axes", [])

        if self.backend == 'vgamepad':
            self._update_vgamepad(buttons, axes)
        elif self.backend == 'evdev':
            self._update_evdev(buttons, axes)

    def _update_vgamepad(self, buttons, axes):
        try:
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

            if len(buttons) > 6:
                lt_val = int(buttons[6] * 255) if isinstance(buttons[6], (int, float)) else (255 if buttons[6] else 0)
                self.gamepad.left_trigger(value=lt_val)

            if len(buttons) > 7:
                rt_val = int(buttons[7] * 255) if isinstance(buttons[7], (int, float)) else (255 if buttons[7] else 0)
                self.gamepad.right_trigger(value=rt_val)

            if len(axes) >= 4:
                lx = int(axes[0] * 32767)
                ly = int(-axes[1] * 32767)
                self.gamepad.left_joystick(x_value=lx, y_value=ly)

                rx = int(axes[2] * 32767)
                ry = int(-axes[3] * 32767)
                self.gamepad.right_joystick(x_value=rx, y_value=ry)

            self.gamepad.update()
        except Exception as e:
            print(f"[VirtualController] Error updating vgamepad state: {e}")

    def _update_evdev(self, buttons, axes):
        try:
            ec = self.ecodes
            btn_map = [
                (0, ec.BTN_A), (1, ec.BTN_B), (2, ec.BTN_X), (3, ec.BTN_Y),
                (4, ec.BTN_TL), (5, ec.BTN_TR),
                (8, ec.BTN_SELECT), (9, ec.BTN_START),
                (10, ec.BTN_THUMBL), (11, ec.BTN_THUMBR),
                (16, ec.BTN_MODE)
            ]

            for btn_idx, code in btn_map:
                val = 1 if (btn_idx < len(buttons) and buttons[btn_idx]) else 0
                self.gamepad.write(ec.EV_KEY, code, val)

            # DPad Hat
            hat_x = 0
            if len(buttons) > 14 and buttons[14]: hat_x -= 1
            if len(buttons) > 15 and buttons[15]: hat_x += 1
            self.gamepad.write(ec.EV_ABS, ec.ABS_HAT0X, hat_x)

            hat_y = 0
            if len(buttons) > 12 and buttons[12]: hat_y -= 1
            if len(buttons) > 13 and buttons[13]: hat_y += 1
            self.gamepad.write(ec.EV_ABS, ec.ABS_HAT0Y, hat_y)

            # Triggers
            if len(buttons) > 6:
                lt = int(buttons[6] * 255) if isinstance(buttons[6], (int, float)) else (255 if buttons[6] else 0)
                self.gamepad.write(ec.EV_ABS, ec.ABS_Z, lt)
            if len(buttons) > 7:
                rt = int(buttons[7] * 255) if isinstance(buttons[7], (int, float)) else (255 if buttons[7] else 0)
                self.gamepad.write(ec.EV_ABS, ec.ABS_RZ, rt)

            # Axes
            if len(axes) >= 4:
                self.gamepad.write(ec.EV_ABS, ec.ABS_X, int(axes[0] * 32767))
                self.gamepad.write(ec.EV_ABS, ec.ABS_Y, int(axes[1] * 32767))
                self.gamepad.write(ec.EV_ABS, ec.ABS_RX, int(axes[2] * 32767))
                self.gamepad.write(ec.EV_ABS, ec.ABS_RY, int(axes[3] * 32767))

            self.gamepad.syn()
        except Exception as e:
            print(f"[VirtualController] Error updating evdev state: {e}")
