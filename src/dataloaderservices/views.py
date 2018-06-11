import codecs
import os
from datetime import timedelta, datetime

from StringIO import StringIO

import requests
from django.conf import settings
from django.forms.models import model_to_dict
from django.http.response import HttpResponse
from django.views.generic.base import View
from unicodecsv.py2 import UnicodeWriter

from dataloader.models import SamplingFeature, TimeSeriesResultValue, Unit, EquipmentModel, TimeSeriesResult, Result
from django.db.models.expressions import F
# Create your views here.
from django.utils.dateparse import parse_datetime
from rest_framework import exceptions
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from dataloaderinterface.forms import ResultForm, SiteSensorForm
from dataloaderinterface.models import SiteSensor, SiteRegistration, SensorOutput, SensorMeasurement
from dataloaderservices.auth import UUIDAuthentication
from dataloaderservices.serializers import OrganizationSerializer, SensorSerializer

from pytz import utc

from leafpack.models import LeafPack


class ResultApi(APIView):
    authentication_classes = (SessionAuthentication,)

    def post(self, request, format=None):
        form = ResultForm(data=request.POST)
        if form.is_valid():
            return Response({}, status=status.HTTP_200_OK)

        error_data = dict(form.errors)
        return Response(error_data, status=status.HTTP_206_PARTIAL_CONTENT)


class ModelVariablesApi(APIView):
    authentication_classes = (SessionAuthentication, )

    def get(self, request, format=None):
        if 'equipment_model_id' not in request.GET:
            return Response({'error': 'Equipment Model Id not received.'})

        equipment_model_id = request.GET['equipment_model_id']
        if equipment_model_id == '':
            return Response({'error': 'Empty Equipment Model Id received.'})

        equipment_model = EquipmentModel.objects.filter(pk=equipment_model_id).first()
        if not equipment_model:
            return Response({'error': 'Equipment Model not found.'})

        output = equipment_model.instrument_output_variables.values('variable', 'instrument_raw_output_unit')

        return Response(output)


class OutputVariablesApi(APIView):
    authentication_classes = (SessionAuthentication,)

    def get(self, request):
        output = SensorOutput.objects.for_filters()
        return Response(output)


class RegisterSensorApi(APIView):
    authentication_classes = (SessionAuthentication, )

    def post(self, request, format=None):
        form = SiteSensorForm(data=request.POST)

        if not form.is_valid():
            error_data = dict(form.errors)
            return Response(error_data, status=status.HTTP_206_PARTIAL_CONTENT)

        registration = form.cleaned_data['registration']
        sensor_output = form.cleaned_data['output_variable']
        site_sensor = SiteSensor.objects.create(registration=registration, sensor_output=sensor_output)
        return Response(model_to_dict(site_sensor, fields=[field.name for field in site_sensor._meta.fields]), status=status.HTTP_201_CREATED)


class EditSensorApi(APIView):
    authentication_classes = (SessionAuthentication, )

    def post(self, request, format=None):
        if 'id' not in request.POST:
            return Response({'id': 'No sensor id in the request.'}, status=status.HTTP_400_BAD_REQUEST)

        sensor = SiteSensor.objects.filter(pk=request.POST['id']).first()
        if not sensor:
            return Response({'id': 'Sensor not found.'}, status=status.HTTP_404_NOT_FOUND)

        form = SiteSensorForm(data=request.POST, instance=sensor)

        if not form.is_valid():
            error_data = dict(form.errors)
            return Response(error_data, status=status.HTTP_206_PARTIAL_CONTENT)

        sensor_output = form.cleaned_data['output_variable']
        sensor.sensor_output = sensor_output
        sensor.save(update_fields=['sensor_output'])
        return Response(model_to_dict(sensor, fields=[field.name for field in sensor._meta.fields]), status=status.HTTP_202_ACCEPTED)


class DeleteSensorApi(APIView):
    authentication_classes = (SessionAuthentication, )

    def post(self, request, format=None):
        if 'id' not in request.POST:
            return Response({'id': 'No sensor id in the request.'}, status=status.HTTP_400_BAD_REQUEST)

        sensor = SiteSensor.objects.filter(pk=request.POST['id']).first()
        if not sensor:
            return Response({'id': 'Sensor not found.'}, status=status.HTTP_404_NOT_FOUND)

        deleted = sensor.delete()
        return Response(deleted, status=status.HTTP_202_ACCEPTED)


