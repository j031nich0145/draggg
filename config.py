#!/usr/bin/env python3
"""
Configuration Management for Linux Three-Finger Drag
Handles loading, saving, and validating configuration files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "three-finger-drag"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "device": None,  # Auto-detect if None
    "threshold": 10,
    "drag_sensitivity": 0.25,
    "left_handed": False,
    "leading_finger_weight": 1.5,
    "other_fingers_weight": 0.3,
}

CONFIG_VALIDATION = {
    "threshold": {"type": int, "min": 1, "max": 100, "default": 10},
    "drag_sensitivity": {"type": float, "min": 0.1, "max": 5.0, "default": 1.0},
    "left_handed": {"type": bool, "default": False},
    "leading_finger_weight": {"type": float, "min": 0.1, "max": 10.0, "default": 1.5},
    "other_fingers_weight": {"type": float, "min": 0.1, "max": 10.0, "default": 0.3},
    "device": {"type": (str, type(None)), "default": None},
}


class ConfigError(Exception):
    """Configuration-related error."""
    pass


def validate_config_value(key: str, value: Any) -> Any:
    """
    Validate and normalize a configuration value.
    Returns the validated value or raises ConfigError.
    """
    if key not in CONFIG_VALIDATION:
        return value  # Unknown keys pass through
    
    validation = CONFIG_VALIDATION[key]
    expected_type = validation["type"]
    
    # Handle tuple of types (for optional values)
    if isinstance(expected_type, tuple):
        if not isinstance(value, expected_type):
            raise ConfigError(
                f"Invalid type for '{key}': expected {expected_type}, got {type(value).__name__}"
            )
    elif not isinstance(value, expected_type):
        raise ConfigError(
            f"Invalid type for '{key}': expected {expected_type.__name__}, got {type(value).__name__}"
        )
    
    # Validate numeric ranges
    if expected_type in (int, float) and isinstance(value, (int, float)):
        if "min" in validation and value < validation["min"]:
            raise ConfigError(
                f"Value for '{key}' ({value}) is below minimum ({validation['min']})"
            )
        if "max" in validation and value > validation["max"]:
            raise ConfigError(
                f"Value for '{key}' ({value}) is above maximum ({validation['max']})"
            )
    
    return value


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to config file. If None, uses default location.
    
    Returns:
        Dictionary with configuration values.
    
    Raises:
        ConfigError: If config file is invalid.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_FILE
    else:
        config_path = Path(config_path)
    
    # Start with defaults
    config = DEFAULT_CONFIG.copy()
    
    # Load from file if it exists
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            
            # Validate and merge file config
            for key, value in file_config.items():
                if key in DEFAULT_CONFIG:
                    try:
                        validated_value = validate_config_value(key, value)
                        config[key] = validated_value
                    except ConfigError as e:
                        raise ConfigError(f"Error in config file '{config_path}': {e}")
                # Ignore unknown keys
        
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file '{config_path}': {e}")
        except IOError as e:
            raise ConfigError(f"Error reading config file '{config_path}': {e}")
    
    return config


def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Dictionary with configuration values.
        config_path: Path to config file. If None, uses default location.
    
    Raises:
        ConfigError: If config is invalid or file cannot be written.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_FILE
    else:
        config_path = Path(config_path)
    
    # Validate all values before saving
    validated_config = {}
    for key, value in config.items():
        if key in DEFAULT_CONFIG:
            try:
                validated_config[key] = validate_config_value(key, value)
            except ConfigError as e:
                raise ConfigError(f"Invalid config value: {e}")
        # Skip unknown keys
    
    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write config file
    try:
        with open(config_path, 'w') as f:
            json.dump(validated_config, f, indent=4)
    except IOError as e:
        raise ConfigError(f"Error writing config file '{config_path}': {e}")


def merge_configs(
    base_config: Dict[str, Any],
    override_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries.
    Values in override_config override values in base_config.
    
    Args:
        base_config: Base configuration.
        override_config: Configuration values to override.
    
    Returns:
        Merged configuration dictionary.
    """
    merged = base_config.copy()
    
    for key, value in override_config.items():
        if value is not None:  # None values don't override
            if key in DEFAULT_CONFIG:
                try:
                    merged[key] = validate_config_value(key, value)
                except ConfigError as e:
                    # Log warning but continue with invalid value
                    # (caller can handle or ignore)
                    pass
            merged[key] = value
    
    return merged


def get_config_path() -> Path:
    """Get the default configuration file path."""
    return DEFAULT_CONFIG_FILE


def config_from_args(args) -> Dict[str, Any]:
    """
    Create configuration dictionary from argparse arguments.
    
    Args:
        args: Parsed argparse arguments.
    
    Returns:
        Configuration dictionary.
    """
    config = {}
    
    if hasattr(args, 'device') and args.device:
        config['device'] = args.device
    if hasattr(args, 'threshold') and args.threshold is not None:
        config['threshold'] = args.threshold
    if hasattr(args, 'drag_sensitivity') and args.drag_sensitivity is not None:
        config['drag_sensitivity'] = args.drag_sensitivity
    if hasattr(args, 'left_handed'):
        config['left_handed'] = args.left_handed
    if hasattr(args, 'leading_weight') and args.leading_weight is not None:
        config['leading_finger_weight'] = args.leading_weight
    if hasattr(args, 'other_weight') and args.other_weight is not None:
        config['other_fingers_weight'] = args.other_weight
    
    return config


def create_default_config(config_path: Optional[str] = None) -> None:
    """
    Create a default configuration file.
    
    Args:
        config_path: Path to config file. If None, uses default location.
    """
    if config_path is None:
        config_path = DEFAULT_CONFIG_FILE
    else:
        config_path = Path(config_path)
    
    save_config(DEFAULT_CONFIG, config_path)

