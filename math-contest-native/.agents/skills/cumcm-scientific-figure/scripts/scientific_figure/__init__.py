"""Public figure API. No drawing or global rc mutation on import."""
from .style import PROFILE, style_context
from .templates import (FigureBundle, parametric_curve, time_phase_spectrum,
                        flow_field, regime_map, convergence_validation,
                        dual_axis_frequency, schematic)
from .export import export_bundle

__all__ = ["PROFILE", "style_context", "FigureBundle", "parametric_curve",
           "time_phase_spectrum", "flow_field", "regime_map",
           "convergence_validation", "dual_axis_frequency", "schematic", "export_bundle"]
