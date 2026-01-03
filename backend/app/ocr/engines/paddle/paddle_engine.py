"""
PaddleOCR Engine Core
====================
Core PaddleOCR engine initialization and management.
"""

import logging
import os
import yaml
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

# Global singleton instance
_ocr_engine = None

# Path to YAML configuration file (project root)
YAML_CONFIG_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "PaddleOCR.yaml")
)


def load_yaml_config():
    """
    Load PaddleOCR configuration from YAML file.

    Returns:
        dict: Configuration dictionary or None if file doesn't exist
    """
    try:
        if os.path.exists(YAML_CONFIG_PATH):
            with open(YAML_CONFIG_PATH, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded PaddleOCR configuration from {YAML_CONFIG_PATH}")
                return config
        else:
            logger.warning(
                f"PaddleOCR YAML config not found at {YAML_CONFIG_PATH}, using defaults"
            )
            return None
    except Exception as e:
        logger.error(f"Failed to load YAML config: {e}, using defaults")
        return None


class PaddleOCREngine:
    """Simplified PaddleOCR engine wrapper with Croatian Latin support"""

    def __init__(self, lang=None, config_path=None):
        """
        Initialize PaddleOCR engine with YAML configuration support.

        Args:
            lang (str): Language code - defaults to value from YAML config or 'hr' for Croatian
                       Croatian includes special characters: č, ć, đ, š, ž
            config_path (str): Path to YAML config file - defaults to PaddleOCR.yaml in project root

        Note:
            Configuration is loaded from YAML file (PaddleOCR.yaml) if it exists.
            Parameters can be overridden by passing them directly.
        """
        # Load YAML configuration
        yaml_config = load_yaml_config() if config_path is None else None
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f)

        # Determine language (priority: parameter > YAML > default 'hr')
        if lang is None:
            lang = yaml_config.get("lang", "hr") if yaml_config else "hr"
        self.lang = lang

        # Build PaddleOCR initialization parameters
        if yaml_config:
            # Pass ALL relevant parameters from YAML to PaddleOCR
            ocr_params = {
                "lang": lang,
                "use_angle_cls": yaml_config.get("use_angle_cls", False),
                # Detection parameters (critical for text box detection)
                "det_db_thresh": yaml_config.get("det_db_thresh", 0.3),
                "det_db_box_thresh": yaml_config.get("det_db_box_thresh", 0.6),
                "det_db_unclip_ratio": yaml_config.get("det_db_unclip_ratio", 1.5),
                "det_limit_side_len": yaml_config.get("det_limit_side_len", 960),
                "det_limit_type": yaml_config.get("det_limit_type", "max"),
                # Recognition parameters
                "rec_batch_num": yaml_config.get("rec_batch_num", 6),
                # "max_text_length": yaml_config.get("max_text_length", 25),
                # Performance parameters
                # 'use_gpu': yaml_config.get('use_gpu', False),
                "enable_mkldnn": yaml_config.get("enable_mkldnn", False),
            }
            logger.info(f"Using configuration from YAML file: {YAML_CONFIG_PATH}")
            logger.info(
                f"Detection settings: thresh={ocr_params['det_db_thresh']}, box_thresh={ocr_params['det_db_box_thresh']}, unclip={ocr_params['det_db_unclip_ratio']}"
            )
        else:
            # Fallback to minimal defaults if YAML not found
            ocr_params = {
                "lang": lang,
                "use_angle_cls": False,  # We handle orientation manually
            }
            logger.info("Using hardcoded default configuration (YAML not found)")

        # Initialize PaddleOCR
        try:
            self.ocr = PaddleOCR(**ocr_params)
            logger.info(
                f"PaddleOCR initialized successfully (lang={lang}, GPU=auto-detected)"
            )
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise


def get_ocr_engine(lang="hr"):
    """
    Get singleton OCR engine instance

    Args:
        lang (str): Language code - defaults to 'hr' for Croatian

    Returns:
        PaddleOCREngine: Singleton OCR engine instance
    """
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = PaddleOCREngine(lang=lang)
    return _ocr_engine

