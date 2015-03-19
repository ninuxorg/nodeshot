from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Metric


@api_view(('GET', 'POST'))
def metric_details(request, pk, format=None):
    """
    Get or write metric values
    """
    metric = get_object_or_404(Metric, pk=pk)
    # get
    if request.method == 'GET':
        results = metric.select()
        return Response(results)
    # post
    else:
        if not request.DATA:
            return Response({'detail': 'expected values in POST data or JSON payload'},
                            status=400)
        metric.write(request.DATA)
        return Response({'detail': 'ok'})
