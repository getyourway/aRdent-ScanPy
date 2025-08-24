#!/usr/bin/env python3
"""
ScanPad Lua Interactive - Interactive Lua Script QR Generator

Interactive terminal application for generating QR codes from demo Lua scripts.
Choose from available demo scripts and generate deployment QR codes automatically.
"""

import sys
import os
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ardent_scanpad.controllers.qr_generator import QRGeneratorController

try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
    QR_WARNING = ""
except ImportError:
    QR_AVAILABLE = False
    QR_WARNING = "\n⚠️  QR code dependencies not available. Install with: pip install qrcode[pil]\n"


class ScanPadLuaInteractive:
    """Interactive Lua script QR code generator"""
    
    def __init__(self):
        self.qr_generator = QRGeneratorController()
        self.script_dir = Path(__file__).parent / "demo_scripts"
        self.output_dir = Path(__file__).parent / "output"
        
    def run(self):
        """Main entry point"""
        self._print_header()
        
        if not QR_AVAILABLE:
            print(QR_WARNING)
            if not self._confirm("Continue anyway? QR codes won't be generated, only command strings"):
                return
        
        # Check demo_scripts directory
        if not self.script_dir.exists():
            print(f"❌ Demo scripts directory not found: {self.script_dir}")
            return
        
        # Enter interactive mode
        self._interactive_menu()
        
        print("\n👋 Lua Interactive session ended!")
    
    def _print_header(self):
        """Print application header"""
        print("\n" + "="*70)
        print("🛠️ aRdent ScanPad - Lua Script QR Generator")
        print("Generate QR codes from demo Lua scripts for device deployment")
        print("="*70)
        
        if QR_AVAILABLE:
            print("✅ QR code generation ready")
        else:
            print("❌ QR code generation not available (qrcode library missing)")
        
        print(f"📁 Demo scripts: {self.script_dir}")
        print(f"📤 Output directory: {self.output_dir}")
        print()
    
    def _interactive_menu(self):
        """Main interactive menu"""
        while True:
            print("\n🛠️ LUA SCRIPT QR GENERATOR:")
            print("="*50)
            print("1. 📋 List available demo scripts")
            print("2. 🔧 Generate QR from demo script")
            print("3. 📝 Generate QR from custom file")
            print("4. 🗑️  Generate clear Lua script QR")
            print("5. ℹ️  Generate Lua info QR")
            print("6. 📁 View generated QR codes")
            print("0. ❌ Exit")
            
            choice = input("\nSelect option (0-6): ").strip()
            
            try:
                if choice == "0":
                    break
                elif choice == "1":
                    self._list_demo_scripts()
                elif choice == "2":
                    self._generate_from_demo()
                elif choice == "3":
                    self._generate_from_custom_file()
                elif choice == "4":
                    self._generate_clear_script()
                elif choice == "5":
                    self._generate_script_info()
                elif choice == "6":
                    self._view_output_directory()
                else:
                    print("❌ Invalid choice. Please select 0-6.")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                input("Press Enter to continue...")
    
    def _list_demo_scripts(self):
        """List all available demo scripts"""
        print("\n📋 AVAILABLE DEMO SCRIPTS")
        print("="*50)
        
        scripts = self._get_demo_scripts()
        
        if not scripts:
            print("❌ No demo scripts found in demo_scripts/ directory")
            return
        
        for i, script_path in enumerate(scripts, 1):
            print(f"\n{i:2d}. 📜 {script_path.name}")
            
            # Show script info
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Extract description from comments
                description = "No description"
                for line in lines[:10]:  # Check first 10 lines
                    line = line.strip()
                    if line.startswith('-- ') and not line.startswith('-- Script'):
                        description = line[3:]
                        break
                    elif line.startswith('--- '):
                        description = line[4:]
                        break
                
                size = script_path.stat().st_size
                line_count = len(lines)
                
                print(f"     📄 Description: {description}")
                print(f"     📊 Size: {size} bytes, {line_count} lines")
                
            except Exception as e:
                print(f"     ❌ Error reading script: {e}")
        
        input(f"\nFound {len(scripts)} demo scripts. Press Enter to continue...")
    
    def _generate_from_demo(self):
        """Generate QR codes from selected demo script"""
        print("\n🔧 GENERATE QR FROM DEMO SCRIPT")
        print("="*40)
        
        scripts = self._get_demo_scripts()
        
        if not scripts:
            print("❌ No demo scripts found")
            return
        
        # Display scripts menu
        print("\nAvailable demo scripts:")
        for i, script_path in enumerate(scripts, 1):
            print(f"  {i:2d}. {script_path.name}")
        
        try:
            choice = int(input(f"\nSelect script (1-{len(scripts)}): "))
            if not (1 <= choice <= len(scripts)):
                print("❌ Invalid script selection")
                return
                
            selected_script = scripts[choice - 1]
            
        except ValueError:
            print("❌ Invalid input. Please enter a number.")
            return
        
        # Load and display script info
        try:
            with open(selected_script, 'r', encoding='utf-8') as f:
                script_content = f.read()
            
            script_size = len(script_content.encode('utf-8'))
            script_lines = len(script_content.split('\n'))
            
            print(f"\n📄 Selected Script: {selected_script.name}")
            print(f"📊 Size: {script_size} bytes, {script_lines} lines")
            
            # Show preview
            print(f"\n📖 Preview (first 10 lines):")
            print("-" * 50)
            preview_lines = script_content.split('\n')[:10]
            for i, line in enumerate(preview_lines, 1):
                print(f"{i:2d}| {line}")
            if len(script_content.split('\n')) > 10:
                print("...")
            print("-" * 50)
            
            if not self._confirm("\nGenerate QR codes for this script?"):
                return
            
            # QR generation options
            print("\n⚙️  QR Generation Options:")
            max_size = input("Max QR size (chars, default 1000): ").strip()
            try:
                max_size = int(max_size) if max_size else 1000
            except ValueError:
                max_size = 1000
            
            compression = input("Compression level (1-9, default 6): ").strip()
            try:
                compression = int(compression) if compression else 6
                compression = max(1, min(9, compression))
            except ValueError:
                compression = 6
            
            print(f"\n🔗 Generating QR codes...")
            print(f"   Max QR size: {max_size} chars")
            print(f"   Compression: {compression}")
            
            # Generate QR codes
            qr_commands = self.qr_generator.create_lua_script_qr(
                script_content, 
                max_qr_size=max_size, 
                compression_level=compression
            )
            
            # Display results
            print(f"\n✅ Generated {len(qr_commands)} QR code(s):")
            
            for i, command in enumerate(qr_commands):
                metadata = command.metadata
                fragment_info = ""
                if len(qr_commands) > 1:
                    if metadata.get('is_final_fragment'):
                        fragment_info = f" (Final - Execute)"
                    else:
                        fragment_info = f" (Fragment {i+1}/{len(qr_commands)})"
                
                qr_size = metadata.get('qr_size_chars', len(command.command_data))
                print(f"   {i+1}. QR Code{fragment_info}: {qr_size} chars")
            
            # Show compression stats
            if qr_commands:
                metadata = qr_commands[0].metadata
                print(f"\n📊 Compression Statistics:")
                print(f"   Original: {metadata.get('original_size_bytes', 0)} bytes")
                print(f"   Compressed: {metadata.get('compressed_size_bytes', 0)} bytes") 
                print(f"   Base64: {metadata.get('base64_size_chars', 0)} chars")
                print(f"   Ratio: {metadata.get('compression_ratio_percent', 0)}%")
            
            # Save QR codes
            if QR_AVAILABLE and self._confirm("\nSave QR codes to files now?"):
                script_name = selected_script.stem  # filename without extension
                self._save_lua_qr_sequence(qr_commands, script_name)
        
        except Exception as e:
            print(f"❌ Error processing script: {e}")
    
    def _generate_from_custom_file(self):
        """Generate QR codes from custom file"""
        print("\n📝 GENERATE QR FROM CUSTOM FILE")
        print("="*40)
        
        filename = input("Enter Lua script filename (with .lua extension): ").strip()
        if not filename:
            print("❌ No filename provided")
            return
        
        # Add .lua extension if missing
        if not filename.endswith('.lua'):
            filename += '.lua'
        
        # Try multiple locations
        script_path = None
        search_paths = [
            Path(filename),  # Absolute or relative to cwd
            Path(__file__).parent / filename,  # Relative to this script
            self.script_dir / filename,  # In demo_scripts
        ]
        
        for path in search_paths:
            if path.exists():
                script_path = path
                break
        
        if not script_path:
            print(f"❌ Script file not found: {filename}")
            print("Searched in:")
            for path in search_paths:
                print(f"  - {path}")
            return
        
        try:
            # Generate QR codes using existing method
            qr_commands = self.qr_generator.create_lua_script_from_file(script_path)
            
            print(f"✅ Generated {len(qr_commands)} QR code(s) from {script_path.name}")
            
            # Save QR codes
            if QR_AVAILABLE and self._confirm("Save QR codes to files now?"):
                script_name = script_path.stem
                self._save_lua_qr_sequence(qr_commands, script_name)
        
        except Exception as e:
            print(f"❌ Error processing custom file: {e}")
    
    def _generate_clear_script(self):
        """Generate QR code to clear Lua script"""
        print("\n🗑️  GENERATE CLEAR SCRIPT QR")
        print("="*30)
        print("This generates a QR code to clear/delete the currently")
        print("loaded Lua script from the device.")
        
        if not self._confirm("\nGenerate clear Lua script QR code?"):
            return
        
        try:
            command = self.qr_generator.create_lua_clear_command()
            
            print(f"\n✅ Clear command generated:")
            print(f"   Command: {command.command_data}")
            print(f"   Description: {command.description}")
            
            if QR_AVAILABLE and self._confirm("Save QR code to file now?"):
                self.output_dir.mkdir(exist_ok=True)
                filepath = self.output_dir / "clear_lua_script.png"
                
                if command.save(filepath):
                    print(f"✅ Clear QR saved: {filepath}")
                else:
                    print("❌ Failed to save QR code")
            
        except Exception as e:
            print(f"❌ Error generating clear command: {e}")
    
    def _generate_script_info(self):
        """Generate QR code to get Lua script info"""
        print("\nℹ️  GENERATE LUA INFO QR")
        print("="*30)
        print("This generates a QR code to request information about")
        print("the currently loaded Lua script from the device.")
        
        if not self._confirm("\nGenerate Lua script info QR code?"):
            return
        
        try:
            command = self.qr_generator.create_lua_info_command()
            
            print(f"\n✅ Info command generated:")
            print(f"   Command: {command.command_data}")
            print(f"   Description: {command.description}")
            
            if QR_AVAILABLE and self._confirm("Save QR code to file now?"):
                self.output_dir.mkdir(exist_ok=True)
                filepath = self.output_dir / "lua_script_info.png"
                
                if command.save(filepath):
                    print(f"✅ Info QR saved: {filepath}")
                else:
                    print("❌ Failed to save QR code")
            
        except Exception as e:
            print(f"❌ Error generating info command: {e}")
    
    def _view_output_directory(self):
        """View contents of output directory"""
        print("\n📁 OUTPUT DIRECTORY CONTENTS")
        print("="*50)
        
        if not self.output_dir.exists():
            print(f"❌ Output directory doesn't exist: {self.output_dir}")
            return
        
        png_files = list(self.output_dir.glob("*.png"))
        
        if not png_files:
            print("📂 Output directory is empty")
            return
        
        print(f"📂 Directory: {self.output_dir}")
        print(f"📊 Found {len(png_files)} QR code(s):\n")
        
        for i, file_path in enumerate(sorted(png_files), 1):
            stat = file_path.stat()
            size_kb = stat.st_size / 1024
            
            print(f"{i:2d}. 📱 {file_path.name}")
            print(f"     📊 Size: {size_kb:.1f} KB")
            
            # Try to guess file type from name
            if 'clear' in file_path.name.lower():
                print("     🗑️  Type: Clear Lua script")
            elif 'info' in file_path.name.lower():
                print("     ℹ️   Type: Lua script info")
            elif 'part' in file_path.name.lower() or 'fragment' in file_path.name.lower():
                print("     🧩 Type: Multi-part Lua script")
            else:
                print("     📜 Type: Lua script deployment")
        
        input(f"\nPress Enter to continue...")
    
    def _get_demo_scripts(self) -> List[Path]:
        """Get list of demo script files"""
        if not self.script_dir.exists():
            return []
        
        scripts = list(self.script_dir.glob("*.lua"))
        return sorted(scripts)
    
    def _save_lua_qr_sequence(self, qr_commands, script_name):
        """Save Lua QR sequence with descriptive filenames"""
        try:
            self.output_dir.mkdir(exist_ok=True)
            
            saved_files = []
            total_fragments = len(qr_commands)
            
            for i, command in enumerate(qr_commands):
                fragment_num = i + 1
                
                if total_fragments == 1:
                    filename = f"lua_{script_name}_deploy.png"
                else:
                    is_final = command.metadata.get('is_final_fragment', False)
                    if is_final:
                        filename = f"lua_{script_name}_final_execute.png"
                    else:
                        filename = f"lua_{script_name}_part_{fragment_num:02d}_of_{total_fragments:02d}.png"
                
                filepath = self.output_dir / filename
                
                if command.save(filepath):
                    saved_files.append(str(filepath))
                    print(f"✅ Saved: {filename}")
                else:
                    print(f"❌ Failed to save: {filename}")
            
            print(f"\n✅ Saved {len(saved_files)} Lua QR codes to {self.output_dir}")
            
            # Display deployment instructions
            if total_fragments > 1:
                print("\n📖 Deployment Instructions:")
                print("1. Flash firmware to your aRdent ScanPad")
                print("2. Scan QR codes in order:")
                for i, command in enumerate(qr_commands):
                    fragment_num = i + 1
                    is_final = command.metadata.get('is_final_fragment', False)
                    if is_final:
                        print(f"   {fragment_num}. Final (Execute) - deploys and runs script")
                    else:
                        print(f"   {fragment_num}. Fragment {fragment_num} - loads data")
                print("3. Script will be deployed and executed automatically")
            else:
                print("\n📖 Deployment Instructions:")
                print("1. Flash firmware to your aRdent ScanPad")  
                print("2. Scan the single QR code")
                print("3. Script will be deployed and executed automatically")
            
        except Exception as e:
            print(f"❌ Error saving Lua QR sequence: {e}")
    
    def _confirm(self, message: str) -> bool:
        """Ask for user confirmation"""
        response = input(f"{message} (y/n): ").strip().lower()
        return response in ['y', 'yes']


def main():
    """Main entry point"""
    try:
        app = ScanPadLuaInteractive()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()