class DeleteLeafpackApi(APIView):
    authentication_classes = (SessionAuthentication, )

    def post(self, request, format=None):
        if 'id' not in request.POST:
            return Response({'id': 'No leafpack id in the request.'}, status=status.HTTP_400_BAD_REQUEST)

        leafpack = LeafPack.objects.filter(pk=request.POST['id']).first()
        if not leafpack:
            return Response({'id': 'Leafpack not found.'}, status=status.HTTP_404_NOT_FOUND)

        deleted = leafpack.delete()
        return Response(deleted, status=status.HTTP_202_ACCEPTED)


class OrganizationApi(APIView):
    authentication_classes = (SessionAuthentication, )

    def post(self, request, format=None):
        organization_serializer = OrganizationSerializer(data=request.data)

        if organization_serializer.is_valid():
            organization_serializer.save()
            return Response(organization_serializer.data, status=status.HTTP_201_CREATED)

        error_data = dict(organization_serializer.errors)
        return Response(error_data, status=status.HTTP_206_PARTIAL_CONTENT)


class FollowSiteApi(APIView):
    authentication_classes = (SessionAuthentication,)

    def post(self, request, format=None):
        action = request.data['action']
        sampling_feature_code = request.data['sampling_feature_code']
        site = SiteRegistration.objects.get(sampling_feature_code=sampling_feature_code)

        if action == 'follow':
            request.user.followed_sites.add(site)
        elif action == 'unfollow':
            request.user.followed_sites.remove(site)

        return Response({}, status.HTTP_200_OK)


