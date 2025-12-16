import threading
from typing import Callable, Optional

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class HotkeyManager:
    def __init__(self):
        self.listener = None
        self.current_hotkey = None
        self.on_activate: Optional[Callable] = None
        self.on_deactivate: Optional[Callable] = None
        self.is_pressed = False
        self.pressed_keys = set()
    
    def parse_hotkey(self, hotkey_str: str) -> set:
        """Parsuje string hotkeya do zestawu klawiszy"""
        keys = set()
        parts = hotkey_str.lower().replace(" ", "").split("+")
        
        key_mapping = {
            "ctrl": keyboard.Key.ctrl_l,
            "control": keyboard.Key.ctrl_l,
            "shift": keyboard.Key.shift_l,
            "alt": keyboard.Key.alt_l,
            "cmd": keyboard.Key.cmd,
            "command": keyboard.Key.cmd,
            "win": keyboard.Key.cmd,
        }
        
        for part in parts:
            if part in key_mapping:
                keys.add(key_mapping[part])
            elif len(part) == 1:
                keys.add(keyboard.KeyCode.from_char(part))
            else:
                try:
                    keys.add(getattr(keyboard.Key, part))
                except AttributeError:
                    keys.add(keyboard.KeyCode.from_char(part[0]))
        
        return keys
    
    def start(self, hotkey: str, on_activate: Callable, on_deactivate: Callable):
        if not PYNPUT_AVAILABLE:
            print("pynput nie jest dostępne")
            return False
        
        self.stop()
        
        self.current_hotkey = self.parse_hotkey(hotkey)
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.pressed_keys = set()
        self.is_pressed = False
        
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.daemon = True
        self.listener.start()
        
        return True
    
    def _normalize_key(self, key):
        """Normalizuje klawisz (np. ctrl_r -> ctrl_l)"""
        if hasattr(key, 'name'):
            name = key.name
            if name.endswith('_r'):
                base_name = name[:-2] + '_l'
                try:
                    return getattr(keyboard.Key, base_name)
                except AttributeError:
                    pass
        return key
    
    def _on_press(self, key):
        normalized = self._normalize_key(key)
        self.pressed_keys.add(normalized)
        
        if self.current_hotkey and self.current_hotkey.issubset(self.pressed_keys):
            if not self.is_pressed:
                self.is_pressed = True
                if self.on_activate:
                    threading.Thread(target=self.on_activate, daemon=True).start()
    
    def _on_release(self, key):
        normalized = self._normalize_key(key)
        self.pressed_keys.discard(normalized)
        self.pressed_keys.discard(key)
        
        if self.is_pressed and self.current_hotkey:
            if not self.current_hotkey.issubset(self.pressed_keys):
                self.is_pressed = False
                if self.on_deactivate:
                    threading.Thread(target=self.on_deactivate, daemon=True).start()
    
    def stop(self):
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.pressed_keys = set()
        self.is_pressed = False
    
    def is_available(self) -> bool:
        return PYNPUT_AVAILABLE
