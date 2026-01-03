"""
OCR Processing Coordinator
=========================
Coordinates OCR processing across multiple images and strategies.

PIPELINE POSITION:
    pipeline/ocr_orchestrator.py (MAIN PIPELINE)
        ↓
    pipeline/processing_coordinator.py (THIS FILE)
        ↓
    engines/paddle/paddle_coordinator.py (Engine-Specific)

PURPOSE:
- Manages multiple processed image variants (cropped, enhanced, etc.)
- Runs OCR on each variant with quality scoring
- Selects best OCR result based on text quality metrics
- Coordinates between image processing and OCR engine execution
- Different from the main pipeline orchestrator which handles the entire flow
"""

import logging
from typing import List, Tuple, Any
from app.ocr.engines.paddle.paddle_coordinator import run_ocr_on_image
from app.ocr.engines.scoring.text_scoring import score_ocr_text
from app.ocr.engines.scoring.image_quality import score_image_quality

logger = logging.getLogger(__name__)


class ProcessingCoordinator:
    """Coordinates OCR processing across multiple images and configurations"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
    
    def run_paddleocr_processing(self, processed_images: List[Any]) -> Tuple[str, float, Tuple, List]:
        """Run PaddleOCR processing on all image variants"""
        best_text = ""
        best_score = -1
        best_info = ("", -1, "")
        all_ocr_attempts = []
        
        # First, score all images for quality
        image_quality_scores = []
        for i, p_img in enumerate(processed_images):
            quality_score = score_image_quality(p_img, f"variant_{i}")
            image_quality_scores.append(quality_score)

        # Sort images by quality (highest first)
        quality_sorted_indices = sorted(range(len(processed_images)), 
                                      key=lambda i: image_quality_scores[i], 
                                      reverse=True)

        logger.info(f"[PADDLEOCR] Image quality scores: " + 
                   ", ".join([f"variant_{i}={image_quality_scores[i]:.1f}" 
                             for i in quality_sorted_indices]))

        for rank, i in enumerate(quality_sorted_indices):
            p_img = processed_images[i]
            image_quality = image_quality_scores[i]
            
            logger.info(f"[PADDLEOCR] Processing variant {i} (rank {rank+1}/{len(processed_images)}, "
                       f"quality={image_quality:.1f})")
            
            # Run PaddleOCR
            ocr_results = run_ocr_on_image(
                p_img, 
                debug=self.debug, 
                image_index=i,
                lang='en'  # PaddleOCR English model works well for Croatian text
            )
            all_ocr_attempts.extend(ocr_results)

            # Evaluate each OCR result with quality weighting
            for text, config_idx, config_str in ocr_results:
                if not text or len(text.strip()) < 10:
                    continue
                
                text_score = score_ocr_text(text)
                
                # Weight final score by image quality
                quality_weight = min(image_quality / 50.0, 2.5)  # Max 2.5x boost for high quality
                final_score = text_score * quality_weight
                
                logger.debug(f"[PADDLEOCR] variant_{i}: text_score={text_score}, "
                           f"quality_weight={quality_weight:.2f}, "
                           f"final_score={final_score:.1f}")
                
                if final_score > best_score:
                    best_score = final_score
                    best_text = text
                    best_info = (f"image_{i}", config_idx, config_str)
                    
                    if self.debug:
                        logger.info(f"[PADDLEOCR] New best result (score {final_score:.1f}): "
                                  f"config='{config_str}', preview='{text[:80]}...'")
        
        return best_text, best_score, best_info, all_ocr_attempts
    
    def evaluate_ocr_results(self, ocr_results: List[Tuple[str, int, str]], 
                           image_quality: float) -> List[Tuple[str, float]]:
        """Evaluate OCR results with quality weighting"""
        evaluated_results = []
        
        for text, config_idx, config_str in ocr_results:
            if not text or len(text.strip()) < 10:
                continue
            
            text_score = score_ocr_text(text)
            quality_weight = min(image_quality / 50.0, 2.5)
            final_score = text_score * quality_weight
            
            evaluated_results.append((text, final_score))
        
        return evaluated_results