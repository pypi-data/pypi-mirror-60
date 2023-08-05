import os, sys, traceback
from google.cloud import logging_v2
from google.cloud import dataproc_v1
from google.protobuf.struct_pb2 import Struct


class Logger(object):

    types = ['cloud_dataproc_job','cloud_function']

    def __init__(self, type, labels):

        if type not in self.types:
            raise ValueError("'type' must be one of %s but was %s" % (self.types,type))

        # For unknown reason, logging to Stackdriver doesnt work if this not in general labels...
        if type == 'cloud_dataproc_job':
            labels["dataproc.googleapis.com/cluster_name"] = os.environ['DATAPROC_CLUSTER_NAME']
            labels["dataproc.googleapis.com/cluster_uuid"] = os.environ['DATAPROC_CLUSTER_UUID']

        self.type = type
        self.client = logging_v2.LoggingServiceV2Client()
        self.log_name, self.resource = self.get_name_and_resource()
        self.labels = labels

    @staticmethod
    def get_execution_id_from_request(request):
        return request.headers.get("Function-Execution-Id")

    @staticmethod
    def get_execution_id_from_context(context):
        return context.event_id

    @staticmethod
    def _get_dataprocjob_id_and_uuid(step_id):
        client = dataproc_v1.JobControllerClient(
            client_options={'api_endpoint': 'europe-west1-dataproc.googleapis.com:443'})
        jobs = client.list_jobs(
            os.environ['GCP_PROJECT'], os.environ['DATAPROC_REGION'],
            cluster_name=os.environ['DATAPROC_CLUSTER_NAME'], job_state_matcher='ACTIVE')

        for element in jobs:
            if element.reference.job_id.startswith(step_id):
                return element.reference.job_id, element.job_uuid


    def get_name_and_resource(self):
        if self.type == 'cloud_dataproc_job':

            # Get job_id and job_uuid. Can only do it if user entered step_id
            job_id, job_uuid = '',''
            if 'step_id' in self.labels:
                job_id, job_uuid = self._get_dataprocjob_id_and_uuid(self.labels['step_id'])

            # Name and resource
            name =  "projects/{}/logs/dataproc.job.driver".format(os.environ['GCP_PROJECT'])
            resource = {
               'labels': {
                  'job_id': job_id,
                  'job_uuid': job_uuid,
                  'region': os.environ['DATAPROC_REGION'],
               },
               'type': 'cloud_dataproc_job'
            }

        elif self.type == 'cloud_function':
            name = "projects/{}/logs/cloudfunctions.googleapis.com%2Fcloud-functions".format(os.environ['GCP_PROJECT'])
            resource = {
                'labels': {
                    'function_name': os.environ['FUNCTION_NAME'],
                    'region': os.environ['FUNCTION_REGION']
                },
                'type': 'cloud_function'
            }
        else:
            raise ValueError("'type' %s is not known'" % self.type)
        return name, resource

    def _log(self, severity, **kwargs):
        json_payload = Struct()
        for k,v in kwargs.items():
            json_payload[k] = v
        self.client.write_log_entries(
            [{'json_payload': json_payload, 'severity': severity}],
            log_name=self.log_name, resource=self.resource, labels=self.labels
        )


    def error(self, message, tb=None):
        if tb is None and sys.exc_info()[0] is not None:
            tb = traceback.format_exc()
        self._log('ERROR',message=message,traceback=tb)

    def info(self,message):
        self._log('INFO',message=message)

    def debug(self,message):
        self._log('DEBUG', message=message)

    def warn(self,message):
        self._log('WARNING',message=message)






