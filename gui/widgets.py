#!/usr/bin/env python3
"""
Reusable GUI widgets for draggg.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class LabeledSlider(ttk.Frame):
    """Slider widget with label and value display."""
    
    def __init__(self, parent, label: str, from_: float, to: float,
                 default: float = None, resolution: float = 0.01,
                 command: Optional[Callable] = None, **kwargs):
        super().__init__(parent)
        
        self.label_text = label
        self.from_val = from_
        self.to_val = to
        self.resolution = resolution
        self.command = command
        self.default = default if default is not None else from_
        
        # Label
        self.label = ttk.Label(self, text=label)
        self.label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Value display
        self.value_var = tk.DoubleVar(value=self.default)
        self.value_label = ttk.Label(self, textvariable=self.value_var, width=8)
        self.value_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Slider
        self.slider = ttk.Scale(
            self,
            from_=from_,
            to=to,
            value=self.default,
            orient=tk.HORIZONTAL,
            command=self._on_slider_change,
            **kwargs
        )
        self.slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Update value display
        self._update_display()
    
    def _on_slider_change(self, value):
        """Handle slider value change."""
        val = float(value)
        # Round to resolution
        val = round(val / self.resolution) * self.resolution
        self.value_var.set(val)
        if self.command:
            self.command(val)
    
    def _update_display(self):
        """Update value display label."""
        val = self.value_var.get()
        # Format based on resolution
        if self.resolution >= 1:
            self.value_label.config(text=f"{int(val)}")
        elif self.resolution >= 0.1:
            self.value_label.config(text=f"{val:.1f}")
        else:
            self.value_label.config(text=f"{val:.2f}")
    
    def get(self) -> float:
        """Get current slider value."""
        return self.value_var.get()
    
    def set(self, value: float):
        """Set slider value."""
        self.value_var.set(value)
        self.slider.set(value)
        self._update_display()


class StatusIndicator(ttk.Frame):
    """Status indicator with color and text."""
    
    COLORS = {
        'success': '#28a745',
        'warning': '#ffc107',
        'error': '#dc3545',
        'info': '#17a2b8',
        'neutral': '#6c757d',
    }
    
    def __init__(self, parent, text: str = "", status: str = "neutral", **kwargs):
        super().__init__(parent, **kwargs)
        
        # Color circle (using a small label with colored background)
        self.color_label = tk.Label(
            self,
            text="●",
            fg=self.COLORS.get(status, self.COLORS['neutral']),
            font=("Arial", 16),
            bg=self.cget('bg') if 'bg' in kwargs else None
        )
        self.color_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Text label
        self.text_label = ttk.Label(self, text=text)
        self.text_label.pack(side=tk.LEFT)
    
    def set_status(self, status: str, text: str = None):
        """Update status and optionally text."""
        self.color_label.config(fg=self.COLORS.get(status, self.COLORS['neutral']))
        if text is not None:
            self.text_label.config(text=text)


class CollapsibleFrame(ttk.Frame):
    """Frame that can be expanded/collapsed."""
    
    def __init__(self, parent, title: str, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.is_expanded = False
        
        # Header with toggle button
        self.header = ttk.Frame(self)
        self.header.pack(fill=tk.X)
        
        self.toggle_btn = ttk.Button(
            self.header,
            text=f"▼ {title}",
            command=self.toggle,
            width=20
        )
        self.toggle_btn.pack(side=tk.LEFT)
        
        # Content frame (hidden by default)
        self.content = ttk.Frame(self)
        # Don't pack initially
    
    def toggle(self):
        """Toggle expanded/collapsed state."""
        current_text = self.toggle_btn.cget('text')
        title = current_text.split(' ', 1)[1] if ' ' in current_text else "Advanced Settings"
        
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.content.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            self.toggle_btn.config(text=f"▲ {title}")
        else:
            self.content.pack_forget()
            self.toggle_btn.config(text=f"▼ {title}")
    
    def get_content_frame(self) -> ttk.Frame:
        """Get the content frame to add widgets to."""
        return self.content

