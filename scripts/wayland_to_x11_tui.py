#!/usr/bin/env python3
"""
Wayland to X11 Conversion TUI Helper
Curses-based interface for converting Wayland sessions to X11.
"""

import os
import sys
import curses
import subprocess
from pathlib import Path

# Import conversion script functions
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.wayland_to_x11 import (
    detect_distribution,
    detect_display_manager,
    get_config_path,
    convert_wayland_to_x11,
    can_modify_config
)


class WaylandToX11TUI:
    """Curses-based TUI for Wayland to X11 conversion."""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        self.selected_option = 0  # 0 = Yes, 1 = No
        self.current_step = 'info'  # info, progress, result, logout
        
        # Detect system info
        self.session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown').lower()
        self.distro = detect_distribution()
        self.display_manager = detect_display_manager()
        self.config_path = get_config_path(self.display_manager, self.distro) if self.display_manager else None
        
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Header
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Success
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # Error
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Warning
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Selected
    
    def draw_header(self):
        """Draw header with title and session info."""
        title = "Wayland to X11 Conversion Helper"
        self.stdscr.addstr(0, 0, "=" * self.width, curses.color_pair(1))
        self.stdscr.addstr(1, (self.width - len(title)) // 2, title, curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(2, 0, "=" * self.width, curses.color_pair(1))
        
        # Session info
        y = 4
        self.stdscr.addstr(y, 2, f"Current Session: {self.session_type.upper()}", curses.A_BOLD)
        y += 1
        if self.display_manager:
            self.stdscr.addstr(y, 2, f"Display Manager: {self.display_manager.upper()}")
            y += 1
        if self.config_path:
            self.stdscr.addstr(y, 2, f"Config File: {self.config_path}")
            y += 1
        
        # Separator
        y += 1
        self.stdscr.addstr(y, 0, "-" * self.width)
        return y + 2
    
    def draw_info(self, start_y):
        """Draw information about what will happen."""
        y = start_y
        self.stdscr.addstr(y, 2, "This will:", curses.A_BOLD)
        y += 2
        
        info_lines = [
            "• Backup your current config file",
            "• Disable Wayland in display manager",
            "• Require logout to take effect",
            "",
            "After logout, your system will use X11 session",
            "and draggg will work optimally."
        ]
        
        for line in info_lines:
            if y < self.height - 5:
                self.stdscr.addstr(y, 4, line)
                y += 1
        
        return y + 1
    
    def draw_confirmation(self, start_y):
        """Draw confirmation prompt."""
        y = start_y
        prompt = "Continue?"
        self.stdscr.addstr(y, 2, prompt, curses.A_BOLD)
        y += 2
        
        # Yes option
        yes_text = "[Yes]"
        no_text = "[No]"
        
        if self.selected_option == 0:
            self.stdscr.addstr(y, 4, yes_text, curses.color_pair(5) | curses.A_BOLD)
            self.stdscr.addstr(y, 4 + len(yes_text) + 2, no_text)
        else:
            self.stdscr.addstr(y, 4, yes_text)
            self.stdscr.addstr(y, 4 + len(yes_text) + 2, no_text, curses.color_pair(5) | curses.A_BOLD)
        
        # Instructions
        y += 2
        self.stdscr.addstr(y, 2, "Use ← → to select, Enter to confirm, Q to quit", curses.color_pair(4))
    
    def draw_progress(self, start_y, message="Processing..."):
        """Draw progress indicator."""
        y = start_y
        self.stdscr.addstr(y, 2, message, curses.color_pair(4))
        y += 1
        self.stdscr.addstr(y, 2, "Please wait...", curses.A_BLINK)
        self.stdscr.refresh()
    
    def draw_result(self, start_y, success: bool, message: str):
        """Draw result message."""
        y = start_y
        if success:
            self.stdscr.addstr(y, 2, "✓ Success!", curses.color_pair(2) | curses.A_BOLD)
        else:
            self.stdscr.addstr(y, 2, "✗ Error", curses.color_pair(3) | curses.A_BOLD)
        
        y += 2
        # Wrap message
        words = message.split()
        line = ""
        x = 2
        for word in words:
            if len(line + word) + 1 > self.width - 4:
                self.stdscr.addstr(y, x, line)
                y += 1
                line = word + " "
            else:
                line += word + " "
        if line:
            self.stdscr.addstr(y, x, line)
            y += 1
        
        return y + 1
    
    def draw_logout_prompt(self, start_y):
        """Draw logout prompt."""
        y = start_y
        self.stdscr.addstr(y, 2, "Log out now?", curses.A_BOLD)
        y += 2
        
        yes_text = "[Yes]"
        no_text = "[No]"
        
        if self.selected_option == 0:
            self.stdscr.addstr(y, 4, yes_text, curses.color_pair(5) | curses.A_BOLD)
            self.stdscr.addstr(y, 4 + len(yes_text) + 2, no_text)
        else:
            self.stdscr.addstr(y, 4, yes_text)
            self.stdscr.addstr(y, 4 + len(yes_text) + 2, no_text, curses.color_pair(5) | curses.A_BOLD)
        
        y += 2
        self.stdscr.addstr(y, 2, "Use ← → to select, Enter to confirm", curses.color_pair(4))
    
    def execute_logout(self) -> bool:
        """Execute logout command."""
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        
        logout_commands = []
        if 'gnome' in desktop:
            logout_commands.append('gnome-session-quit --logout --no-prompt')
        elif 'kde' in desktop:
            logout_commands.append('qdbus org.kde.ksmserver /KSMServer logout 0 0 0')
        elif 'xfce' in desktop:
            logout_commands.append('xfce4-session-logout --logout')
        else:
            logout_commands.extend([
                'gnome-session-quit --logout',
                'loginctl terminate-user $USER'
            ])
        
        for cmd in logout_commands:
            try:
                subprocess.Popen(cmd, shell=True)
                return True
            except Exception:
                continue
        
        return False
    
    def run(self):
        """Main TUI loop."""
        while True:
            self.stdscr.clear()
            
            if self.current_step == 'info':
                y = self.draw_header()
                y = self.draw_info(y)
                y = self.draw_confirmation(y)
                
                # Handle input
                key = self.stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == curses.KEY_LEFT:
                    self.selected_option = 0
                elif key == curses.KEY_RIGHT:
                    self.selected_option = 1
                elif key == ord('\n') or key == ord('\r'):
                    if self.selected_option == 0:  # Yes
                        self.current_step = 'progress'
                    else:  # No
                        break
            
            elif self.current_step == 'progress':
                y = self.draw_header()
                y = self.draw_progress(y)
                
                # Run conversion
                success, message = convert_wayland_to_x11()
                
                self.conversion_success = success
                self.conversion_message = message
                self.current_step = 'result'
            
            elif self.current_step == 'result':
                y = self.draw_header()
                y = self.draw_result(y, self.conversion_success, self.conversion_message)
                
                if self.conversion_success:
                    y += 2
                    self.stdscr.addstr(y, 2, "Press any key to continue...", curses.color_pair(4))
                    self.stdscr.getch()
                    self.current_step = 'logout'
                else:
                    y += 2
                    self.stdscr.addstr(y, 2, "Press any key to exit...", curses.color_pair(4))
                    self.stdscr.getch()
                    break
            
            elif self.current_step == 'logout':
                y = self.draw_header()
                if self.conversion_success:
                    y = self.draw_result(y, True, self.conversion_message)
                y += 2
                y = self.draw_logout_prompt(y)
                
                # Handle input
                key = self.stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == curses.KEY_LEFT:
                    self.selected_option = 0
                elif key == curses.KEY_RIGHT:
                    self.selected_option = 1
                elif key == ord('\n') or key == ord('\r'):
                    if self.selected_option == 0:  # Yes
                        if self.execute_logout():
                            self.stdscr.clear()
                            self.stdscr.addstr(self.height // 2, (self.width - 30) // 2,
                                             "Logging out...", curses.color_pair(2))
                            self.stdscr.refresh()
                            curses.napms(2000)
                        else:
                            y = self.draw_header()
                            y = self.draw_result(y, False, "Could not execute logout. Please log out manually.")
                            self.stdscr.addstr(y + 2, 2, "Press any key to exit...", curses.color_pair(4))
                            self.stdscr.getch()
                        break
                    else:  # No
                        break
            
            self.stdscr.refresh()


def main():
    """Main entry point."""
    # Check if running on Wayland
    session_type = os.environ.get('XDG_SESSION_TYPE', 'unknown').lower()
    if session_type == 'x11':
        print("Already running on X11 session. No conversion needed.")
        sys.exit(0)
    
    if session_type != 'wayland':
        print(f"Warning: Unknown session type: {session_type}")
        print("This tool is designed for Wayland sessions.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Check if running in a terminal
    if not sys.stdout.isatty():
        print("Error: This tool requires a terminal.", file=sys.stderr)
        sys.exit(1)
    
    # Run TUI
    try:
        curses.wrapper(WaylandToX11TUI)
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
