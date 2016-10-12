from datetime import datetime
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions

from dataloader.models import SamplingFeature, TimeSeriesResultValue, CensorCode, QualityCode, Unit, Affiliation
from dataloaderinterface.models import DeviceRegistration
from dataloaderservices.auth import UUIDAuthentication
from dataloaderservices.serializers import AffiliationSerializer, PersonSerializer, OrganizationSerializer


class AffiliationApi(APIView):
    authentication_classes = (SessionAuthentication, )

    def get(self, request, format=None):
        if 'affiliation_id' not in request.GET:
            return Response({'error': 'Affiliation Id not received.'})

        affiliation_id = request.GET['affiliation_id']
        if affiliation_id == '':
            return Response({'error': 'Empty Affiliation Id received.'})

        affiliation = Affiliation.objects.filter(pk=affiliation_id).first()
        if not affiliation:
            return Response({'error': 'Affiliation not found.'})

        return Response(AffiliationSerializer(affiliation).data)

    def post(self, request, format=None):
        person_serializer = PersonSerializer(data=request.data)
        organization_serializer = OrganizationSerializer(data=request.data)
        affiliation_serializer = AffiliationSerializer(data=request.data)

        if person_serializer.is_valid() and organization_serializer.is_valid() and affiliation_serializer.is_valid():
            person_serializer.save()
            organization_serializer.save()
            affiliation_serializer.save(
                person=person_serializer.instance,
                organization=organization_serializer.instance
            )
            return Response(affiliation_serializer.data, status=status.HTTP_201_CREATED)

        error_data = dict(person_serializer.errors, **organization_serializer.errors)
        error_data.update(affiliation_serializer.errors)

        return Response(error_data, status=status.HTTP_400_BAD_REQUEST)


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
        utc = sampling_feature.feature_action.get().action.begin_datetime_utc_offset
        date = try_parsing_date(datevalue, utc )
        for result in results:
            # Create value object and assign all correct values and stuff
            value = TimeSeriesResultValue()
            value.result_id = result.result_id
            #value.value_datetime = datetime.now()  #  get timestamp and convert it to datetime object instead of this

            value.value_datetime_utc_offset = utc
            value.value_datetime = date
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

        result.result_datetime = date
        result.feature_action.action.end_date_time = date
        result.save()

        return Response({}, status.HTTP_201_CREATED)

# from dateutil import tz
# from datetime import timedelta
def try_parsing_date(text, offset):
    for fmt in ( '%Y-%m-%d %H:%M:%S','%Y-%m-%d %H:%M', '%Y-%m-%d',):
        try:

            # utc = timedelta(hours=int(offset))
            # tzlocal = tz.tzoffset(None, utc.seconds)

            dt= datetime.strptime(text, fmt)#.replace(tzinfo=tzlocal)
            return dt
        except ValueError as v:
            print v
            pass
    raise exceptions.ParseError('no valid date format found')
