import json
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.response import Response

from influxdb.client import InfluxDBClientError

from .models import Metric


@api_view(('GET', 'POST'))
def metric_details(request, pk, format=None):
    """
    Get or write metric values
    """
    metric = get_object_or_404(Metric, pk=pk)
    # get
    if request.method == 'GET':
        try:
            results = metric.select(q=request.QUERY_PARAMS.get('q', metric.query))
        except InfluxDBClientError as e:
            return Response(json.loads(e.content), status=e.code)
        return Response(results)
    # post
    else:
        if not request.DATA:
            return Response({'detail': 'expected values in POST data or JSON payload'},
                            status=400)
        data = request.DATA.copy()
        # try converting strings to floats when sending form-data
        if request.content_type != 'application/json':
            for key, value in data.items():
                try:
                    data[key] = float(value) if '.' in value else int(value)
                except ValueError:
                    pass
        # write
        metric.write(data)
        return Response({'detail': 'ok'})
