import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from pygrowthstandards.config.development import DEVELOPMENT_GOALS, DEVELOPMENT_GOALS_ORDER
from pygrowthstandards.oop.patient import Patient
from pygrowthstandards.utils.constants import MONTH
from pygrowthstandards.utils.plot import style


class DevelopmentPlotterMixin:
    patient: Patient

    def plot_development_goals(self, show: bool = False, output_path: str = "") -> tuple[Axes, Axes]:
        """
        Create development goals plot with two stacked subplots:
        - Top: months [1, ..., 15]
        - Bottom: months [13, 14, 15, 18] and years 2..6 mapped to [24,36,48,60,72]
        """
        # Columns spec per subplot
        labels_top = [str(i) for i in range(1, 16)]
        values_top = list(range(1, 16))
        labels_bottom = ["13", "14", "15", "18", "2a", "3a", "4a", "5a", "6a"]
        values_bottom = [13, 14, 15, 18, 24, 36, 48, 60, 72]

        ordered_goals = [DEVELOPMENT_GOALS[s] for s in DEVELOPMENT_GOALS_ORDER if s in DEVELOPMENT_GOALS]
        goals_top = [g for g in ordered_goals if g.max_age_months <= 15]
        goals_bottom = [g for g in ordered_goals if g.max_age_months > 15]

        n_top = len(goals_top)
        n_bottom = len(goals_bottom)
        fig_width = 16
        fig_height = max(3, int(n_top * 0.35)) + max(3, int(n_bottom * 0.35)) + 1
        fig, (ax_top, ax_bottom) = plt.subplots(
            2,
            1,
            figsize=(fig_width, fig_height),
            gridspec_kw={
                "height_ratios": [max(1, n_top), max(1, n_bottom)],
                "hspace": 0.15,
            },
        )
        style.set_style(fig, ax_top)
        style.set_style(fig, ax_bottom)
        # Disable tight_layout since we're using manual subplots_adjust
        fig.set_layout_engine("none")

        # Top subplot
        for row, goal in enumerate(goals_top):
            start = goal.min_age_months
            end = goal.max_age_months
            if end == 0:
                start = end = 1
            start = max(1, min(15, start))
            end = max(1, min(15, end))
            for m in range(start, end + 1):
                idx = values_top.index(m)
                ax_top.add_patch(Rectangle((idx, row), 1, 1, color="#ADD8E6", alpha=0.5))
        ax_top.set_xlim(0, len(values_top))
        ax_top.set_ylim(0, n_top)
        ax_top.set_xticks([i + 0.5 for i in range(len(values_top))])
        ax_top.set_xticklabels(labels_top)
        ax_top.set_yticks([i + 0.5 for i in range(n_top)])
        ax_top.set_yticklabels([g.descriptions["pt"] for g in goals_top])
        ax_top.invert_yaxis()
        ax_top.set_title("Marcos do desenvolvimento (cartão: meses 1–15)")
        ax_top.tick_params(axis="x", labelsize=8)
        ax_top.tick_params(axis="y", labelsize=9)
        ax_top.set_xticks(range(len(values_top) + 1), minor=True)
        ax_top.set_yticks(range(n_top + 1), minor=True)
        ax_top.grid(True, which="minor", axis="both", linestyle="-", linewidth=0.5, alpha=0.3)
        ax_top.grid(False, which="major")

        # Bottom subplot
        for row, goal in enumerate(goals_bottom):
            for idx, v in enumerate(values_bottom):
                if goal.min_age_months <= v <= goal.max_age_months:
                    ax_bottom.add_patch(Rectangle((idx, row), 1, 1, color="#ADD8E6", alpha=0.5))
        ax_bottom.set_xlim(0, len(values_bottom))
        ax_bottom.set_ylim(0, n_bottom)
        ax_bottom.set_xticks([i + 0.5 for i in range(len(values_bottom))])
        ax_bottom.set_xticklabels(labels_bottom)
        ax_bottom.set_yticks([i + 0.5 for i in range(n_bottom)])
        ax_bottom.set_yticklabels([g.descriptions["pt"] for g in goals_bottom])
        ax_bottom.invert_yaxis()
        ax_bottom.set_xlabel("Idade (meses/anos)")
        ax_bottom.set_ylabel("Marcos do desenvolvimento")
        ax_bottom.tick_params(axis="x", labelsize=8)
        ax_bottom.tick_params(axis="y", labelsize=9)
        ax_bottom.set_xticks(range(len(values_bottom) + 1), minor=True)
        ax_bottom.set_yticks(range(n_bottom + 1), minor=True)
        ax_bottom.grid(True, which="minor", axis="both", linestyle="-", linewidth=0.5, alpha=0.3)
        ax_bottom.grid(False, which="major")

        # Adjust margins for long PT labels and reduce unused space
        fig.subplots_adjust(left=0.28, right=0.97, top=0.96, bottom=0.08)

        if show:
            plt.show()
        if output_path:
            plt.savefig(output_path)
        return ax_top, ax_bottom

    def plot_achievements(self, show: bool = False, output_path: str = "") -> tuple[Axes, Axes]:
        """
        Overlay the child's achievements on top of the development goals subplots.
        Colors: early=#A9A9A9, on-time=#32CD32, +1m=#FFD700, delayed=#FF4500.
        """
        # Base grid with subplots
        ax_top, ax_bottom = self.plot_development_goals()

        # Rebuild the same spec and goal order to match rows/columns
        values_top = list(range(1, 16))
        values_bottom = [13, 14, 15, 18, 24, 36, 48, 60, 72]

        ordered_goals = [DEVELOPMENT_GOALS[s] for s in DEVELOPMENT_GOALS_ORDER if s in DEVELOPMENT_GOALS]
        goals_top = [g for g in ordered_goals if g.max_age_months <= 15]
        goals_bottom = [g for g in ordered_goals if g.max_age_months > 15]

        def row_for_goal_top(goal_cfg) -> int:
            return goals_top.index(goal_cfg)

        def row_for_goal_bottom(goal_cfg) -> int:
            return goals_bottom.index(goal_cfg)

        def col_for_month_top(m: float) -> int:
            m_int = max(1, min(15, int(round(m))))
            return values_top.index(m_int)

        def col_for_month_bottom(m: float) -> int:
            idx = min(range(len(values_bottom)), key=lambda i: abs(values_bottom[i] - m))
            return idx

        # Overlay child's achieved cells
        for group in self.patient.development_goals:
            for ach in group.goals:
                goal_cfg = DEVELOPMENT_GOALS.get(ach.goal)
                if not goal_cfg:
                    continue
                # child's age in months at achievement
                achievement_month = ((ach.date) - self.patient.birthday_date).days / MONTH  # type: ignore

                # Determine color vs expected window
                if achievement_month < goal_cfg.min_age_months:
                    color = "#A9A9A9"
                elif goal_cfg.min_age_months <= achievement_month <= goal_cfg.max_age_months:
                    color = "#32CD32"
                elif int(round(achievement_month)) == goal_cfg.max_age_months + 1:
                    color = "#FFD700"
                else:
                    color = "#FF4500"

                # Add patch to appropriate subplot
                if goal_cfg in goals_top:
                    col = col_for_month_top(achievement_month)
                    row = row_for_goal_top(goal_cfg)
                    ax_top.add_patch(Rectangle((col, row), 1, 1, color=color, alpha=0.8))
                else:
                    col = col_for_month_bottom(achievement_month)
                    row = row_for_goal_bottom(goal_cfg)
                    ax_bottom.add_patch(Rectangle((col, row), 1, 1, color=color, alpha=0.8))

        if show:
            plt.show()
        if output_path:
            plt.savefig(output_path)
        return ax_top, ax_bottom
