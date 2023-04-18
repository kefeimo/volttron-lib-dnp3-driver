"""
This test suits focus on the exposed RPC calls.
It utilizes a vip agent to evoke the RPC calls.
The volltron instance and dnp3-agent is start manually.
Note: several fixtures are used
    volttron_platform_wrapper
    vip_agent
    dnp3_outstation_agent
"""
import pathlib

import gevent
import pytest
import os
from volttron.client.vip.agent import build_agent
from time import sleep
import datetime
from dnp3_python.dnp3station.outstation_new import MyOutStationNew
import random
import subprocess
from volttron.utils import is_volttron_running
import json
# from utils.testing_utils import *
from volttrontesting.fixtures.volttron_platform_fixtures import volttron_instance
from volttron.client.known_identities import CONFIGURATION_STORE, PLATFORM_DRIVER
import json
from volttron.utils import jsonapi

import logging

logging_logger = logging.getLogger(__name__)

dnp3_vip_identity = "dnp3_outstation"
platform_driver_id = PLATFORM_DRIVER


# @pytest.fixture(scope="module")
# def volttron_home():
#     """
#     VOLTTRON_HOME environment variable suggested to setup at pytest.ini [env]
#     """
#     volttron_home: str = os.getenv("VOLTTRON_HOME")
#     assert volttron_home
#     return volttron_home
#
#
# def test_volttron_home_fixture(volttron_home):
#     assert volttron_home
#     print(volttron_home)


def test_testing_file_path():
    parent_path = os.getcwd()
    dnp3_agent_config_path = os.path.join(parent_path, "dnp3-outstation-config.json")
    # print(dnp3_agent_config_path)
    logging_logger.info(f"test_testing_file_path {dnp3_agent_config_path}")


def test_volttron_instance_fixture(volttron_instance):
    print(volttron_instance)
    logging_logger.info(f"=========== volttron_instance_new.volttron_home: {volttron_instance.volttron_home}")
    logging_logger.info(f"=========== volttron_instance_new.skip_cleanup: {volttron_instance.skip_cleanup}")
    logging_logger.info(f"=========== volttron_instance_new.vip_address: {volttron_instance.vip_address}")


@pytest.fixture(scope="module")
def vip_agent(volttron_instance):
    # build a vip agent
    a = volttron_instance.build_agent()
    print(a)
    return a


def test_vip_agent_fixture(vip_agent):
    print(vip_agent)
    logging_logger.info(f"=========== vip_agent: {vip_agent}")
    logging_logger.info(f"=========== vip_agent.core.identity: {vip_agent.core.identity}")
    logging_logger.info(f"=========== vip_agent.vip.peerlist().get(): {vip_agent.vip.peerlist().get()}")


@pytest.fixture(scope="module")
def install_platform_driver(volttron_instance) -> dict:
    """
    Install and start a dnp3-outstation-agent, return its vip-identity
    """
    # install a dnp3-outstation-agent
    # TODO: improve the following hacky path resolver
    parent_path = pathlib.Path(__file__)
    dnp3_outstation_package_path = pathlib.Path(parent_path).parent.parent
    dnp3_agent_config_path = str(os.path.join(parent_path, "dnp3-outstation-config.json"))
    config = {
        "driver_scrape_interval": 0.05,
        "publish_breadth_first_all": "false",
        "publish_depth_first": "false",
        "publish_breadth_first": "false"
    }
    uuid = volttron_instance.install_agent(
        # agent_dir=dnp3_outstation_package_path,
        agent_dir="volttron-platform-driver",
        config_file=config,
        start=False,  # Note: for some reason, need to set to False, then start
        vip_identity=platform_driver_id)
    # start agent with retry
    # pid = retry_call(volttron_instance.start_agent, f_kwargs=dict(agent_uuid=uuid), max_retries=5, delay_s=2,
    #                  wait_before_call_s=2)

    # # check if running with retry
    # retry_call(volttron_instance.is_agent_running, f_kwargs=dict(agent_uuid=uuid), max_retries=5, delay_s=2,
    #            wait_before_call_s=2)
    gevent.sleep(5)
    # pid = volttron_instance.start_agent(uuid)
    # gevent.sleep(5)
    logging_logger.info(
        f"=========== volttron_instance.is_agent_running(uuid): {volttron_instance.is_agent_running(uuid)}")
    # TODO: get retry_call back
    return uuid


def test_install_platform_driver_fixture(install_platform_driver, vip_agent, volttron_instance):
    uuid = install_platform_driver
    print(uuid)
    logging_logger.info(f"=========== dnp3_outstation_agent ids: {uuid}")
    logging_logger.info(f"=========== vip_agent.vip.peerlist().get(): {vip_agent.vip.peerlist().get()}")
    # logging_logger.info(f"=========== volttron_instance_new.is_agent_running(puid): "
    #                     f"{volttron_instance.is_agent_running(install_platform_driver['uuid'])}")


