#!/usr/bin/env python3
"""
Validation script for converted Quarto files
Checks quality and completeness of PDF conversions
"""

import os
import re
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

class QuartoValidator:
    def __init__(self, chapters_dir="./chapters"):
        self.chapters_dir = Path(chapters_dir)
        self.validation_rules = {
            'yaml_frontmatter': r'^---\n.*?\n---\n',
            'equations_inline': r'\$[^$]+\$',
            'equations_display': r'\$\$[^$]+\$\$',
            'headings': r'^#+\s+.+$',
            'figures': r'!\[.*?\]\(.*?\)',
            'tables': r'\|.*?\|',
            'code_blocks': r'```.*?```'
        }
        
    def validate_file(self, qmd_path):
        """Validate a single QMD file"""
        try:
            with open(qmd_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                'file': qmd_path.name,
                'error': f"Could not read file: {e}",
                'valid': False
            }
        
        # Basic validation checks
        results = {
            'file': qmd_path.name,
            'file_path': str(qmd_path),
            'has_frontmatter': bool(re.search(self.validation_rules['yaml_frontmatter'], content, re.DOTALL)),
            'inline_equations': len(re.findall(self.validation_rules['equations_inline'], content)),
            'display_equations': len(re.findall(self.validation_rules['equations_display'], content)),
            'heading_count': len(re.findall(self.validation_rules['headings'], content, re.MULTILINE)),
            'figure_count': len(re.findall(self.validation_rules['figures'], content)),
            'table_count': len(re.findall(self.validation_rules['tables'], content)),
            'code_block_count': len(re.findall(self.validation_rules['code_blocks'], content, re.DOTALL)),
            'word_count': len(content.split()),
            'character_count': len(content),
            'file_size_kb': qmd_path.stat().st_size / 1024,
            'created_date': datetime.fromtimestamp(qmd_path.stat().st_ctime).strftime('%Y-%m-%d %H:%M'),
            'modified_date': datetime.fromtimestamp(qmd_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        }
        
        # Quality checks
        results['quality_score'] = self.calculate_quality_score(results, content)
        results['has_content'] = results['word_count'] > 100
        results['has_structure'] = results['heading_count'] > 0
        results['has_math'] = (results['inline_equations'] + results['display_equations']) > 0
        results['valid'] = all([
            results['has_frontmatter'],
            results['has_content'],
            results['has_structure']
        ])
        
        return results
    
    def calculate_quality_score(self, results, content):
        """Calculate a quality score for the converted content"""
        score = 0
        
        # Base points for having content
        if results['word_count'] > 100:
            score += 20
        if results['word_count'] > 1000:
            score += 10
        
        # Structure points
        score += min(results['heading_count'] * 5, 30)  # Max 30 points for headings
        
        # Math content points
        math_total = results['inline_equations'] + results['display_equations']
        score += min(math_total * 2, 20)  # Max 20 points for equations
        
        # Figures and tables
        score += min(results['figure_count'] * 3, 15)  # Max 15 points for figures
        score += min(results['table_count'] * 3, 10)   # Max 10 points for tables
        
        # Frontmatter
        if results['has_frontmatter']:
            score += 10
        
        # Penalize very short content
        if results['word_count'] < 50:
            score -= 20
        
        return max(0, min(100, score))  # Keep between 0-100
    
    def validate_all_files(self):
        """Validate all QMD files in the chapters directory"""
        if not self.chapters_dir.exists():
            print(f"Chapters directory does not exist: {self.chapters_dir}")
            return [], {}
        
        results = []
        
        # Find all .qmd files recursively
        for qmd_file in self.chapters_dir.rglob("*.qmd"):
            result = self.validate_file(qmd_file)
            results.append(result)
        
        if not results:
            print("No .qmd files found in chapters directory")
            return [], {}
        
        # Generate summary statistics
        df = pd.DataFrame(results)
        
        summary = {
            'total_files': len(results),
            'valid_files': df['valid'].sum(),
            'files_with_frontmatter': df['has_frontmatter'].sum(),
            'files_with_content': df['has_content'].sum(),
            'files_with_math': df['has_math'].sum(),
            'total_words': df['word_count'].sum(),
            'total_equations': (df['inline_equations'] + df['display_equations']).sum(),
            'total_figures': df['figure_count'].sum(),
            'total_tables': df['table_count'].sum(),
            'avg_quality_score': df['quality_score'].mean(),
            'avg_word_count': df['word_count'].mean(),
            'categories': {}
        }
        
        # Category breakdown
        for category in ['optimization', 'statistics', 'machine_learning']:
            category_files = [r for r in results if category in r['file_path']]
            if category_files:
                category_df = pd.DataFrame(category_files)
                summary['categories'][category] = {
                    'file_count': len(category_files),
                    'avg_quality_score': category_df['quality_score'].mean(),
                    'total_words': category_df['word_count'].sum(),
                    'total_equations': (category_df['inline_equations'] + category_df['display_equations']).sum()
                }
        
        return results, summary
    
    def generate_report(self, output_dir="./automation/logs"):
        """Generate comprehensive validation report"""
        results, summary = self.validate_all_files()
        
        if not results:
            print("No files to validate")
            return
        
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save detailed results
        df = pd.DataFrame(results)
        detailed_report_path = output_dir / f'validation_detailed_{timestamp}.csv'
        df.to_csv(detailed_report_path, index=False)
        
        # Save summary
        summary_path = output_dir / f'validation_summary_{timestamp}.json'
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary to console
        print("\n=== VALIDATION SUMMARY ===")
        print(f"Total files: {summary['total_files']}")
        print(f"Valid files: {summary['valid_files']} ({summary['valid_files']/summary['total_files']*100:.1f}%)")
        print(f"Files with frontmatter: {summary['files_with_frontmatter']}")
        print(f"Files with content: {summary['files_with_content']}")
        print(f"Files with math: {summary['files_with_math']}")
        print(f"Average quality score: {summary['avg_quality_score']:.1f}/100")
        print(f"Total words: {summary['total_words']:,}")
        print(f"Total equations: {summary['total_equations']}")
        print(f"Total figures: {summary['total_figures']}")
        print(f"Total tables: {summary['total_tables']}")
        
        if summary['categories']:
            print("\n=== BY CATEGORY ===")
            for category, stats in summary['categories'].items():
                print(f"{category.title()}:")
                print(f"  Files: {stats['file_count']}")
                print(f"  Avg Quality: {stats['avg_quality_score']:.1f}/100")
                print(f"  Words: {stats['total_words']:,}")
                print(f"  Equations: {stats['total_equations']}")
        
        # Identify problem files
        problem_files = [r for r in results if not r['valid'] or r['quality_score'] < 50]
        if problem_files:
            print(f"\n=== PROBLEM FILES ({len(problem_files)}) ===")
            for file_info in problem_files:
                issues = []
                if not file_info['has_frontmatter']:
                    issues.append("No frontmatter")
                if not file_info['has_content']:
                    issues.append("No content")
                if not file_info['has_structure']:
                    issues.append("No structure")
                if file_info['quality_score'] < 50:
                    issues.append(f"Low quality ({file_info['quality_score']:.1f})")
                
                print(f"  {file_info['file']}: {', '.join(issues)}")
        
        print(f"\nDetailed report: {detailed_report_path}")
        print(f"Summary report: {summary_path}")
        
        return results, summary

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate converted Quarto files')
    parser.add_argument('--chapters-dir', default='./chapters',
                       help='Directory containing converted chapters')
    parser.add_argument('--output-dir', default='./automation/logs',
                       help='Directory for validation reports')
    
    args = parser.parse_args()
    
    validator = QuartoValidator(args.chapters_dir)
    results, summary = validator.generate_report(args.output_dir)
    
    # Exit with error code if validation issues found
    if summary and summary['valid_files'] < summary['total_files']:
        print(f"\nValidation completed with issues. {summary['total_files'] - summary['valid_files']} files have problems.")
        exit(1)
    else:
        print("\nAll files passed validation!")
        exit(0)

if __name__ == "__main__":
    main()