import os
import argparse
from pathlib import Path
from tqdm import tqdm
import zipfile
import pillow_heif
from PIL import Image
import shutil
import logging

class ImageConverter:
    def __init__(self, input_dir, output_dir=None, output_format='jpg'):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else self.input_dir / 'converted'
        self.output_format = output_format.lower()
        
        # Create output directory if not exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            filename=self.output_dir / 'conversion.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def convert(self):
        """Main conversion method"""
        files = [f for f in self.input_dir.iterdir() if self.is_supported_file(f.name)]
        
        if not files:
            logging.warning(f"No supported files found in {self.input_dir}")
            return

        for file in tqdm(files, desc="Converting files"):
            try:
                if file.suffix.lower() == '.livp':
                    self.livp_to_image(file)
                elif file.suffix.lower() == '.heic':
                    self.heic_to_image(file)
            except Exception as e:
                logging.error(f"Failed to convert {file.name}: {str(e)}")

    def is_supported_file(self, filename):
        """Check if file is supported format"""
        return filename.lower().endswith(('.livp', '.heic'))

    def livp_to_image(self, livp_file):
        """Convert LIVP file to target format"""
        with zipfile.ZipFile(livp_file) as zf:
            for item in zf.namelist():
                if item.lower().endswith('.heic'):
                    # Extract HEIC file
                    heic_path = self.output_dir / item
                    zf.extract(item, self.output_dir)
                    
                    # Convert HEIC to target format
                    self.convert_heic(heic_path, livp_file.stem)
                    
                    # Clean up extracted HEIC file
                    heic_path.unlink()
                    break

    def heic_to_image(self, heic_file):
        """Convert HEIC file to target format"""
        self.convert_heic(heic_file, heic_file.stem)

    def convert_heic(self, heic_path, output_stem):
        """Convert HEIC file to target format"""
        heif_file = pillow_heif.read_heif(heic_path)
        image = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
        )
        
        output_path = self.output_dir / f"{output_stem}.{self.output_format}"
        image.save(output_path, format="JPEG" if self.output_format == "jpg" else "PNG")

def main():
    parser = argparse.ArgumentParser(description='Convert LIVP/HEIC files to JPG/PNG')
    parser.add_argument('input_dir', help='Directory containing LIVP/HEIC files')
    parser.add_argument('-o', '--output_dir', help='Output directory (default: input_dir/converted)')
    parser.add_argument('-f', '--format', choices=['jpg', 'png'], default='jpg',
                       help='Output format (default: jpg)')
    
    args = parser.parse_args()
    
    converter = ImageConverter(args.input_dir, args.output_dir, args.format)
    converter.convert()

if __name__ == '__main__':
    main()
