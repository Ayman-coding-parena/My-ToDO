"""Terminal pie chart that reflects live task completion stats."""

from math import pi


def _point_in_slice(angle: float, start: float, end: float) -> bool:
    if start <= end:
        return start <= angle < end
    return angle >= start or angle < end


def render_pie_chart(completed: int, total: int, size: int = 11) -> str:
    """Draw an ASCII pie chart. Updates whenever stats change."""
    if total == 0:
        return "\n  (no tasks yet — add one to see progress)\n"

    ratio = completed / total
    if ratio >= 1.0:
        ratio = 1.0
    elif ratio <= 0.0:
        ratio = 0.0

    completed_angle = ratio * 2 * pi
    radius = size // 2
    center = radius

    filled = "#"
    empty = "."

    lines: list[str] = []
    for y in range(size):
        row = "  "
        for x in range(size):
            dx = x - center + 0.5
            dy = center - y - 0.5
            dist_sq = dx * dx + dy * dy
            if dist_sq > radius * radius:
                row += " "
                continue
            if ratio >= 1.0:
                row += filled
                continue
            if ratio <= 0.0:
                row += empty
                continue
            angle = (pi - atan2_safe(dy, dx)) % (2 * pi)
            in_completed = _point_in_slice(angle, 0, completed_angle)
            row += filled if in_completed else empty
        lines.append(row)

    pct = ratio * 100
    header = f"  Progress: {completed}/{total} completed ({pct:.0f}%)"
    legend = f"  {filled} done   {empty} remaining"
    return "\n".join([header, ""] + lines + ["", legend])


def atan2_safe(y: float, x: float) -> float:
    from math import atan2

    return atan2(y, x)


def render_progress_summary(completed: int, total: int) -> str:
    if total == 0:
        return "Progress: 0/0 (add tasks to track completion)"
    pct = completed / total * 100
    bar_width = 20
    filled = int(bar_width * completed / total)
    bar = "#" * filled + "." * (bar_width - filled)
    return f"Progress: [{bar}] {completed}/{total} ({pct:.0f}%)"
