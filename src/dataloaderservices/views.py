from datetime import datetime, timedelta

from django.db.models.expressions import F
from django.shortcuts import render

# Create your views here.
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions

from dataloader.models import SamplingFeature, TimeSeriesResultValue, CensorCode, QualityCode, Unit, Affiliation, \
    EquipmentModel
from dataloaderinterface.forms import ResultForm, ResultFormSet
from dataloaderinterface.models import DeviceRegistration
from dataloaderservices.auth import UUIDAuthentication
from dataloaderservices.serializers import AffiliationSerializer, PersonSerializer, OrganizationSerializer, \
    EquipmentModelSerializer


class ResultApi(APIView):
    authentication_classes = (SessionAuthentication,)

    allowed_methods = ('POST',)

    def post(self, request, format=None):
        # request.POST can possibly be empty
        # always use request.data for all http methods
        form = ResultForm(data=request.data)
        if form.is_valid():
            return Response({}, status=status.HTTP_200_OK)

        error_data = dict(form.errors)
        return Response(error_data, status=status.HTTP_206_PARTIAL_CONTENT)


class ModelVariablesApi(APIView):
    authentication_classes = (SessionAuthentication, )

    allowed_methods = ('GET',)

    def get(self, request, format=None):
        if 'equipment_model_id' not in request.data:
            return Response({'error': 'Equipment Model Id not received.'}, status=status.HTTP_400_BAD_REQEST)

        equipment_model_id = request.data['equipment_model_id']
        if equipment_model_id == '':
            return Response({'error': 'Empty Equipment Model Id received.'}, status=status.HTTP_400_BAD_REQEST)

        equipment_model = EquipmentModel.objects.filter(pk=equipment_model_id).first()
        if not equipment_model:
            return Response({'error': 'Equipment Model not found.'}, status=status.HTTP_400_BAD_REQEST)

        output = equipment_model.instrument_output_variables.values('variable', 'instrument_raw_output_unit')

        return Response(output)


class OrganizationApi(APIView):
    authentication_classes = (SessionAuthentication, )

    allowed_methods = ('POST',)

    def post(self, request, format=None):
        organization_serializer = OrganizationSerializer(data=request.data)

        if organization_serializer.is_valid():
            organization_serializer.save()
            return Response(organization_serializer.data, status=status.HTTP_201_CREATED)

        error_data = dict(organization_serializer.errors)
        return Response(error_data, status=status.HTTP_206_PARTIAL_CONTENT)


class ResultValuesApi(APIView):
    authentication_classes = (SessionAuthentication,)

    allowed_methods = ('GET',)

    def get(self, request, format=None):
        if 'result_ids' not in request.data:
            return Response({'error': 'No result id received.'}, status=status.HTTP_400_BAD_REQEST)

        results = request.data.getlist('result_ids')
        values = TimeSeriesResultValue.objects.filter(result_id__in=results)

        output = values.instrument_output_variables.values('variable', 'instrument_raw_output_unit')

        return Response(output)


class TimeSeriesValuesApi(APIView):
    authentication_classes = (UUIDAuthentication, )

    allowed_methods = ('POST',)

    def post(self, request, format=None):
        #  make sure that the data is in the request (sampling_feature, timestamp(?), ...) if not return error response
        # if 'sampling_feature' not in request.data or 'timestamp' not in request.data:
        if not all(key in request.data for key in ('timestamp', 'sampling_feature')):
            return Response({'error': 'Required data not found in request.'}, status=status.HTTP_400_BAD_REQEST)

        # parse the received timestamp
        try:
            measurement_datetime = parse_datetime(request.data['timestamp'])
        except ValueError:
            return Response({'error': 'The timestamp value is not valid.'}, status=status.HTTP_400_BAD_REQEST)

        if not measurement_datetime:
            return Response({'error': 'The timestamp value is not well formatted.'}, status=status.HTTP_400_BAD_REQEST)

        if not measurement_datetime.utcoffset():
            return Response({'error': 'The timestamp value requires timezone information.'},
                            status=status.HTTP_400_BAD_REQEST)

        utc_offset = int(measurement_datetime.utcoffset().total_seconds() / timedelta(hours=1).total_seconds())

        # get odm2 sampling feature if it matches sampling feature uuid sent
        sampling_feature = SamplingFeature.objects.filter(sampling_feature_uuid__exact=
                                                          request.data['sampling_feature']).first()
        if not sampling_feature:
            return Response({'error': 'Sampling Feature code does not match any existing site.'},
                            status=status.HTTP_400_BAD_REQEST)

        # get all feature actions related to the sampling feature, along with the results, results variables,
        # and actions.
        feature_actions = sampling_feature.feature_actions.prefetch_related('results__variable', 'action').all()
        for feature_action in feature_actions:
            result = feature_action.results.all().first()

            # don't create a new TimeSeriesValue for results that are not included in the request
            if str(result.result_uuid) not in request.data:
                continue

            result_value = TimeSeriesResultValue(
                result_id=result.result_id,
                value_datetime_utc_offset=utc_offset,
                value_datetime=measurement_datetime,
                censor_code_id='Not censored',
                quality_code_id='None',
                time_aggregation_interval=1,
                time_aggregation_interval_unit=Unit.objects.get(unit_name='hour minute'),
                data_value=request.data[str(result.result_uuid)]
            )

            try:
                result_value.save()
            except Exception as e:
                err_msg = "{variable_code} value not saved {exception_message}"
                err_msg = err_msg.format(variable_code=result.variable.variable_code, exception_message=e)
                return Response({'error': err_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            result.value_count = F('value_count') + 1
            result.result_datetime = measurement_datetime
            result.result_datetime_utc_offset = utc_offset
            result.save(update_fields=['result_datetime', 'value_count', 'result_datetime_utc_offset'])

        return Response({}, status.HTTP_201_CREATED)


def try_parsing_date(text):
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    raise exceptions.ParseError('no valid date format found')
