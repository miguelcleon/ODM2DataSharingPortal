from django.core.management.base import BaseCommand

from dataloader.models import DataLoggerFileColumn, DataLoggerProgramFile, DataLoggerFile, InstrumentOutputVariable, \
    EquipmentModel
from dataloaderinterface.models import SiteRegistration, SiteSensor


class Command(BaseCommand):
    help = ''

    @staticmethod
    def delete_datalogger_data():
        print('%s program files found vs %s registrations' % (DataLoggerProgramFile.objects.count(), SiteRegistration.objects.count()))
        print('%s datalogger files found' % DataLoggerFile.objects.count())
        print('%s datalogger file columns found vs %s sensors registered' % (DataLoggerFileColumn.objects.count(), SiteSensor.objects.count()))
        DataLoggerProgramFile.objects.all().delete()
        DataLoggerFileColumn.objects.all().delete()
        DataLoggerFile.objects.all().delete()

    def handle(self, *args, **options):
        self.delete_datalogger_data()

        registrations = SiteRegistration.objects.prefetch_related('sensors').all()
        for registration in registrations:
            data_logger_program = DataLoggerProgramFile.objects.create(
                affiliation_id=registration.affiliation_id,
                program_name='%s' % registration.sampling_feature_code
            )

            data_logger_file = DataLoggerFile.objects.create(
                program=data_logger_program,
                data_logger_file_name='%s' % registration.sampling_feature_code
            )

            print('--- Program and file created for site %s' % registration.sampling_feature_code)

            sensors = registration.sensors.all()
            for sensor in sensors:
                instrument_output_variable = InstrumentOutputVariable.objects.filter(
                    model__model_name=sensor.model_name,
                    variable__variable_code=sensor.variable_code,
                    instrument_raw_output_unit__unit_name=sensor.unit_name,
                ).first()
                if not instrument_output_variable:
                    print('***** instrument output variable not found for result %s' % sensor.result_id)

                DataLoggerFileColumn.objects.create(
                    result=sensor.result,
                    data_logger_file=data_logger_file,
                    instrument_output_variable=instrument_output_variable,
                    column_label='%s(%s)' % (sensor.variable_code, sensor.unit_abbreviation)
                )
                print('---- Datalogger file column created for %s' % sensor.sensor_identity)
