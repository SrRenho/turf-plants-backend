from django.db import transaction
from typing import Dict, Any
from game_api.models import Pixel, Player
from game_api.level_system import xp_progress  # wherever your xp_progress lives


def format_owner_name(player: Player) -> str:
    """Return a display name for a Player (first+last or username)."""
    user = player.user
    first = (user.first_name or "").strip()
    last = (user.last_name or "").strip()
    full = f"{first} {last}".strip()
    return full or user.username


def serialize_pixel(pixel: Pixel) -> Dict[str, Any]:
    """Turn a Pixel model into the dict payload your frontend expects."""
    level, xp_into_level, xp_until_next = xp_progress(float(pixel.total_xp or 0))
    return {
        "x": pixel.x,
        "y": pixel.y,
        "owner": format_owner_name(pixel.owner),
        "description": pixel.description,
        "planted_on": pixel.planted_on.isoformat() if pixel.planted_on else "",
        "total_xp": pixel.total_xp,
        "level": level,
        "xp_into_level": xp_into_level,
        "xp_until_next": xp_until_next,
    }


def create_pixel_for_player(player, x, y, description):
    """
    Attempt to create a new pixel for a player.
    Returns either {"error": msg} or {"pixel": Pixel}.
    Rejects if pixel already exists or player has no seeds.
    """
    if player.seeds < 1:
        return {"error": "Not enough seeds"}

    with transaction.atomic():
        if Pixel.objects.filter(x=x, y=y).exists():
            return {"error": "Pixel already exists"}

        pixel = Pixel.objects.create(x=x, y=y, owner=player, description=description)
        player.seeds -= 1
        player.save(update_fields=["seeds"])
        return {"pixel": pixel}
