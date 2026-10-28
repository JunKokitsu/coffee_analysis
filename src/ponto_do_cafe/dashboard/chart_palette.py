from dataclasses import dataclass

LIGHT_SEQUENTIAL = ("#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b")
DARK_SEQUENTIAL = ("#0d366b", "#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4", "#cde2fb")


@dataclass(frozen=True)
class ChartPalette:
    surface: str
    primary_ink: str
    secondary_ink: str
    muted_ink: str
    gridline: str
    baseline: str
    highlight: str
    negative: str
    recessive_mark: str
    sequential: tuple[str, ...]
    map_style: str

    @classmethod
    def for_theme(cls, theme: str | None) -> "ChartPalette":
        if theme == "dark":
            return cls("#1a1a19", "#ffffff", "#c3c2b7", "#898781", "#2c2c2a", "#383835", "#3987e5", "#e66767", "#5d5c58", DARK_SEQUENTIAL, "carto-darkmatter")
        return cls("#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#2a78d6", "#e34948", "#c3c2b7", LIGHT_SEQUENTIAL, "carto-positron")

    def sequential_scale(self) -> list[tuple[float, str]]:
        last = len(self.sequential) - 1
        return [(position / last, color) for position, color in enumerate(self.sequential)]

    def layout(self) -> dict[str, object]:
        axis = {"gridcolor": self.gridline, "linecolor": self.baseline, "zerolinecolor": self.baseline, "tickfont": {"color": self.muted_ink}, "title": {"font": {"color": self.secondary_ink}}}
        return {
            "paper_bgcolor": self.surface,
            "plot_bgcolor": self.surface,
            "font": {"family": "system-ui, -apple-system, Segoe UI, sans-serif", "color": self.primary_ink, "size": 13},
            "margin": {"l": 8, "r": 8, "t": 8, "b": 8},
            "xaxis": axis,
            "yaxis": axis,
            "hoverlabel": {"bgcolor": self.surface, "bordercolor": self.baseline, "font": {"color": self.primary_ink}},
            "showlegend": False,
        }
