from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Pixel, Player

@api_view(['GET'])
def get_pixels(request):
    # fetch all pixels from DB with all relevant fields
    all_pixels = Pixel.objects.all().values(
        'x',
        'y',
        'owner__user__username',
        'description',
        'planted_on'
    )
    return Response(list(all_pixels))


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def paint_pixel(request):
    x, y = request.data.get('x'), request.data.get('y')
    if x is not None and y is not None:
        player = Player.objects.get(user=request.user)
        Pixel.objects.get_or_create(
            x=x,
            y=y,
            defaults={'owner': player}
        )
    return Response({'status': 'ok'})