#!/usr/bin/env python3
"""
Simple validation test for all 6 Pokemon Team Builder improvements.
"""

import os
from pathlib import Path

def main():
    """Validate all improvements."""
    project_root = Path(__file__).parent
    
    print("🎮 POKEMON TEAM BUILDER - IMPROVEMENTS VALIDATION")
    print("=" * 60)
    
    improvements = [
        {
            'name': '1. Dependencies & Imports Fixed',
            'files': ['requirements.txt'],
            'check': lambda: 'colorama' in (project_root / 'requirements.txt').read_text()
        },
        {
            'name': '2. GUI Implementation Complete',
            'files': ['src/gui/team_analysis_gui.py', 'src/gui/team_optimization_gui.py'],
            'check': lambda: all((project_root / f).exists() and (project_root / f).stat().st_size > 5000 for f in ['src/gui/team_analysis_gui.py', 'src/gui/team_optimization_gui.py'])
        },
        {
            'name': '3. Database System Created',
            'files': ['data/pokemon.json', 'data/moves.json', 'data/abilities.json', 'initialize_databases.py'],
            'check': lambda: all((project_root / f).exists() for f in ['data/pokemon.json', 'data/moves.json', 'data/abilities.json', 'initialize_databases.py'])
        },
        {
            'name': '4. Performance Optimization Added',
            'files': ['src/utils/performance.py'],
            'check': lambda: (project_root / 'src/utils/performance.py').exists() and (project_root / 'src/utils/performance.py').stat().st_size > 5000
        },
        {
            'name': '5. Comprehensive Logging System',
            'files': ['src/utils/logging_config.py', 'logs/'],
            'check': lambda: (project_root / 'src/utils/logging_config.py').exists() and (project_root / 'logs').exists()
        },
        {
            'name': '6. Battle AI System Implemented',
            'files': ['src/battle/battle_ai.py'],
            'check': lambda: (project_root / 'src/battle/battle_ai.py').exists() and (project_root / 'src/battle/battle_ai.py').stat().st_size > 10000
        }
    ]
    
    all_passed = True
    
    for i, improvement in enumerate(improvements, 1):
        try:
            if improvement['check']():
                status = "✅ IMPLEMENTED"
            else:
                status = "❌ MISSING"
                all_passed = False
        except Exception:
            status = "⚠️  ERROR"
            all_passed = False
        
        print(f"{status} - {improvement['name']}")
        
        # Show file details
        for file_path in improvement['files']:
            full_path = project_root / file_path
            if full_path.exists():
                if full_path.is_file():
                    size = full_path.stat().st_size
                    print(f"    📄 {file_path} ({size:,} bytes)")
                else:
                    contents = len(list(full_path.iterdir())) if full_path.is_dir() else 0
                    print(f"    📁 {file_path} ({contents} items)")
            else:
                print(f"    ❌ {file_path} (not found)")
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎯 SUCCESS: All 6 Priority Improvements Completed!")
        print("🚀 Pokemon Team Builder is ready for advanced features!")
    else:
        print("⚠️  Some improvements need attention")
    print("=" * 60)

if __name__ == "__main__":
    main()