class CSVDataApi(View):
    authentication_classes = ()
    csv_headers = ('DateTime', 'TimeOffset', 'DateTimeUTC', 'Value', 'CensorCode', 'QualifierCode',)
    date_format = '%Y-%m-%d %H:%M:%S'

    def get(self, request):
        if 'result_id' not in request.GET:
            return Response({'error': 'Result Id not received.'})

        result_id = request.GET['result_id']
        if result_id == '':
            return Response({'error': 'Empty Result Id received.'})

        try:
            filename, csv_file = CSVDataApi.get_csv_file(result_id)
        except ValueError as e:
            return Response({'error': e.message})  # Time Series Result not found.

        response = HttpResponse(csv_file.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % filename
        return response

    @staticmethod
    def get_csv_file(result_id):
        time_series_result = TimeSeriesResult.objects \
            .prefetch_related('values') \
            .select_related('result__feature_action__sampling_feature', 'result__variable') \
            .filter(pk=result_id) \
            .first()

        if not time_series_result:
            raise ValueError('Time Series Result not found.')
        result = time_series_result.result

        csv_file = StringIO()
        csv_writer = UnicodeWriter(csv_file)
        csv_file.write(CSVDataApi.generate_metadata(time_series_result.result))
        csv_writer.writerow(CSVDataApi.csv_headers)
        csv_writer.writerows(CSVDataApi.get_data_values(time_series_result))

        filename = "{0}_{1}_{2}.csv".format(result.feature_action.sampling_feature.sampling_feature_code,
                                            result.variable.variable_code, result.result_id)
        return filename, csv_file

    @staticmethod
    def get_data_values(result):
        data_values = result.values.all()
        return [((data_value.value_datetime + timedelta(hours=data_value.value_datetime_utc_offset)).strftime(CSVDataApi.date_format),
                 '{0}:00'.format(data_value.value_datetime_utc_offset),
                 data_value.value_datetime.strftime(CSVDataApi.date_format),
                 data_value.data_value,
                 data_value.censor_code_id,
                 data_value.quality_code_id)
                for data_value in data_values]

    @staticmethod
    def get_metadata_template():
        with codecs.open(os.path.join(os.path.dirname(__file__), 'metadata_template.txt'), 'r', encoding='utf-8') as metadata_file:
            return metadata_file.read()



    @staticmethod
    def generate_metadata(result):
        sensor = SiteSensor.objects.select_related('registration').filter(result_id=result.result_id).first()
        if not sensor: # i dunno man, if it doesn't return anything it's messed up anyways.
            return

        action = result.feature_action.action
        equipment_model = EquipmentModel.objects.get(pk=sensor.sensor_output.model_id)
        affiliation = sensor.registration.odm2_affiliation
        return CSVDataApi.get_metadata_template().format(
            sampling_feature=sensor.registration.sampling_feature,
            variable=result.variable,
            unit=result.unit,
            model=equipment_model,
            result=result,
            action=action,
            affiliation=affiliation
        ).encode('utf-8')


class TimeSeriesValuesApi(APIView):
    authentication_classes = (UUIDAuthentication, )

    def post(self, request, format=None):
        #  make sure that the data is in the request (sampling_feature, timestamp(?), ...) if not return error response
        # if 'sampling_feature' not in request.data or 'timestamp' not in request.data:
        if not all(key in request.data for key in ('timestamp', 'sampling_feature')):
            raise exceptions.ParseError("Required data not found in request.")

        # parse the received timestamp
        try:
            measurement_datetime = parse_datetime(request.data['timestamp'])
        except ValueError:
            raise exceptions.ParseError('The timestamp value is not valid.')

        if not measurement_datetime:
            raise exceptions.ParseError('The timestamp value is not well formatted.')

        if measurement_datetime.utcoffset() is None:
            raise exceptions.ParseError('The timestamp value requires timezone information.')

        utc_offset = int(measurement_datetime.utcoffset().total_seconds() / timedelta(hours=1).total_seconds())

        # saving datetimes in utc time now.
        measurement_datetime = measurement_datetime.replace(tzinfo=None) - timedelta(hours=utc_offset)

        # get odm2 sampling feature if it matches sampling feature uuid sent
        sampling_feature = SamplingFeature.objects.filter(sampling_feature_uuid__exact=request.data['sampling_feature']).first()
        if not sampling_feature:
            raise exceptions.ParseError('Sampling Feature code does not match any existing site.')

        # get all feature actions related to the sampling feature, along with the results, results variables, and actions.
        feature_actions = sampling_feature.feature_actions.prefetch_related('results__variable', 'action').all()
        for feature_action in feature_actions:
            result = feature_action.results.all().first()
            site_sensor = SiteSensor.objects.filter(result_id=result.result_id).first()

            is_first_value = result.value_count == 0

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
                # continue adding the remaining measurements in the request.
                # TODO: use a logger to log the failed request information.
                continue
                # raise exceptions.ParseError("{variable_code} value not saved {exception_message}".format(
                #     variable_code=result.variable.variable_code, exception_message=e
                # ))

            result.value_count = F('value_count') + 1
            result.result_datetime = measurement_datetime
            result.result_datetime_utc_offset = utc_offset

            # delete last measurement
            last_measurement = SensorMeasurement.objects.filter(sensor=site_sensor).first()
            last_measurement and last_measurement.delete()

            # create new 'last' measurement
            SensorMeasurement.objects.create(
                sensor=site_sensor,
                value_datetime=result_value.value_datetime,
                value_datetime_utc_offset=timedelta(hours=result_value.value_datetime_utc_offset),
                data_value=result_value.data_value
            )

            if is_first_value:
                result.valid_datetime = measurement_datetime
                result.valid_datetime_utc_offset = utc_offset
                site_sensor.activation_date = measurement_datetime
                site_sensor.activation_date_utc_offset = utc_offset

                if not site_sensor.registration.deployment_date:
                    site_sensor.registration.deployment_date = measurement_datetime
                    site_sensor.registration.deployment_date_utc_offset = utc_offset
                    site_sensor.registration.save(update_fields=['deployment_date'])

            site_sensor.save(update_fields=[
                'activation_date', 'activation_date_utc_offset'
            ])
            result.save(update_fields=[
                'result_datetime', 'value_count', 'result_datetime_utc_offset',
                'valid_datetime', 'valid_datetime_utc_offset'
            ])

            # Insert data value into influx instance.
            influx_request_url = settings.INFLUX_UPDATE_URL
            influx_request_body = settings.INFLUX_UPDATE_BODY.format(
                result_uuid=str(site_sensor.result_uuid).replace('-', '_'),
                data_value=result_value.data_value,
                utc_offset=result_value.value_datetime_utc_offset,
                timestamp_s=long((result_value.value_datetime - datetime.utcfromtimestamp(0)).total_seconds()),
            )
            requests.post(influx_request_url, influx_request_body.encode())

        return Response({}, status.HTTP_201_CREATED)
