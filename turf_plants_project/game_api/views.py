from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Pixel, Player
from django.db.models import F
from decouple import config
from game_api.level_system import xp_progress

@api_view(['GET'])
def get_pixels(request):
    qs = Pixel.objects.all().annotate(
        owner_username=F('owner__user__username')  # follow Player -> User -> username
    ).values('x', 'y', 'owner_username', 'description', 'planted_on', 'total_xp')

    # optionally rename key to 'owner' in the dicts
    pixels = []
    for p in qs:
        level, xp_into, xp_until = xp_progress(float(p.get('total_xp', 0) or 0))
        # convert planted_on if needed
        planted_on = p.get('planted_on')
        planted_on_iso = planted_on.isoformat() if planted_on else ""
        d = {
            'x': p['x'],
            'y': p['y'],
            'owner': p.pop('owner_username'),
            'description': p['description'],
            'planted_on': planted_on_iso,
            'total_xp': p['total_xp'],
            'level': level,
            'xp_into_level': xp_into,
            'xp_until_next': xp_until,
        }
        pixels.append(d)

    return Response(pixels)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def paint_pixel(request):
    x, y = request.data.get('x'), request.data.get('y')
    description = request.data.get('description')
    if x is None or y is None:
        return Response({'error': 'x and y required'}, status=400)

    player = Player.objects.get(user=request.user)
    pixel, created = Pixel.objects.get_or_create(
        x=x,
        y=y,
        defaults={
            'owner': player,
            'description': description,
        }
    )

    level, xp_into_level, xp_until_next = xp_progress(pixel.total_xp)

    # format like GET
    pixel_data = {
        'x': pixel.x,
        'y': pixel.y,
        'owner': pixel.owner.user.username,
        'description': pixel.description,
        'planted_on': pixel.planted_on.isoformat() if pixel.planted_on else "",
        'total_xp': pixel.total_xp,
        'level': level,
        'xp_into_level': xp_into_level,
        'xp_until_next': xp_until_next,
    }

    return Response(pixel_data)



@api_view(['POST'])
@authentication_classes([])
def award_hourly_xp(request):
    raw = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION") or ""
    token = raw.replace("Bearer ", "").strip()

    if token == config('ADMIN_TOKEN'):
        updated = Pixel.objects.update(total_xp=F('total_xp') + 10)
        return Response({"success": True, "updated_pixels": updated})

    return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

