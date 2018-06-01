from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models.expressions import F

from dataloader.models import InstrumentOutputVariable, TimeSeriesResult, Result
from dataloaderinterface.models import SiteRegistration, SensorOutput, SiteSensor, SensorMeasurement


class Command(BaseCommand):
    help = ''

    @staticmethod
    def add_site_data():
        sites = SiteRegistration.objects.all()

        for site in sites:
            affiliation = site.odm2_affiliation

            site.person_id = affiliation.person_id
            site.person_first_name = affiliation.person.person_first_name
            site.person_last_name = affiliation.person.person_last_name

            if affiliation.organization:
                site.organization_id = affiliation.organization_id
                site.organization_name = affiliation.organization.organization_name
                site.organization_code = affiliation.organization.organization_code

            site.save(update_fields=[
                'person_id', 'person_first_name', 'person_last_name',
                'organization_id', 'organization_name', 'organization_code'
            ])

    @staticmethod
    def add_sensor_output_data():
        sensors = SiteSensor.objects.filter(sensor_output__isnull=True)
        output = SensorOutput.objects.all()
        result_ids = [result_id[0] for result_id in sensors.values_list('result_id')]
        results = Result.objects\
            .prefetch_related('data_logger_file_columns')\
            .filter(result_id__in=result_ids)\
            .annotate(output_variable_id=F('data_logger_file_columns__instrument_output_variable_id'))\
            .values('result_id', 'output_variable_id')

        for sensor in sensors:
            print(sensor.id)
            result = results.filter(result_id=sensor.result_id).first()
            try:
                sensor.sensor_output = output.filter(instrument_output_variable_id=result['output_variable_id']).first()
                sensor.save(update_fields=['sensor_output'])
            except TypeError:
                print('error with result %s on site %s' % (sensor.id, sensor.registration.sampling_feature_code))
                continue

    @staticmethod
    def generate_sensor_output_data():
        output_fields = [
            'instrument_output_variable_id', 'model_id', 'model_name', 'model_manufacturer','variable_id',
            'variable_name', 'variable_code', 'unit_id', 'unit_name', 'unit_abbreviation'
        ]

        instrument_output_variables = InstrumentOutputVariable.objects\
            .prefetch_related('model', 'variable', 'instrument_raw_output_unit')\
            .annotate(
                model_name=F('model__model_name'), model_manufacturer=F('model__model_manufacturer__organization_code'),
                variable_name=F('variable__variable_name'), variable_code=F('variable__variable_code'),
                unit_id=F('instrument_raw_output_unit_id'), unit_name=F('instrument_raw_output_unit__unit_name'),
                unit_abbreviation=F('instrument_raw_output_unit__unit_abbreviation'))\
            .values(*output_fields)

        sensor_output_variables = [SensorOutput(**output_data) for output_data in instrument_output_variables]
        SensorOutput.objects.bulk_create(sensor_output_variables)

    @staticmethod
    def create_last_measurements():
        sensor_measurements_data = SiteSensor.objects\
            .filter(last_measurement_id__isnull=False, last_measurement_datetime__isnull=False)\
            .values('id', 'last_measurement_datetime', 'last_measurement_utc_offset', 'last_measurement_value')

        last_measurements = [SensorMeasurement(
            sensor_id=measurement_data['id'],
            value_datetime=measurement_data['last_measurement_datetime'],
            value_datetime_utc_offset=timedelta(hours=measurement_data['last_measurement_utc_offset']),
            data_value=measurement_data['last_measurement_value']
        ) for measurement_data in sensor_measurements_data]
        SensorMeasurement.objects.bulk_create(last_measurements)

    def handle(self, *args, **options):
        self.add_site_data()
        self.generate_sensor_output_data()
        self.create_last_measurements()
        self.add_sensor_output_data()
