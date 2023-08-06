# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime

import vcr
from marquez_client import MarquezClient
from pytest import fixture


@fixture(scope='class')
def namespace_name():
    return "ns_name_for_testing"


@fixture(scope='class')
def marquez_client_default_ns():
    return MarquezClient(host="localhost",
                         port=5000)


@fixture(scope='class')
@vcr.use_cassette(
    'tests/fixtures/vcr/test_jobruns/namespace_for_jobruns_tests.yaml')
def existing_namespace(marquez_client_default_ns, namespace_name):
    owner_name = "ns_owner"
    description = "this is a namespace for testing."

    return marquez_client_default_ns.create_namespace(
        namespace_name, owner_name, description)


@fixture(scope='class')
def marquez_client(namespace_name):
    return MarquezClient(host="localhost", namespace_name=namespace_name,
                         port=5000)


@fixture(scope='class')
@vcr.use_cassette(
    'tests/fixtures/vcr/test_jobruns/job_for_jobruns_tests.yaml')
def existing_job(marquez_client, existing_namespace):
    input_datsets = ['input1', 'input2']
    output_datsets = ['output1', 'output2']
    created_job = marquez_client.create_job(
        'some_job', 'BATCH', 'https://github.com/wework/jobs/commit/124f',
        input_datsets,
        output_datsets)
    return created_job


@fixture(scope='function')
def job_run_args():
    return None


@fixture(scope='function')
def nominal_start_time():
    return "2019-10-14T21:20:04.586Z"


@fixture(scope='function')
def nominal_end_time(nominal_start_time):
    return "2019-10-14T22:20:04.586Z"


@fixture(scope='function')
@vcr.use_cassette(
    'tests/fixtures/vcr/test_jobruns/jobrun_for_jobruns_tests.yaml')
def existing_jobrun(marquez_client, existing_job, job_run_args,
                    nominal_start_time, nominal_end_time):
    created_job_run = marquez_client.create_job_run(
        existing_job['name'], run_args=job_run_args,
        nominal_start_time=str(nominal_start_time),
        nominal_end_time=str(nominal_end_time))
    return created_job_run


@vcr.use_cassette(
    'tests/fixtures/vcr/test_jobruns/test_create_jobrun.yaml')
def test_create_jobrun(marquez_client, existing_job, job_run_args,
                       nominal_start_time, nominal_end_time):
    nominal_start_time = str(nominal_start_time)
    nominal_end_time = str(nominal_end_time)

    created_job_run = marquez_client.create_job_run(
        existing_job['name'], run_args=job_run_args,
        nominal_start_time=nominal_start_time,
        nominal_end_time=nominal_end_time)

    assert created_job_run['runId'] is not None


@vcr.use_cassette(
    'tests/fixtures/vcr/test_jobruns/test_get_jobrun.yaml')
def test_get_jobrun(marquez_client, existing_jobrun, job_run_args):
    marquez_client.mark_job_run_as_started(existing_jobrun['runId'])
    get_jobrun_response = marquez_client.get_job_run(existing_jobrun['runId'])
    assert get_jobrun_response['runId'] == existing_jobrun['runId']
    assert get_jobrun_response['runState'] == "RUNNING"
    assert get_jobrun_response['nominalStartTime'] is not None
    assert get_jobrun_response['nominalEndTime'] is not None


@vcr.use_cassette(
    'tests/fixtures/vcr/test_jobruns/test_jobrun_can_be_marked_aborted.yaml')
def test_jobrun_can_be_marked_aborted(marquez_client, existing_jobrun):
    marquez_client.mark_job_run_as_aborted(existing_jobrun['runId'])
    get_jobrun_response = marquez_client.get_job_run(existing_jobrun['runId'])
    assert get_jobrun_response['runId'] == existing_jobrun['runId']
    assert get_jobrun_response['runState'] == "ABORTED"


@vcr.use_cassette(
    'tests/fixtures/vcr/test_jobruns/test_jobrun_can_be_marked_failed.yaml')
def test_jobrun_can_be_marked_failed(marquez_client, existing_jobrun):
    marquez_client.mark_job_run_as_failed(existing_jobrun['runId'])
    get_jobrun_response = marquez_client.get_job_run(existing_jobrun['runId'])
    assert get_jobrun_response['runId'] == existing_jobrun['runId']
    assert get_jobrun_response['runState'] == "FAILED"


@vcr.use_cassette(
    'tests/fixtures/vcr/test_jobruns/test_jobrun_can_be_marked_completed.yaml')
def test_jobrun_can_be_marked_completed(marquez_client, existing_jobrun):
    marquez_client.mark_job_run_as_completed(existing_jobrun['runId'])
    get_jobrun_response = marquez_client.get_job_run(existing_jobrun['runId'])
    assert get_jobrun_response['runId'] == existing_jobrun['runId']
    assert get_jobrun_response['runState'] == "COMPLETED"
