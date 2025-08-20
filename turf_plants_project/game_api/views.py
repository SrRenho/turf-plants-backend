from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Pixel, Player
from django.db.models import F

@api_view(['GET'])
def get_pixels(request):
    qs = Pixel.objects.all().annotate(
        owner_username=F('owner__user__username')  # follow Player -> User -> username
    ).values('x', 'y', 'owner_username', 'description', 'planted_on')

    # optionally rename key to 'owner' in the dicts
    pixels = [{**p, 'owner': p.pop('owner_username')} for p in qs]

    return Response(pixels)


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def paint_pixel(request):
    x, y = request.data.get('x'), request.data.get('y')
    if x is None or y is None:
        return Response({'error': 'x and y required'}, status=400)

    player = Player.objects.get(user=request.user)
    pixel, created = Pixel.objects.get_or_create(
        x=x,
        y=y,
        defaults={
            'owner': player,
            'description': "fui creado con post",
        }
    )

    # format like GET
    pixel_data = {
        'x': pixel.x,
        'y': pixel.y,
        'owner': pixel.owner.user.username,
        'description': pixel.description,
        'planted_on': pixel.planted_on.isoformat() if pixel.planted_on else "",
    }

    return Response(pixel_data)