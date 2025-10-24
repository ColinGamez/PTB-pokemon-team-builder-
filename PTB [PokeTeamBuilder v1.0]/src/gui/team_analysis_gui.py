"""
Team Analysis GUI component.
Provides comprehensive team analysis with visual charts and recommendations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TeamAnalysisFrame(tk.Frame):
    """Team analysis interface frame."""
    
    def __init__(self, parent, theme_manager, team=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.current_team = team
        self.analysis_results = None
        
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
        
        if self.current_team:
            self._analyze_team()
    
    def _create_widgets(self):
        """Create all widgets for the analysis interface."""
        # Header
        self.header_frame = self.theme_manager.create_styled_frame(self)
        self.title_label = self.theme_manager.create_styled_label(
            self.header_frame,
            text="📊 Team Analysis",
            font=('Arial', 18, 'bold')
        )
        
        # Control panel
        self.control_frame = self.theme_manager.create_styled_frame(self)
        
        self.analyze_btn = self.theme_manager.create_styled_button(
            self.control_frame,
            text="🔍 Analyze Team",
            command=self._analyze_team
        )
        
        self.export_btn = self.theme_manager.create_styled_button(
            self.control_frame,
            text="📊 Export Report",
            command=self._export_analysis
        )
        
        # Results notebook
        self.results_notebook = ttk.Notebook(self)
        
        # Overview tab
        self.overview_frame = self.theme_manager.create_styled_frame(self.results_notebook)
        self.results_notebook.add(self.overview_frame, text="Overview")
        
        # Type coverage tab
        self.type_frame = self.theme_manager.create_styled_frame(self.results_notebook)
        self.results_notebook.add(self.type_frame, text="Type Coverage")
        
        # Weaknesses tab
        self.weakness_frame = self.theme_manager.create_styled_frame(self.results_notebook)
        self.results_notebook.add(self.weakness_frame, text="Weaknesses")
        
        # Stats tab
        self.stats_frame = self.theme_manager.create_styled_frame(self.results_notebook)
        self.results_notebook.add(self.stats_frame, text="Statistics")
        
        # Recommendations tab
        self.recommendations_frame = self.theme_manager.create_styled_frame(self.results_notebook)
        self.results_notebook.add(self.recommendations_frame, text="Recommendations")
        
        # Create content for each tab
        self._create_overview_content()
        self._create_type_content()
        self._create_weakness_content()
        self._create_stats_content()
        self._create_recommendations_content()
    
    def _setup_layout(self):
        """Setup the layout of all widgets."""
        # Header
        self.header_frame.pack(fill=tk.X, padx=10, pady=5)
        self.title_label.pack(side=tk.LEFT, padx=10)
        
        # Control panel
        self.control_frame.pack(fill=tk.X, padx=10, pady=5)
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
        # Results
        self.results_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _bind_events(self):
        """Bind events for the analysis interface."""
        pass
    
    def _create_overview_content(self):
        """Create overview tab content."""
        # Team summary
        self.summary_label = self.theme_manager.create_styled_label(
            self.overview_frame,
            text="Team Summary",
            font=('Arial', 14, 'bold')
        )
        self.summary_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Summary text
        self.summary_text = tk.Text(
            self.overview_frame,
            height=8,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.summary_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Overall score
        self.score_frame = self.theme_manager.create_styled_frame(self.overview_frame)
        self.score_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.score_label = self.theme_manager.create_styled_label(
            self.score_frame,
            text="Overall Score:",
            font=('Arial', 12, 'bold')
        )
        self.score_label.pack(side=tk.LEFT, padx=5)
        
        self.score_value = self.theme_manager.create_styled_label(
            self.score_frame,
            text="--/100",
            font=('Arial', 12)
        )
        self.score_value.pack(side=tk.LEFT, padx=5)
        
        # Score progress bar
        self.score_progress = ttk.Progressbar(
            self.score_frame,
            mode='determinate',
            length=200
        )
        self.score_progress.pack(side=tk.LEFT, padx=10)
    
    def _create_type_content(self):
        """Create type coverage tab content."""
        # Type coverage chart
        self.type_label = self.theme_manager.create_styled_label(
            self.type_frame,
            text="Type Coverage Analysis",
            font=('Arial', 14, 'bold')
        )
        self.type_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Coverage list
        self.coverage_frame = self.theme_manager.create_styled_frame(self.type_frame)
        self.coverage_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for type coverage
        self.coverage_tree = ttk.Treeview(
            self.coverage_frame,
            columns=('Type', 'Count', 'Percentage'),
            show='headings',
            height=10
        )
        
        self.coverage_tree.heading('Type', text='Type')
        self.coverage_tree.heading('Count', text='Pokemon Count')
        self.coverage_tree.heading('Percentage', text='Coverage %')
        
        self.coverage_tree.column('Type', width=120)
        self.coverage_tree.column('Count', width=100)
        self.coverage_tree.column('Percentage', width=100)
        
        # Scrollbar for coverage tree
        coverage_scrollbar = ttk.Scrollbar(self.coverage_frame, orient=tk.VERTICAL, command=self.coverage_tree.yview)
        self.coverage_tree.configure(yscrollcommand=coverage_scrollbar.set)
        
        self.coverage_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        coverage_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_weakness_content(self):
        """Create weakness analysis tab content."""
        self.weakness_label = self.theme_manager.create_styled_label(
            self.weakness_frame,
            text="Team Weaknesses",
            font=('Arial', 14, 'bold')
        )
        self.weakness_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Weakness list
        self.weakness_listbox = tk.Listbox(
            self.weakness_frame,
            height=12
        )
        self.weakness_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Weakness scrollbar
        weakness_scrollbar = ttk.Scrollbar(self.weakness_frame, orient=tk.VERTICAL, command=self.weakness_listbox.yview)
        self.weakness_listbox.configure(yscrollcommand=weakness_scrollbar.set)
        weakness_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_stats_content(self):
        """Create statistics tab content."""
        self.stats_label = self.theme_manager.create_styled_label(
            self.stats_frame,
            text="Team Statistics",
            font=('Arial', 14, 'bold')
        )
        self.stats_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Stats display
        self.stats_text = tk.Text(
            self.stats_frame,
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def _create_recommendations_content(self):
        """Create recommendations tab content."""
        self.rec_label = self.theme_manager.create_styled_label(
            self.recommendations_frame,
            text="Improvement Recommendations",
            font=('Arial', 14, 'bold')
        )
        self.rec_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Recommendations list
        self.rec_text = tk.Text(
            self.recommendations_frame,
            height=15,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.rec_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    def set_team(self, team):
        """Set the team to analyze."""
        self.current_team = team
        if team:
            self._analyze_team()
    
    def _analyze_team(self):
        """Perform comprehensive team analysis."""
        if not self.current_team:
            messagebox.showwarning("No Team", "Please load a team first.")
            return
        
        try:
            from ..teambuilder.analyzer import TeamAnalyzer
            
            # Create analyzer and analyze team
            analyzer = TeamAnalyzer(self.current_team)
            self.analysis_results = analyzer.analyze_team()
            
            # Update all displays
            self._update_overview()
            self._update_type_coverage()
            self._update_weaknesses()
            self._update_statistics()
            self._update_recommendations()
            
            logger.info(f"Team analysis completed for {self.current_team.name}")
            
        except ImportError:
            # Fallback if analyzer not implemented
            self._perform_basic_analysis()
        except Exception as e:
            logger.error(f"Team analysis failed: {e}")
            messagebox.showerror("Analysis Error", f"Failed to analyze team: {e}")
    
    def _perform_basic_analysis(self):
        """Perform basic analysis if full analyzer not available."""
        if not self.current_team:
            return
        
        # Basic analysis
        active_pokemon = self.current_team.get_active_pokemon()
        team_size = len(active_pokemon)
        
        # Create mock analysis results
        self.analysis_results = {
            'overall_score': min(100, team_size * 15),  # Basic scoring
            'team_size': team_size,
            'type_coverage': self._analyze_basic_types(active_pokemon),
            'weaknesses': self._analyze_basic_weaknesses(active_pokemon),
            'recommendations': self._generate_basic_recommendations(team_size)
        }
        
        # Update displays
        self._update_overview()
        self._update_type_coverage()
        self._update_weaknesses()
        self._update_statistics()
        self._update_recommendations()
    
    def _analyze_basic_types(self, pokemon_list):
        """Basic type coverage analysis."""
        type_counts = {}
        for pokemon in pokemon_list:
            for ptype in pokemon.types:
                type_name = ptype.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
        return type_counts
    
    def _analyze_basic_weaknesses(self, pokemon_list):
        """Basic weakness analysis."""
        weaknesses = []
        if len(pokemon_list) < 6:
            weaknesses.append("Team is not full (incomplete team)")
        
        type_counts = self._analyze_basic_types(pokemon_list)
        if len(type_counts) < 3:
            weaknesses.append("Limited type diversity")
        
        return weaknesses
    
    def _generate_basic_recommendations(self, team_size):
        """Generate basic recommendations."""
        recommendations = []
        
        if team_size < 6:
            recommendations.append(f"Add {6 - team_size} more Pokemon to complete your team")
        
        if team_size == 0:
            recommendations.append("Start by adding your first Pokemon")
        elif team_size < 3:
            recommendations.append("Add Pokemon of different types for better coverage")
        
        recommendations.append("Consider balancing offensive and defensive capabilities")
        recommendations.append("Ensure your team has good move coverage")
        
        return recommendations
    
    def _update_overview(self):
        """Update the overview tab."""
        if not self.analysis_results:
            return
        
        # Update summary text
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        summary = f"""Team: {self.current_team.name}
Format: {self.current_team.format.value}
Era: {self.current_team.era.value}
Size: {self.analysis_results.get('team_size', 0)}/6