@pytest.fixture(scope="module")
def configure_platform_driver(install_platform_driver, vip_agent, volttron_instance):
    uuid = install_platform_driver

    capabilities = {"edit_config_store": {"identity": PLATFORM_DRIVER}}
    volttron_instance.add_capabilities(vip_agent.core.publickey, capabilities)

    # Add Fake Driver to Platform Driver
    registry_config_string = """Point Name,Volttron Point Name,Group,Variation,Index,Scaling,Units,Writable,Notes
    AnalogInput_index0,AnalogInput_index0,30,6,0,1,NA,FALSE,Double Analogue input without status
    AnalogInput_index1,AnalogInput_index1,30,6,1,1,NA,FALSE,Double Analogue input without status
    AnalogInput_index2,AnalogInput_index2,30,6,2,1,NA,FALSE,Double Analogue input without status
    AnalogInput_index3,AnalogInput_index3,30,6,3,1,NA,FALSE,Double Analogue input without status
    BinaryInput_index0,BinaryInput_index0,1,2,0,1,NA,FALSE,Single bit binary input with status
    BinaryInput_index1,BinaryInput_index1,1,2,1,1,NA,FALSE,Single bit binary input with status
    BinaryInput_index2,BinaryInput_index2,1,2,2,1,NA,FALSE,Single bit binary input with status
    BinaryInput_index3,BinaryInput_index3,1,2,3,1,NA,FALSE,Single bit binary input with status
    AnalogOutput_index0,AnalogOutput_index0,40,4,0,1,NA,TRUE,Double-precision floating point with flags
    AnalogOutput_index1,AnalogOutput_index1,40,4,1,1,NA,TRUE,Double-precision floating point with flags
    AnalogOutput_index2,AnalogOutput_index2,40,4,2,1,NA,TRUE,Double-precision floating point with flags
    AnalogOutput_index3,AnalogOutput_index3,40,4,3,1,NA,TRUE,Double-precision floating point with flags
    BinaryOutput_index0,BinaryOutput_index0,10,2,0,1,NA,TRUE,Binary Output with flags
    BinaryOutput_index1,BinaryOutput_index1,10,2,1,1,NA,TRUE,Binary Output with flags
    BinaryOutput_index2,BinaryOutput_index2,10,2,2,1,NA,TRUE,Binary Output with flags
    BinaryOutput_index3,BinaryOutput_index3,10,2,3,1,NA,TRUE,Binary Output with flags"""
    # Note: vctl config store <platform_driver_id> <config-name> <config-content-path> --csv
    config_name = "dnp3.csv"
    config_content = registry_config_string
    vip_agent.vip.rpc.call(CONFIGURATION_STORE,
                           "manage_store",
                           platform_driver_id,
                           config_name,
                           config_content,
                           config_type="csv")

    driver_config = {
        "driver_config": {"master_ip": "0.0.0.0", "outstation_ip": "127.0.0.1",
                          "master_id": 2, "outstation_id": 1,
                          "port": 20000},
        "registry_config": "config://dnp3.csv",
        "driver_type": "dnp3",
        "interval": 5,
        "timezone": "UTC",
        "heart_beat_point": "random_bool"
    }
    # Note: vctl config store <platform_driver_id> <config-name> <config-content-path> --json
    config_name = "devices/campus/building/dnp3"
    config_content = driver_config
    vip_agent.vip.rpc.call(CONFIGURATION_STORE,
                           "manage_store",
                           platform_driver_id,
                           config_name,
                           jsonapi.dumps(config_content),  # Note: need to use jsonapi.dump, not json.dump
                           config_type='json')

    gevent.sleep(10)
    pid = volttron_instance.start_agent(uuid)
    return pid


def test_configure_platform_driver_fixture(configure_platform_driver, install_platform_driver, vip_agent,
                                           volttron_instance):
    uuid = install_platform_driver
    pid = configure_platform_driver
    logging_logger.info(f"=========== dnp3_outstation_agent ids: {uuid}")
    logging_logger.info(f"=========== volttron_instance_new.is_agent_running(puid): "
                        f"{volttron_instance.is_agent_running(uuid)}")
    logging_logger.info(f"=========== vip_agent.vip.peerlist().get(): {vip_agent.vip.peerlist().get()}")
    logging_logger.info(f"=========== platform_driver_id: {platform_driver_id}")

    res = vip_agent.vip.rpc.call(CONFIGURATION_STORE, "manage_list_stores").get(5)
    logging_logger.info(f"=========== manage_list_stores {res}")

    res = vip_agent.vip.rpc.call(CONFIGURATION_STORE, "manage_list_configs", platform_driver_id).get(5)
    logging_logger.info(f"=========== manage_list_configs {res}")


def test_scrape_all(vip_agent, configure_platform_driver):
    res = vip_agent.vip.rpc.call(PLATFORM_DRIVER, "scrape_all",
                                 "campus/building/dnp3").get(timeout=10)
    logging_logger.info(f"=========== scrape_all {res}")

from volttron.client.vip.agent import build_agent


def test_sandbox():
    a = build_agent()
    print(a)

    res = a.vip.rpc.call(CONFIGURATION_STORE,
                         "manage_get", "platform_driver_for_dnp3", "devices/campus/building/dnp3").get(5)
    logging_logger.info(f"=========== a.vip.rpc.call(CONFIGURATION_STORE, manage_store, {res}")

    res = a.vip.rpc.call(PLATFORM_DRIVER, "scrape_all",
                                 "devices/campus/building/dnp3").get(timeout=10)
    logging_logger.info(f"=========== scrape_all, {res}")
