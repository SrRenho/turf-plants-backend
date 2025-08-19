from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Pixel

@api_view(['GET'])
def get_pixels(request):
    # fetch all pixels from DB
    all_pixels = Pixel.objects.all().values_list('x', 'y')
    return Response(list(all_pixels))


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def paint_pixel(request):
    x, y = request.data.get('x'), request.data.get('y')
    if x is not None and y is not None:
        Pixel.objects.get_or_create(x=x, y=y)
    return Response({'status': 'ok'})