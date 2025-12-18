from datetime import datetime
from typing import Optional, Tuple

def parse_time_range(
    start_time_str: Optional[str],
    end_time_str: Optional[str],
) -> tuple[Optional[datetime], Optional[datetime]]:
    if not start_time_str:
        return None, None

    start_time = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
    end_time = (
        datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
        if end_time_str
        else datetime.now()
    )

    return start_time, end_time
