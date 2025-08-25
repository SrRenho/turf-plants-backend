from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Pixel, Player
from django.db.models import F

@api_view(['GET'])
def get_pixels(request):
    qs = Pixel.objects.all().annotate(
        owner_username=F('owner__user__username')  # follow Player -> User -> username
    ).values('x', 'y', 'owner_username', 'description', 'planted_on', 'total_xp')

    # optionally rename key to 'owner' in the dicts
    pixels = [{**p, 'owner': p.pop('owner_username')} for p in qs]

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

    # format like GET
    pixel_data = {
        'x': pixel.x,
        'y': pixel.y,
        'owner': pixel.owner.user.username,
        'description': pixel.description,
        'planted_on': pixel.planted_on.isoformat() if pixel.planted_on else "",
        'total_xp': pixel.total_xp,
    }

    return Response(pixel_data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def award_hourly_xp(request):
    updated = Pixel.objects.update(total_xp=F('total_xp') + 1)
    return Response({"success": True, "updated_pixels": updated})