BEGIN;
--
-- Create model HydroShareAccount
--
CREATE TABLE "hydroshare_account" ("id" serial NOT NULL PRIMARY KEY, "name" varchar(255) NOT NULL, "is_enabled" boolean NOT NULL, "ext_hydroshare_id" integer NOT NULL UNIQUE);
--
-- Create model HydroShareSiteSetting
--
CREATE TABLE "hydroshare_site_setting" ("id" serial NOT NULL PRIMARY KEY, "sync_type" varchar(255) NOT NULL, "resource_id" varchar(255) NOT NULL, "update_freq" interval NOT NULL, "is_enabled" boolean NOT NULL, "last_sync_date" timestamp with time zone NULL, "hs_account_id" integer NULL);
--
-- Create model HydroShareSyncLog
--
CREATE TABLE "hydroshare_sync_log" ("id" serial NOT NULL PRIMARY KEY, "sync_date" timestamp with time zone NOT NULL, "sync_type" varchar(255) NOT NULL, "site_sharing_id" integer NOT NULL);
--
-- Create model OAuthToken
--
CREATE TABLE "oauth_token" ("id" serial NOT NULL PRIMARY KEY, "access_token" varchar(255) NOT NULL, "refresh_token" varchar(255) NOT NULL, "token_type" varchar(6) NOT NULL, "expires_in" timestamp with time zone NOT NULL, "scope" varchar(255) NOT NULL, "account_id" integer NOT NULL);
--
-- Create model ODM2User
--
CREATE TABLE "dataloaderinterface_odm2user" ("id" serial NOT NULL PRIMARY KEY, "affiliation_id" integer NOT NULL, "user_id" integer NOT NULL UNIQUE);
--
-- Create model SiteAlert
--
CREATE TABLE "dataloaderinterface_sitealert" ("id" serial NOT NULL PRIMARY KEY, "LastAlerted" timestamp with time zone NULL, "HoursThreshold" integer NOT NULL CHECK ("HoursThreshold" >= 0));
--
-- Create model SiteRegistration
--
CREATE TABLE "dataloaderinterface_siteregistration" ("RegistrationID" serial NOT NULL PRIMARY KEY, "RegistrationToken" varchar(64) NOT NULL UNIQUE, "RegistrationDate" timestamp with time zone NOT NULL, "DeploymentDate" timestamp with time zone NULL, "AffiliationID" integer NOT NULL, "Person" varchar(765) NOT NULL, "Organization" varchar(255) NULL, "SamplingFeatureID" integer NOT NULL, "SamplingFeatureCode" varchar(50) NOT NULL UNIQUE, "SamplingFeatureName" varchar(255) NOT NULL, "Elevation" double precision NULL, "Latitude" double precision NOT NULL, "Longitude" double precision NOT NULL, "SiteType" varchar(765) NOT NULL, "User" integer NOT NULL);
CREATE TABLE "dataloaderinterface_siteregistration_followed_by" ("id" serial NOT NULL PRIMARY KEY, "siteregistration_id" integer NOT NULL, "user_id" integer NOT NULL);
--
-- Create model SiteSensor
--
CREATE TABLE "dataloaderinterface_sitesensor" ("id" serial NOT NULL PRIMARY KEY, "ResultID" integer NOT NULL UNIQUE, "ResultUUID" uuid NOT NULL UNIQUE, "ModelName" varchar(255) NOT NULL, "ModelManufacturer" varchar(255) NOT NULL, "VariableName" varchar(255) NOT NULL, "VariableCode" varchar(50) NOT NULL, "UnitsName" varchar(255) NOT NULL, "UnitAbbreviation" varchar(255) NOT NULL, "SampledMedium" varchar(255) NOT NULL, "LastMeasurementID" integer NULL UNIQUE, "LastMeasurementValue" double precision NULL, "LastMeasurementDatetime" timestamp with time zone NULL, "LastMeasurementUtcOffset" integer NULL, "LastMeasurementUtcDatetime" timestamp with time zone NULL, "ActivationDate" timestamp with time zone NULL, "ActivationDateUtcOffset" integer NULL, "RegistrationID" integer NOT NULL);
--
-- Add field site_registration to sitealert
--
ALTER TABLE "dataloaderinterface_sitealert" ADD COLUMN "RegistrationID" integer NOT NULL;
ALTER TABLE "dataloaderinterface_sitealert" ALTER COLUMN "RegistrationID" DROP DEFAULT;
--
-- Add field user to sitealert
--
ALTER TABLE "dataloaderinterface_sitealert" ADD COLUMN "User" integer NOT NULL;
ALTER TABLE "dataloaderinterface_sitealert" ALTER COLUMN "User" DROP DEFAULT;
--
-- Add field site_registration to hydrosharesitesetting
--
ALTER TABLE "hydroshare_site_setting" ADD COLUMN "site_registration_id" integer NOT NULL UNIQUE;
ALTER TABLE "hydroshare_site_setting" ALTER COLUMN "site_registration_id" DROP DEFAULT;
--
-- Add field user to hydroshareaccount
--
ALTER TABLE "dataloaderinterface_siteregistration" ADD COLUMN "DeploymentDate" timestamp with time zone NULL;
ALTER TABLE "hydroshare_account" ADD COLUMN "user_id" integer NOT NULL;
ALTER TABLE "hydroshare_account" ALTER COLUMN "user_id" DROP DEFAULT;
ALTER TABLE "hydroshare_site_setting" ADD CONSTRAINT "hydroshare_site_hs_account_id_0aead4e0_fk_hydroshare_account_id" FOREIGN KEY ("hs_account_id") REFERENCES "hydroshare_account" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "hydroshare_site_setting_e1cbf01f" ON "hydroshare_site_setting" ("hs_account_id");
ALTER TABLE "hydroshare_sync_log" ADD CONSTRAINT "hydrosha_site_sharing_id_af410ff7_fk_hydroshare_site_setting_id" FOREIGN KEY ("site_sharing_id") REFERENCES "hydroshare_site_setting" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "hydroshare_sync_log_96c12680" ON "hydroshare_sync_log" ("site_sharing_id");
ALTER TABLE "oauth_token" ADD CONSTRAINT "oauth_token_account_id_9ec62be2_fk_hydroshare_account_id" FOREIGN KEY ("account_id") REFERENCES "hydroshare_account" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "oauth_token_8a089c2a" ON "oauth_token" ("account_id");
ALTER TABLE "dataloaderinterface_odm2user" ADD CONSTRAINT "dataloaderinterface_odm2user_user_id_c7f612f0_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "dataloaderinterface_siteregistration" ADD CONSTRAINT "dataloaderinterface_siteregistrat_User_ddc425ba_fk_auth_user_id" FOREIGN KEY ("User") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "dataloaderinterface_siteregistration_8f9bfe9d" ON "dataloaderinterface_siteregistration" ("User");
CREATE INDEX "dataloaderinterface_siteregistr_RegistrationToken_5bd5fe0a_like" ON "dataloaderinterface_siteregistration" ("RegistrationToken" varchar_pattern_ops);
CREATE INDEX "dataloaderinterface_siteregis_SamplingFeatureCode_ff4f3f4d_like" ON "dataloaderinterface_siteregistration" ("SamplingFeatureCode" varchar_pattern_ops);
ALTER TABLE "dataloaderinterface_siteregistration_followed_by" ADD CONSTRAINT "D14b290714bb90087aea85ea12abf527" FOREIGN KEY ("siteregistration_id") REFERENCES "dataloaderinterface_siteregistration" ("RegistrationID") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "dataloaderinterface_siteregistration_followed_by" ADD CONSTRAINT "dataloaderinterface_siteregist_user_id_d95fd769_fk_auth_user_id" FOREIGN KEY ("user_id") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "dataloaderinterface_siteregistration_followed_by" ADD CONSTRAINT "dataloaderinterface_siteregis_siteregistration_id_ff0c0787_uniq" UNIQUE ("siteregistration_id", "user_id");
CREATE INDEX "dataloaderinterface_siteregistration_followed_by_37ede4dc" ON "dataloaderinterface_siteregistration_followed_by" ("siteregistration_id");
CREATE INDEX "dataloaderinterface_siteregistration_followed_by_e8701ad4" ON "dataloaderinterface_siteregistration_followed_by" ("user_id");
ALTER TABLE "dataloaderinterface_sitesensor" ADD CONSTRAINT "D0a8daa02bd6a7cd173e6e91f6229a3b" FOREIGN KEY ("RegistrationID") REFERENCES "dataloaderinterface_siteregistration" ("RegistrationID") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "dataloaderinterface_sitesensor_58043df5" ON "dataloaderinterface_sitesensor" ("RegistrationID");
CREATE INDEX "dataloaderinterface_sitealert_58043df5" ON "dataloaderinterface_sitealert" ("RegistrationID");
ALTER TABLE "dataloaderinterface_sitealert" ADD CONSTRAINT "D83a3e7dcfa6565ec1561ef2bd409ed7" FOREIGN KEY ("RegistrationID") REFERENCES "dataloaderinterface_siteregistration" ("RegistrationID") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "dataloaderinterface_sitealert_8f9bfe9d" ON "dataloaderinterface_sitealert" ("User");
ALTER TABLE "dataloaderinterface_sitealert" ADD CONSTRAINT "dataloaderinterface_sitealert_User_0ee890d1_fk_auth_user_id" FOREIGN KEY ("User") REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "hydroshare_site_setting" ADD CONSTRAINT "D6c9323ae832badb58171adc906e94f1" FOREIGN KEY ("site_registration_id") REFERENCES "dataloaderinterface_siteregistration" ("RegistrationID") DEFERRABLE INITIALLY DEFERRED;
CREATE INDEX "hydroshare_account_e8701ad4" ON "hydroshare_account" ("user_id");
ALTER TABLE "hydroshare_account" ADD CONSTRAINT "hydroshare__user_id_96d6788d_fk_dataloaderinterface_odm2user_id" FOREIGN KEY ("user_id") REFERENCES "dataloaderinterface_odm2user" ("id") DEFERRABLE INITIALLY DEFERRED;
COMMIT;

