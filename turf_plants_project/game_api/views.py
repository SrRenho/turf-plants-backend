from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Pixel, Player
from django.db.models import F
from decouple import config
from game_api.services import serialize_pixel, create_pixel_for_player, format_owner_name


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_player(request):
    player = Player.objects.get(user=request.user)
    return Response({
        "seeds": player.seeds,
    })

@api_view(['GET'])
def get_pixels(request):
    pixels = Pixel.objects.select_related('owner__user').all()
    serialized = [serialize_pixel(p) for p in pixels]
    return Response(serialized)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def paint_pixel(request):
    x = request.data.get("x")
    y = request.data.get("y")
    description = request.data.get("description", "")

    if x is None or y is None:
        return Response({'error': 'x and y required'}, status=400)

    try:
        player = Player.objects.get(user=request.user)
    except Player.DoesNotExist:
        return Response({'error': 'Player not found'}, status=404)

    result = create_pixel_for_player(player, int(x), int(y), description)
    if "error" in result:
        return Response({"error": result["error"]}, status=400)

    return Response(serialize_pixel(result["pixel"]), status=200)



@api_view(['POST'])
@authentication_classes([])
def award_hourly_xp(request):
    raw = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION") or ""
    token = raw.replace("Bearer ", "").strip()

    if token != config('ADMIN_TOKEN'):
        return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    xp = request.data.get("xp", 1)
    try:
        xp = int(xp)
    except ValueError:
        return Response({"detail": "Invalid XP value"}, status=status.HTTP_400_BAD_REQUEST)

    updated = Pixel.objects.update(total_xp=F('total_xp') + xp)
    return Response({"success": True, "updated_pixels": updated})

