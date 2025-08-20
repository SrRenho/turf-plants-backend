from django_channels_jwt.shortcuts import create_token

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_ws_token(request):
    uuid = create_token(request.user)  # binds user to a UUID in cache
    return Response({"ws_uuid": str(uuid)})