Analysis Summary:
- Overall team strength: {self.analysis_results.get('overall_score', 0)}/100
- Type diversity: {len(self.analysis_results.get('type_coverage', {}))} types
- Major weaknesses: {len(self.analysis_results.get('weaknesses', []))} identified
"""
        
        self.summary_text.insert(1.0, summary)
        self.summary_text.config(state=tk.DISABLED)
        
        # Update score
        score = self.analysis_results.get('overall_score', 0)
        self.score_value.config(text=f"{score}/100")
        self.score_progress['value'] = score
    
    def _update_type_coverage(self):
        """Update the type coverage tab."""
        # Clear existing items
        for item in self.coverage_tree.get_children():
            self.coverage_tree.delete(item)
        
        if not self.analysis_results:
            return
        
        type_coverage = self.analysis_results.get('type_coverage', {})
        total_pokemon = self.analysis_results.get('team_size', 1)
        
        for type_name, count in type_coverage.items():
            percentage = (count / total_pokemon) * 100
            self.coverage_tree.insert('', tk.END, values=(
                type_name.title(),
                count,
                f"{percentage:.1f}%"
            ))
    
    def _update_weaknesses(self):
        """Update the weaknesses tab."""
        self.weakness_listbox.delete(0, tk.END)
        
        if not self.analysis_results:
            return
        
        weaknesses = self.analysis_results.get('weaknesses', [])
        
        if not weaknesses:
            self.weakness_listbox.insert(tk.END, "No major weaknesses identified!")
        else:
            for weakness in weaknesses:
                self.weakness_listbox.insert(tk.END, f"⚠️ {weakness}")
    
    def _update_statistics(self):
        """Update the statistics tab."""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        if not self.analysis_results or not self.current_team:
            self.stats_text.insert(1.0, "No statistics available.")
            self.stats_text.config(state=tk.DISABLED)
            return
        
        # Generate statistics display
        active_pokemon = self.current_team.get_active_pokemon()
        
        stats_info = "TEAM STATISTICS\n" + "="*30 + "\n\n"
        
        if active_pokemon:
            # Average stats
            stats_info += "Average Base Stats:\n"
            total_stats = {'hp': 0, 'attack': 0, 'defense': 0, 'special_attack': 0, 'special_defense': 0, 'speed': 0}
            
            for pokemon in active_pokemon:
                for stat_name, stat_value in pokemon.base_stats.get_all_stats().items():
                    total_stats[stat_name] += stat_value
            
            team_size = len(active_pokemon)
            for stat_name, total in total_stats.items():
                average = total / team_size
                stats_info += f"  {stat_name.replace('_', ' ').title()}: {average:.1f}\n"
            
            stats_info += f"\nTeam Composition:\n"
            for i, pokemon in enumerate(active_pokemon, 1):
                stats_info += f"  {i}. {pokemon.name} (Lv.{pokemon.level})\n"
                stats_info += f"     Types: {', '.join([t.value.title() for t in pokemon.types])}\n"
                stats_info += f"     Nature: {pokemon.nature.value.title()}\n\n"
        
        else:
            stats_info += "No Pokemon in team to analyze."
        
        self.stats_text.insert(1.0, stats_info)
        self.stats_text.config(state=tk.DISABLED)
    
    def _update_recommendations(self):
        """Update the recommendations tab."""
        self.rec_text.config(state=tk.NORMAL)
        self.rec_text.delete(1.0, tk.END)
        
        if not self.analysis_results:
            self.rec_text.insert(1.0, "No recommendations available.")
            self.rec_text.config(state=tk.DISABLED)
            return
        
        recommendations = self.analysis_results.get('recommendations', [])
        
        rec_text = "TEAM IMPROVEMENT RECOMMENDATIONS\n" + "="*40 + "\n\n"
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                rec_text += f"{i}. {rec}\n\n"
        else:
            rec_text += "Your team looks great! No specific recommendations at this time.\n"
        
        rec_text += "\nGeneral Tips:\n"
        rec_text += "• Ensure type diversity for better coverage\n"
        rec_text += "• Balance offensive and defensive capabilities\n"
        rec_text += "• Consider move synergies between team members\n"
        rec_text += "• Check for common weaknesses across your team\n"
        rec_text += "• Adapt your team for your preferred battle format\n"
        
        self.rec_text.insert(1.0, rec_text)
        self.rec_text.config(state=tk.DISABLED)
    
    def _export_analysis(self):
        """Export analysis results to a file."""
        if not self.analysis_results:
            messagebox.showwarning("No Analysis", "Please analyze a team first.")
            return
        
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Analysis Report"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    f.write(f"POKEMON TEAM ANALYSIS REPORT\n")
                    f.write(f"{'='*40}\n\n")
                    f.write(f"Team: {self.current_team.name}\n")
                    f.write(f"Format: {self.current_team.format.value}\n")
                    f.write(f"Era: {self.current_team.era.value}\n")
                    f.write(f"Overall Score: {self.analysis_results.get('overall_score', 0)}/100\n\n")
                    
                    # Add more report details here
                    f.write("This analysis was generated by Pokemon Team Builder v1.0\n")
                
                messagebox.showinfo("Export Successful", f"Analysis report saved to {filename}")
                logger.info(f"Analysis report exported to {filename}")
        
        except Exception as e:
            logger.error(f"Export failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export analysis: {str(e)}")