from django.core.management.base import BaseCommand

from dataloaderinterface.models import SiteSensor


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):
        sensors = SiteSensor.objects.all()
        for sensor in sensors:
            time_series_result = sensor.result.timeseriesresult
            last_measurement = time_series_result.values.last()

            if not last_measurement and not sensor.last_measurement_id:
                print('- %s (%s) sensor has no measurements.' % (sensor.sensor_identity, sensor.result_id))
                continue

            elif sensor.last_measurement_id and not last_measurement:
                print('* %s (%s) sensor has a measurement and it shouldn\'t.' % (sensor.sensor_identity, sensor.result_id))
                sensor.last_measurement_id = None
                sensor.save(update_fields=['last_measurement_id'])
                continue

            elif last_measurement and not sensor.last_measurement_id:
                print('* %s (%s) sensor doesn\'t have a measurement and it should.' % (sensor.sensor_identity, sensor.result_id))
                sensor.last_measurement_id = last_measurement.value_id
                sensor.save(update_fields=['last_measurement_id'])
                continue

            elif sensor.last_measurement_id == last_measurement.value_id:
                print('- %s (%s) sensor is up to date.' % (sensor.sensor_identity, sensor.result_id))
                continue

            print('*** outdated sensor %s (%s) - got: (%s) expected: (%s)' % (
                sensor.sensor_identity,
                sensor.result_id,
                sensor.last_measurement.value_datetime,
                last_measurement.value_datetime
            ))
            sensor.last_measurement_id = last_measurement.value_id
            sensor.save(update_fields=['last_measurement_id'])
