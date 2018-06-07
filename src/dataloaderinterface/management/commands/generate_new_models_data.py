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
        print('-Filling out new site data fields for all %s sites.' % sites.count())
        for site in sites:
            print('--%s' % site.sampling_feature_code)
            affiliation = site.odm2_affiliation
            SiteRegistration.objects.filter(registration_id=site.registration_id).update(
                person_id=affiliation.person_id,
                person_first_name=affiliation.person.person_first_name,
                person_last_name=affiliation.person.person_last_name,
                organization_id=affiliation.organization and affiliation.organization_id,
                organization_name=affiliation.organization and affiliation.organization.organization_name,
                organization_code=affiliation.organization and affiliation.organization.organization_code
            )
        print('-Done with the site registrations!')

    @staticmethod
    def add_sensor_output_data():
        print('-Linking new sensor output variables with sensors')
        sensors = SiteSensor.objects.filter(sensor_output__isnull=True)
        print('--%s sensors retrieved.' % sensors.count())

        output = SensorOutput.objects.all()
        result_ids = [result_id[0] for result_id in sensors.values_list('result_id')]

        print('-Getting result objects with their related data logger file columns')
        results = Result.objects\
            .prefetch_related('data_logger_file_columns')\
            .filter(result_id__in=result_ids)\
            .annotate(output_variable_id=F('data_logger_file_columns__instrument_output_variable_id'))\
            .values('result_id', 'output_variable_id')

        print('-Results retrieved! linking their sensors now.')
        for sensor in sensors:
            result = results.filter(result_id=sensor.result_id).first()
            try:
                output_variable = output.filter(instrument_output_variable_id=result['output_variable_id']).first()
                print('--Linking sensor %s with output variable %s' % (sensor.sensor_identity, output_variable))
                SiteSensor.objects.filter(id=sensor.id).update(sensor_output=output_variable)
                print('---saved!')
            except TypeError:
                print('error with result %s on site %s' % (sensor.id, sensor.registration.sampling_feature_code))
                continue
        print('All sensors updated!')

    @staticmethod
    def generate_sensor_output_data():
        print('-Generating sensor output data from %s instrument output variables' % (InstrumentOutputVariable.objects.count()))
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
        print('-Saving sensor output objects')
        SensorOutput.objects.bulk_create(sensor_output_variables)
        print('-Saved!')

    @staticmethod
    def create_last_measurements():
        print('-Getting Sensors\' last measurements')
        sensor_measurements_data = SiteSensor.objects\
            .filter(last_measurement_id__isnull=False, last_measurement_datetime__isnull=False)\
            .values('id', 'last_measurement_datetime', 'last_measurement_utc_datetime', 'last_measurement_utc_offset', 'last_measurement_value')

        last_measurements = [SensorMeasurement(
            sensor_id=measurement_data['id'],
            value_datetime=measurement_data['last_measurement_utc_datetime'],
            value_datetime_utc_offset=timedelta(hours=measurement_data['last_measurement_utc_offset']),
            data_value=measurement_data['last_measurement_value']
        ) for measurement_data in sensor_measurements_data]

        print('-Creating %s measurement objects' % len(last_measurements))
        SensorMeasurement.objects.bulk_create(last_measurements)
        print('Measurement data added!')

    def handle(self, *args, **options):
        # self.add_site_data()
        # self.generate_sensor_output_data()
        self.create_last_measurements()
        # self.add_sensor_output_data()
        print('That\'s all folks!')
