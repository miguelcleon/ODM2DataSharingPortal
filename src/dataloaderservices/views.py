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
        # TODO: make sure that the data is in the request (sampling_feature, timestamp(?), ...) if not return error response
        uuid = request.data[u'sampling_feature']

        sampling_feature_queryset = SamplingFeature.objects.filter(sampling_feature_uuid__exact=uuid)
        if not sampling_feature_queryset.exists():
            # TODO: return error response
            raise exceptions.AuthenticationFailed('')
            return

        sampling_feature = sampling_feature_queryset.get()
        results = sampling_feature.feature_action.get().result_set.all()
        for result in results:
            # Create value object and assign all correct values and stuff
            value = TimeSeriesResultValue()
            value.result_id = result.result_id
            #value.value_datetime = datetime.now()  # TODO: get timestamp and convert it to datetime object instead of this
            value.value_datetime = self.try_parsing_data(request.data[u'timestamp'])
            value.value_datetime_utc_offset = sampling_feature.feature_action.get().action.begin_datetime_utc_offset
            value.censor_code = CensorCode.objects.get(name='Not censored')
            value.quality_code = QualityCode.objects.get(name='None')
            value.time_aggregation_interval_unit = Unit.objects.get(unit_name='hour minute')
            value.time_aggregation_interval = 1

            result_variable_code = result.variable.variable_code
            if result_variable_code in request.data:
                value.data_value = request.data[result_variable_code]
            # TODO: update result datetime and action datetime.
            value.save()  # TODO: if there's error saving, return error response.

        return Response({}, status.HTTP_201_CREATED)

    def try_parsing_date(text):
        for fmt in ('%Y-%m-%d', '%Y-%m-%d hh:mm:ss', '%d/%m/%y'):
            try:
                return datetime.strptime(text, fmt)
            except ValueError:
                pass
        raise ValueError('no valid date format found')
