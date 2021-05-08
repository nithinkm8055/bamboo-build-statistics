from __future__ import division
import requests
import xml.etree.ElementTree as ET
import sys
import server_config
import datetime
from itertools import repeat
import concurrent.futures

def get_all_branches_in_plan(planKey):

    uri = "{}/rest/api/latest/plan/{}/branch?enabledOnly&max-result=1000".format(server_config.bamboo_uri, planKey)
    res = requests.get(url=uri, verify=False, headers={"Authorization": "Basic " + server_config.bamboo_auth_token})
    
    if res.status_code == 200:
       PLAN_BRANCHES_DICT = populate_dict(res, planKey)
    
    elif res.status_code == 401:
        return "401"
    
    else:
        return "400"

    return PLAN_BRANCHES_DICT


def populate_dict(res, planKey):
    
    PLAN_BRANCHES_DICT = {}
    string_xml = res.content
    parsed_xml_response = ET.fromstring(string_xml)

    branch_element_list = list(parsed_xml_response.iter('*'))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(populate_build_stat_for_branches, branch_element_list, repeat(planKey))
        for result in results:
            if result is not None:
                PLAN_BRANCHES_DICT.update(result)

    return PLAN_BRANCHES_DICT


def populate_build_stat_for_branches(branchElement, planKey):

    """
        populates the build statistics data for every branch in plan to a dictionary
    """
    PLAN_BRANCHES_DICT = {}
    # for child in parsed_xml_response.iter('*'):
    
    if branchElement.tag == "branch":
        latest_build_status, number_of_pass_builds, number_of_fail_builds, number_of_builds, no_of_bamboo_builds_on_branch = get_build_status_per_branch(planKey, branchElement.get("shortName"))
        build_duration_in_hour, build_start_time = get_build_duration_for_branch(branchElement.get("key"))
        # PLAN_BRANCHES_DICT[branchElement.get("shortName")] = [{chbranchElementild.find("link").get("href")}]
        success_ratio = 0
        if number_of_builds > 0:
            success_ratio = (number_of_pass_builds / number_of_builds) * 100

        PLAN_BRANCHES_DICT[branchElement] = [latest_build_status, number_of_builds, number_of_pass_builds, number_of_fail_builds, round(success_ratio, 2), no_of_bamboo_builds_on_branch, round(build_duration_in_hour, 2), build_start_time]
        
        return PLAN_BRANCHES_DICT

def get_build_status_per_branch(planKey, branchname):

    """
        returns the diffrent build statistics data for branch
    """

    branch_stats_uri = "{}/rest/api/latest/result/{}/branch/{}".format(server_config.bamboo_uri, planKey, branchname)
    response = requests.get(branch_stats_uri, verify=False, headers={"Authorization": "Basic " + server_config.bamboo_auth_token})

    if response.status_code == 200:
        build_result = ET.fromstring(response.content)
        build_states = build_result.find('.//results')

        counter = 0
        number_of_pass_builds = 0
        number_of_fail_builds = 0
        latest_build_status = "Not Defined"
        no_of_bamboo_builds_on_branch = 0

        if build_states is not None:
            for build_state in build_states:
                if counter == 0:
                    latest_build_status =  build_state.find(".//buildState").text
                    no_of_bamboo_builds_on_branch = int(build_state.find(".//resultNumber").text)
                if build_state.find(".//buildState").text == "Successful":
                    number_of_pass_builds += 1
                elif build_state.find(".//buildState").text == "Failed":
                    number_of_fail_builds += 1
                counter += 1

            return latest_build_status, number_of_pass_builds, number_of_fail_builds, counter, no_of_bamboo_builds_on_branch
    
    return "error", 0, 0, 0, 0


def get_build_duration_for_branch(branchKey):
    """
        returns the duration for the latest finished build in hours
    """
    build_result_uri= "{}/rest/api/latest/result/{}/latest".format(server_config.bamboo_uri, branchKey)
    response = requests.get(build_result_uri, verify=False, headers={"Authorization": "Basic " + server_config.bamboo_auth_token})
    build_duration_in_hour = 0
    build_start_time = 0
    
    if response.status_code == 200:
        parsed_response = ET.fromstring(response.content)
        build_result = parsed_response.find('.//buildDurationInSeconds').text
        build_start_time_in_utc = parsed_response.find('.//buildStartedTime').text
        build_start_time_in_utc = build_start_time_in_utc[0:-6] # slice date text to remove UTC offset as no support in python2 
        build_start_time_obj = datetime.datetime.strptime(build_start_time_in_utc, "%Y-%m-%dT%H:%M:%S.%f")
        build_start_time = build_start_time_obj.strftime("%a, %d %b %Y, %I:%M %p")
        build_duration_in_hour = int(build_result) / 3600
    
    return build_duration_in_hour, build_start_time


def get_branch_key(planKey, branchname):
    uri = "{}/rest/api/latest/result/{}/branch/{}".format(server_config.bamboo_uri, planKey, branchname)
    response = requests.get(uri, verify=False, headers={"Authorization": "Basic " + server_config.bamboo_auth_token})
    branchkey = ""
    if response.status_code == 200:
        parsed_response = ET.fromstring(response.content)
        branch_element_list = parsed_response.iter('*')

        for branch_elem in branch_element_list:
            if branch_elem.tag == "plan":
                branchkey = branch_elem.get("key")

    return branchkey


def get_total_number_of_builds_from_active_branches(branch_dict):
    """
    """
    number_of_builds = 0
    for key, value in branch_dict.items():
        number_of_builds += value[5]
    return number_of_builds