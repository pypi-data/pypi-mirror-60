""" Requests mock for Resilient REST API """

import logging
import json
import io
import requests
import requests_mock
import pkg_resources
from resilient.resilient_rest_mock import ResilientMock, resilient_endpoint
LOG = logging.getLogger(__name__)


def test_data(filename):
    """Read a test JSON data file"""
    template_file_path = pkg_resources.resource_filename("pytest_resilient_circuits", "data/{}".format(filename))
    with io.open(template_file_path, 'r', encoding="utf-8") as template_file:
        return json.load(template_file)


class BasicResilientMock(ResilientMock):
    """Mock that implements some of the basic REST endpoints.  Test classes can extend this where needed."""

    def __init__(self, *args, **kwargs):
        super(BasicResilientMock, self).__init__(*args, **kwargs)
        self.incident = test_data("200_JSON_GET__incidents_2314.json")

    @resilient_endpoint("POST", "/rest/session")
    def session_post(self, request):
        """ Callback for POST to /rest/session """
        LOG.debug("session_post")
        session_data = {
            "saml_alias": None,
            "csrf_token": "79945884c2e6f2339cbffbbaba01f17b",
            "user_lname": "Doe",
            "user_id": 1,
            "is_ldap": False,
            "is_saml": False,
            "orgs": [
                {
                    "city": "AnyCity",
                    "addr": None,
                    "zip": None,
                    "has_available_twofactor": False,
                    "perms": {
                        "create_shared_layout": True,
                        "administrator": False,
                        "create_incs": True,
                        "master_administrator": True,
                        "observer": False
                    },
                    "supports_ldap": False,
                    "enabled": True,
                    "twofactor_auth_domain": None,
                    "attachments_enabled": True,
                    "has_saml": False,
                    "state": None,
                    "addr2": None,
                    "twofactor_cookie_lifetime_secs": 0,
                    "require_saml": False,
                    "tasks_private": False,
                    "authorized_ldap_group": None,
                    "id": 201,
                    "name": self.org_name
                },
                {
                    "city": None,
                    "addr": None,
                    "zip": None,
                    "has_available_twofactor": False,
                    "perms": {
                        "create_shared_layout": True,
                        "administrator": False,
                        "create_incs": True,
                        "master_administrator": True,
                        "observer": False
                    },
                    "supports_ldap": False,
                    "enabled": True,
                    "twofactor_auth_domain": None,
                    "attachments_enabled": True,
                    "has_saml": False,
                    "state": None,
                    "addr2": None,
                    "twofactor_cookie_lifetime_secs": 0,
                    "require_saml": False,
                    "tasks_private": False,
                    "authorized_ldap_group": None,
                    "id": 202,
                    "name": "Mock Org"
                }
            ],
            "session_ip": "192.168.56.1",
            "user_fname": "John",
            "user_email": self.email
        }
        cookies = {'JSESSIONID': 'FakeSessionId'}
        return requests_mock.create_response(request,
                                             status_code=200,
                                             cookies=requests.cookies.cookiejar_from_dict(cookies),
                                             json=session_data)

    @resilient_endpoint("GET", "/incidents/[0-9]+$")
    def incident_get(self, request):
        """ Callback for GET to /orgs/<org_id>/incidents/<inc_id> """
        LOG.debug("incident_get")
        return requests_mock.create_response(request,
                                             status_code=200,
                                             json=self.incident)

    @resilient_endpoint("PUT", "/incidents/[0-9]+")
    def incident_put(self, request):
        """ Callback for PUT to /orgs/<org_id>/incidents/<inc_id> """
        LOG.debug("incident_put")
        self.incident = request.json()
        return requests_mock.create_response(request,
                                             status_code=200,
                                             json=self.incident)

    @resilient_endpoint("POST", "/incidents/")
    def incident_post(self, request):
        """ Callback for POST to /orgs/<org_id>/incidents """
        LOG.debug("incident_post")
        self.incident = request.json()
        return requests_mock.create_response(request,
                                             status_code=200,
                                             json=self.incident)

    @resilient_endpoint("GET", "/orgs/[0-9]+$")
    def org_get(self, request):
        """ Callback for GET to /orgs/<org_id> """
        LOG.debug("org_get")
        org_data = {"users": {"2": {"id": 2,
                                    "fname": "Resilient",
                                    "lname": "Sysadmin",
                                    "status": "A",
                                    "email": self.email,
                                    "phone": None,
                                    "cell": None,
                                    "title": None,
                                    "notes": None,
                                    "locked": False,
                                    "enabled": True,
                                    "roles": {
                                        "administrator": False,
                                        "observer": False,
                                        "master_administrator": True,
                                        "create_incs": True
                                    },
                                    "last_login": 1475614308048,
                                    "org_id": 202,
                                    "group_ids": [],
                                    "is_external": False},
                              "3": {"id": 3,
                                    "fname": "User",
                                    "lname": "Three",
                                    "status": "A",
                                    "email": "someone@example.com",
                                    "phone": None,
                                    "cell": None,
                                    "title": None,
                                    "notes": None,
                                    "locked": False,
                                    "enabled": True,
                                    "roles": {
                                        "administrator": False,
                                        "observer": False,
                                        "master_administrator": True,
                                        "create_incs": True},
                                    "last_login": 1476711664869,
                                    "org_id": 202,
                                    "group_ids": [],
                                    "is_external": False}
                              },
                    "actions_framework_enabled": True
                    }
        return requests_mock.create_response(request, status_code=200, json=org_data)

    @resilient_endpoint("GET", "/types/incident/fields")
    def incident_fields_get(self, request):
        """ Callback for GET to /orgs/<org_id>/types/incident/fields """
        LOG.debug("incident_fields_get")
        field_data = test_data("200_JSON_GET__types_incident_fields.json")
        return requests_mock.create_response(request, status_code=200, json=field_data)

    @resilient_endpoint("GET", "/types/actioninvocation/fields")
    def action_fields_get(self, request):
        """ Callback for GET to /orgs/<org_id>/types/actioninvocation/fields """
        LOG.debug("action_fields_get")
        field_data = test_data("200_JSON_GET__types_incident_fields.json")
        return requests_mock.create_response(request, status_code=200, json=field_data)

    @resilient_endpoint("GET", "/types/__function/fields")
    def function_fields_get(self, request):
        """ Callback for GET to /orgs/<org_id>/types/__function/fields """
        LOG.debug("function_fields_get")
        field_data = test_data("200_JSON_GET__types_function_fields.json")
        return requests_mock.create_response(request, status_code=200, json=field_data)

    @resilient_endpoint("GET", "/actions")
    def actions_get(self, request):
        """ Callback for GET to /orgs/<org_id>/actions """
        LOG.debug("actions_get")
        data = test_data("200_JSON_GET__actions.json")
        return requests_mock.create_response(request, status_code=200, json=data)

    @resilient_endpoint("GET", "/message_destinations")
    def message_destinations_get(self, request):
        """ Callback for GET to /orgs/<org_id>/message_destinations """
        LOG.debug("message_destinations_get")
        data = test_data("200_JSON_GET__message_destinations.json")
        return requests_mock.create_response(request, status_code=200, json=data)

    @resilient_endpoint("GET", "/functions")
    def functions_get(self, request):
        """ Callback for GET to /orgs/<org_id>/functions """
        LOG.debug("functions_get")
        data = test_data("200_JSON_GET__functions.json")
        return requests_mock.create_response(request, status_code=200, json=data)

    @resilient_endpoint("GET", "/functions/.*$")
    def functions_get_xxx(self, request):
        """ Callback for GET to /orgs/<org_id>/functions/nnn """
        LOG.debug("functions_get_xxx")
        data = test_data("200_JSON_GET__functions.json")
        return requests_mock.create_response(request, status_code=200, json=data["entities"][0])

    @resilient_endpoint("GET", "/incidents/[0-9]+/attachments/[0-9]+/contents$")
    def attachment_contents_get(self, request):
        """ Callback for GET to attachment contents """
        LOG.debug("attachment_contents_get")
        return requests_mock.create_response(request,
                                             status_code=200,
                                             json='"abcdef"')
