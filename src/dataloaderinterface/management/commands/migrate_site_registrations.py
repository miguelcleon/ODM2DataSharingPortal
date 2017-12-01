# from django.core.management.base import BaseCommand
#
# from dataloader.models import SamplingFeature
# from dataloaderinterface.models import DeviceRegistration, SiteRegistration, SiteSensor
#
#
# class Command(BaseCommand):
#     help = 'Fix corrupted or incomplete odm2 data in the scope of this application.'
#
#     @staticmethod
#     def create_site_registration(device_registration):
#         existing_site_registration = SiteRegistration.objects.filter(registration_token=device_registration.authentication_token).first()
#         if existing_site_registration:
#             return existing_site_registration
#
#         affiliation = device_registration.user.affiliation
#         sampling_feature = device_registration.sampling_feature
#
#         registration_data = {
#             'registration_token': device_registration.authentication_token,
#             'registration_date': device_registration.registration_date(),
#             'django_user': device_registration.user.user,
#             'affiliation_id': device_registration.user.affiliation_id,
#             'person': str(affiliation.person),
#             'organization': str(affiliation.organization) or '',
#             'sampling_feature_id': sampling_feature.sampling_feature_id,
#             'sampling_feature_code': sampling_feature.sampling_feature_code,
#             'sampling_feature_name': sampling_feature.sampling_feature_name,
#             'elevation_m': sampling_feature.elevation_m,
#             'latitude': sampling_feature.site.latitude,
#             'longitude': sampling_feature.site.longitude,
#             'site_type': sampling_feature.site.site_type_id
#         }
#
#         site_registration = SiteRegistration(**registration_data)
#         site_registration.save()
#         return site_registration
#
#     @staticmethod
#     def create_site_sensor(result, site_registration):
#         existing_site_sensor = SiteSensor.objects.filter(result_id=result.result_id).first()
#         if existing_site_sensor:
#             return existing_site_sensor
#
#         model = result.data_logger_file_columns.first().instrument_output_variable.model
#         values_manager = result.timeseriesresult.values
#         last_value = values_manager.latest('value_datetime') if values_manager.count() > 0 else None
#
#         sensor_data = {
#             'result_id': result.result_id,
#             'result_uuid': result.result_uuid,
#             'registration': site_registration,
#             'model_name': model.model_name,
#             'model_manufacturer':  model.model_manufacturer.organization_name,
#             'variable_name': result.variable.variable_name_id,
#             'variable_code': result.variable.variable_code,
#             'unit_name': result.unit.unit_name,
#             'unit_abbreviation': result.unit.unit_abbreviation,
#             'sampled_medium': result.sampled_medium_id,
#             'activation_date': result.valid_datetime,
#             'activation_date_utc_offset': result.valid_datetime_utc_offset,
#             'last_measurement_id': last_value and last_value.value_id
#         }
#
#         site_sensor = SiteSensor(**sensor_data)
#         site_sensor.save()
#         return site_sensor
#
#     def handle(self, *args, **options):
#         sampling_features = SamplingFeature.objects.all()
#         print("%s sites found." % sampling_features.count())
#         print("----------------------------------------------------")
#
#         for sampling_feature in sampling_features:
#             device_registration = DeviceRegistration.objects.filter(deployment_sampling_feature_uuid=sampling_feature.sampling_feature_uuid).first()
#             if not device_registration:
#                 print('**** Sampling Feature %s (%s) exists without a site registration!!!' % (sampling_feature.sampling_feature_id, sampling_feature.sampling_feature_code))
#                 continue
#
#             site_registration = self.create_site_registration(device_registration)
#             for feature_action in sampling_feature.feature_actions.all():
#                 result = feature_action.results.first()
#                 self.create_site_sensor(result, site_registration)
#             print('- site %s migrated!' % sampling_feature.sampling_feature_code)
