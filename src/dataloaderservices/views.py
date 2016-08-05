from datetime import datetime
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions

from dataloader.models import SamplingFeature, TimeSeriesResultValue, CensorCode, QualityCode, Unit
from dataloaderinterface.models import DeviceRegistration
from dataloaderservices.auth import UUIDAuthentication


class TimeSeriesValuesApi(APIView):
    authentication_classes = (UUIDAuthentication, )

    def post(self, request, format=None):
        #  make sure that the data is in the request (sampling_feature, timestamp(?), ...) if not return error response
        try:
            uuid = request.data[u'sampling_feature']
            datevalue = request.data[u'timestamp']
        except Exception as e:
            raise exceptions.ParseError("missing data from request: {}".format(e))

        sampling_feature_queryset = SamplingFeature.objects.filter(sampling_feature_uuid__exact=uuid)
        if not sampling_feature_queryset.exists():
            #  return error response
            raise exceptions.ParseError('Sampling Feature does not exist')
            return

        sampling_feature = sampling_feature_queryset.get()
        results = sampling_feature.feature_action.get().result_set.all()
        for result in results:
            # Create value object and assign all correct values and stuff
            value = TimeSeriesResultValue()
            value.result_id = result.result_id
            #value.value_datetime = datetime.now()  #  get timestamp and convert it to datetime object instead of this
            value.value_datetime = try_parsing_date(datevalue)
            value.value_datetime_utc_offset = sampling_feature.feature_action.get().action.begin_datetime_utc_offset
            value.censor_code = CensorCode.objects.get(name='Not censored')
            value.quality_code = QualityCode.objects.get(name='None')
            value.time_aggregation_interval_unit = Unit.objects.get(unit_name='hour minute')
            value.time_aggregation_interval = 1

            result_variable_code = result.variable.variable_code
            if result_variable_code in request.data:
                value.data_value = request.data[result_variable_code]
            #  update result datetime and action datetime.
            try:
                value.save()  # TODO: if there's error saving, return error response.
            except Exception as e:
                raise exceptions.ParseError("{c} value not saved {e}".format(c=result_variable_code, e=e))

        result.result_datetime = value.value_datetime
        result.feature_action.action.end_date_time = value.value_datetime
        result.save()

        return Response({}, status.HTTP_201_CREATED)

def try_parsing_date(text):
    for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S','%Y-%m-%d %H:%M'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise exceptions.ParseError('no valid date format found')
