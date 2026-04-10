from core.state_manager import StateManager
from core.models import ResearchReport, ResearchState
from modules.classifier import classify_intent
from modules.entity_resolver import resolve_entities
from modules.search import run_discovery_search
from modules.angle_generator import generate_research_angles
from modules.researcher import perform_parallel_research
from modules.extractor import extract_insights, map_evidence
from modules.synthesizer import (
    build_report_sections, 
    detect_data_conflicts, 
    perform_quality_audit, 
    generate_executive_summary,
    generate_dashboard_json
)
from utils.logger import PipelineLogger, get_logger

logger = get_logger("Core.Orchestrator")

class ResearchOrchestrator:
    def __init__(self, query: str, progress_callback=None):
        self.state_manager = StateManager(query)
        self.pipeline_log = PipelineLogger("ResearchPipeline")
        self.progress_callback = progress_callback

    def run(self) -> ResearchReport:
        """Executes the full 8-stage research orchestration flow."""
        self.pipeline_log.start(f"for query: {self.state_manager.state.input_query}")
        self._notify_progress(0, "Initializing pipeline...")
        
        try:
            # Stage 1: Classification
            self._notify_progress(10, "Classifying query intent...")
            self._run_stage("Classification", classify_intent, self.state_manager.state.input_query, "intent")
            
            # Stage 2: Entity Resolution
            self._notify_progress(20, "Resolving target entity...")
            self._run_stage("Entity Resolution", resolve_entities, self.state_manager.state.intent, "resolved_entity")
            
            # Stage 3: Discovery Search
            self._notify_progress(30, "Running initial search discovery...")
            self._run_stage("Discovery Search", run_discovery_search, self.state_manager.state.intent, "discovery_results")
            
            # Stage 4: Angle Generation
            self._notify_progress(40, "Generating research angles...")
            angles_result = generate_research_angles(self.state_manager.state.intent, self.state_manager.state.discovery_results)
            self.state_manager.update(angles=angles_result)
            
            # Stage 5: Parallel Research Execution
            self._notify_progress(50, f"Performing deep research (Parallel Workers: {len(self.state_manager.state.angles)})...")
            self._run_stage("Parallel Research", perform_parallel_research, self.state_manager.state.angles, "sources_by_angle")
            
            # Stage 6: Extraction + Evidence Mapping
            self._notify_progress(70, "Extracting insights and mapping evidence...")
            self._run_extraction_stage()
            
            # Stage 7: Synthesis
            self._notify_progress(85, "Synthesizing report and auditing quality...")
            self._run_synthesis_stage()
            
            # Stage 8: Report Generation
            self._notify_progress(95, "Formatting final report...")
            report = self._assemble_final_report()
            self.state_manager.update(report=report)
            
            self._notify_progress(100, "Research complete.")
            self.pipeline_log.end(self.state_manager.get_summary())
            return report

        except Exception as e:
            self.pipeline_log.error("Pipeline crashed", e)
            self.state_manager.add_error(str(e))
            self._notify_progress(-1, f"Error: {str(e)}")
            raise

    def _notify_progress(self, percent: int, message: str):
        if self.progress_callback:
            self.progress_callback(percent, message)

    def _run_stage(self, name: str, func, input_data, state_key: str):
        stage_log = PipelineLogger(name)
        stage_log.start()
        try:
            result = func(input_data)
            self.state_manager.update(**{state_key: result})
            stage_log.end()
        except Exception as e:
            stage_log.error(f"Stage {name} failed", e)
            self.state_manager.add_error(f"{name}: {str(e)}")
            raise

    def _run_extraction_stage(self):
        stage_log = PipelineLogger("Extraction & Mapping")
        stage_log.start()
        
        all_claims = []
        all_sources = []
        for angle_id, sources in self.state_manager.state.sources_by_angle.items():
            all_sources.extend(sources)
            all_claims.extend(extract_insights(angle_id, sources))
            
        evidence = map_evidence(all_claims, all_sources)
        
        self.state_manager.update(all_claims=all_claims, evidence=evidence)
        stage_log.end(f"Extracted {len(all_claims)} claims and {len(evidence)} evidence bullets")

    def _run_synthesis_stage(self):
        stage_log = PipelineLogger("Synthesis & Quality")
        stage_log.start()
        
        sections = build_report_sections(self.state_manager.state.angles, self.state_manager.state.all_claims)
        conflicts = detect_data_conflicts(self.state_manager.state.all_claims)
        
        all_sources = []
        for sources in self.state_manager.state.sources_by_angle.values():
            all_sources.extend(sources)
            
        quality = perform_quality_audit(all_sources, self.state_manager.state.evidence, sections)
        
        self.state_manager.update(sections=sections, conflicts=conflicts)
        # Quality check isn't stored in state directly but used for report
        self.current_quality = quality 
        
        stage_log.end()

    def _assemble_final_report(self) -> ResearchReport:
        state = self.state_manager.state
        
        risks = [
            "Some sources may be inaccessible or blocked during fetch.",
            "Claims are extracted automatically and may need analyst validation.",
        ]
        if not self.current_quality.passed:
            risks.append("Quality thresholds were not fully met; treat conclusions as provisional.")
            
        watch_next = [
            "Track next quarterly earnings release and guidance changes.",
            "Monitor major competitor announcements and market-share updates.",
            "Watch macro factors impacting demand and valuation sentiment.",
        ]
        
        # Generate strict JSON for dashboards
        dashboard_data = generate_dashboard_json(state.all_claims, state.intent)
        
        return ResearchReport(
            executive_summary=generate_executive_summary(state.sections),
            sections=state.sections,
            evidence_bullets=state.evidence,
            risks_uncertainties=risks,
            conflicts=state.conflicts,
            what_to_watch_next=watch_next,
            quality_checks=self.current_quality,
            charts=dashboard_data["charts"],
            networks=dashboard_data["networks"],
            timeline=dashboard_data["timeline"],
            json_output=dashboard_data
        )
