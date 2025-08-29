"""
QR Image Generation

Handles QR code image generation with PIL:
- QR code creation with customizable options
- Title and description rendering
- Batch saving functionality
"""

import logging
from typing import Optional, Dict, Any, Union, List
from pathlib import Path

try:
    import qrcode
    from PIL import Image, ImageDraw, ImageFont
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

logger = logging.getLogger(__name__)


class QRImageGenerator:
    """Generates QR code images with customization"""
    
    def __init__(self):
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Check if required libraries are available"""
        if not QR_AVAILABLE:
            logger.warning(
                "QR code generation requires additional dependencies. "
                "Install with: pip install qrcode[pil]"
            )
    
    def generate_qr_image(self, 
                         qr_data: str,
                         title: str = "",
                         description: str = "",
                         size: int = 300,
                         border: int = 4,
                         error_correction=None,
                         add_title: bool = True) -> Optional[Image.Image]:
        """
        Generate QR code image
        
        Args:
            qr_data: QR code data string
            title: Title text to add above QR
            description: Description text to add above QR
            size: Image size in pixels (square)
            border: QR code border thickness
            error_correction: QR error correction level
            add_title: Whether to add title area
            
        Returns:
            PIL Image object or None if qrcode not available
        """
        if not QR_AVAILABLE:
            logger.warning("qrcode library not available. Install with: pip install qrcode[pil]")
            return None
            
        if error_correction is None:
            error_correction = qrcode.constants.ERROR_CORRECT_M
            
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_correction,
            box_size=10,
            border=border,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Generate image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize to requested size
        qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
        
        # Add title if requested
        if add_title and (title or description):
            qr_img = self._add_title_to_image(qr_img, title, description, size)
            
        return qr_img
    
    def _add_title_to_image(self, qr_img: Image.Image, title: str, description: str, qr_size: int) -> Image.Image:
        """Add title and description to QR image"""
        if not QR_AVAILABLE:
            return qr_img
            
        # Calculate title area height
        title_height = 60
        total_height = qr_size + title_height
        
        # Create new image with title area
        final_img = Image.new('RGB', (qr_size, total_height), 'white')
        
        # Paste QR code
        final_img.paste(qr_img, (0, title_height))
        
        # Add text
        draw = ImageDraw.Draw(final_img)
        
        try:
            # Try to use a better font
            font_title = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
            font_desc = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 10)
        except:
            # Fallback to default font
            font_title = ImageFont.load_default()
            font_desc = ImageFont.load_default()
        
        # Draw title
        if title:
            title_bbox = draw.textbbox((0, 0), title, font=font_title)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (qr_size - title_width) // 2
            draw.text((title_x, 5), title, fill='black', font=font_title)
        
        # Draw description  
        if description:
            desc_text = description[:50] + ("..." if len(description) > 50 else "")
            desc_bbox = draw.textbbox((0, 0), desc_text, font=font_desc)
            desc_width = desc_bbox[2] - desc_bbox[0]
            desc_x = (qr_size - desc_width) // 2
            draw.text((desc_x, 25), desc_text, fill='gray', font=font_desc)
        
        return final_img


class QRImageSaver:
    """Handles QR image saving operations"""
    
    def __init__(self):
        self._generator = QRImageGenerator()
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def save_qr_image(self, 
                     qr_data: str,
                     filename: Union[str, Path],
                     title: str = "",
                     description: str = "",
                     **image_options) -> bool:
        """
        Save QR code as PNG image
        
        Args:
            qr_data: QR code data string
            filename: Output filename
            title: Title text
            description: Description text
            **image_options: Additional arguments for generate_qr_image()
            
        Returns:
            True if saved successfully
        """
        try:
            qr_image = self._generator.generate_qr_image(
                qr_data, title, description, **image_options
            )
                
            if qr_image is None:
                self._logger.error("Cannot generate QR image - qrcode library not available")
                return False
                
            qr_image.save(filename, 'PNG')
            self._logger.info(f"QR code saved to {filename}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to save QR code: {e}")
            return False
    
    def save_multiple_qr_images(self, 
                               qr_data_list: List[Dict[str, Any]],
                               output_dir: Union[str, Path],
                               filename_prefix: str = "qr_",
                               **image_options) -> List[str]:
        """
        Save multiple QR codes to files
        
        Args:
            qr_data_list: List of dicts with 'qr_data', 'title', 'description' keys
            output_dir: Output directory path
            filename_prefix: Prefix for generated filenames
            **image_options: Additional arguments for QR generation
            
        Returns:
            List of generated filenames
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        for i, qr_item in enumerate(qr_data_list):
            qr_data = qr_item.get('qr_data', '')
            title = qr_item.get('title', '')
            description = qr_item.get('description', '')
            
            # Generate safe filename from description
            safe_desc = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_desc = safe_desc.replace(' ', '_')[:50]  # Limit length
            
            filename = f"{filename_prefix}{i:03d}_{safe_desc}.png"
            filepath = output_path / filename
            
            try:
                if self.save_qr_image(qr_data, filepath, title, description, **image_options):
                    saved_files.append(str(filepath))
                    self._logger.info(f"Saved QR code: {filepath}")
                else:
                    self._logger.error(f"Failed to save QR code: {filepath}")
            except Exception as e:
                self._logger.error(f"Error saving {filepath}: {e}")
        
        return saved_files
    
    def save_lua_script_sequence(self,
                                qr_data_list: List[Dict[str, Any]],
                                output_dir: Union[str, Path],
                                filename_prefix: str = "lua_script_") -> List[str]:
        """
        Save Lua script QR sequence with special numbering
        
        Args:
            qr_data_list: List of QR data items with fragment info
            output_dir: Directory to save QR codes
            filename_prefix: Prefix for QR filenames
            
        Returns:
            List of saved file paths
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        total_fragments = len(qr_data_list)
        
        for i, qr_item in enumerate(qr_data_list):
            fragment_num = i + 1
            
            if total_fragments == 1:
                filename = f"{filename_prefix}single.png"
            else:
                filename = f"{filename_prefix}{fragment_num:02d}_of_{total_fragments:02d}.png"
            
            filepath = output_path / filename
            
            try:
                # Add QR generation options for better readability
                image_options = {
                    'size': 400,  # Larger QR for complex data
                    'border': 6,  # More border for better scanning
                    'error_correction': qrcode.constants.ERROR_CORRECT_L if QR_AVAILABLE else None
                }
                
                qr_data = qr_item.get('qr_data', '')
                title = qr_item.get('title', '')
                description = qr_item.get('description', '')
                
                if self.save_qr_image(qr_data, filepath, title, description, **image_options):
                    saved_files.append(str(filepath))
                    self._logger.info(f"Saved QR {fragment_num}/{total_fragments}: {filepath}")
                else:
                    self._logger.error(f"Failed to save QR {fragment_num}/{total_fragments}: {filepath}")
                    
            except Exception as e:
                self._logger.error(f"Error saving QR {fragment_num}/{total_fragments} to {filepath}: {e}")
        
        return saved_files