-- ALTER TABLE dataloaderinterface_sitesensor add column "ResultUUID" uuid NOT NULL;
-- ALTER TABLE dataloaderinterface_sitesensor add column "ModelName" character varying(255) NOT NULL;
-- ALTER TABLE dataloaderinterface_sitesensor add column "ModelManufacturer" character varying(255) NOT NULL;
-- ALTER TABLE dataloaderinterface_sitesensor add column "VariableName" character varying(255) NOT NULL;
-- ALTER TABLE dataloaderinterface_sitesensor add column "VariableCode" character varying(50) NOT NULL;
-- ALTER TABLE dataloaderinterface_sitesensor add column "UnitsName" character varying(255) NOT NULL;
-- ALTER TABLE dataloaderinterface_sitesensor add column "UnitAbbreviation" character varying(255) NOT NULL;
-- ALTER TABLE dataloaderinterface_sitesensor add column "SampledMedium" character varying(255) NOT NULL;
-- ALTER TABLE dataloaderinterface_sitesensor add column "LastMeasurementID" integer;
-- ALTER TABLE dataloaderinterface_sitesensor add column "ActivationDate" timestamp with time zone;
-- ALTER TABLE dataloaderinterface_sitesensor add column "ActivationDateUtcOffset" integer;
-- ALTER TABLE dataloaderinterface_sitesensor add column "RegistrationID" integer NOT NULL;
-- ALTER TABLE dataloaderinterface_sitesensor add column "LastMeasurementDatetime" timestamp with time zone;
-- ALTER TABLE dataloaderinterface_sitesensor add column "LastMeasurementUtcOffset" integer;
-- ALTER TABLE dataloaderinterface_sitesensor add column "LastMeasurementValue" double precision;
-- ALTER TABLE dataloaderinterface_sitesensor add column "LastMeasurementUtcDatetime" time(6) with time zone;
