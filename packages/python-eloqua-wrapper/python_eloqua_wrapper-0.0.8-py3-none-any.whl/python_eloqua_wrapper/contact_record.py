"""API Wrapper for Eloqua Contacts"""

from collections import namedtuple

ContactFields = namedtuple("ContactFields", ["id", "first_name", "last_name", "email_address"])


def assemble_url(params):
    param_map = {
        'count': 'count',
        'depth': 'depth',
        'last_updated_at': 'lastUpdatedAt',
        'order_by': 'orderBy',
        'page': 'page',
        'search': 'search',
        'view_id': 'viewId'
    }

    url = f'/api/REST/1.0/data/contacts?'
    url += ''.join(f'&{param_map[key]}={value}' for key, value in params.items())

    return url


class Contact:
    """Abstracts API operations for Eloqua contacts"""
    def __init__(self, session,
                 contact_fields=None,
                 contact_id=None):
        self.session = session
        if contact_fields:
            self.contact_fields = ContactFields(*contact_fields)
        if contact_id:
            self.contact_id = contact_id

    def make_json_body(self):
        """
        Maps dictionary values to the field names that the Eloqua API expects.
        The request body defines the details of the contact to be created.
        emailAddress is the only required field.
        """
        return {
            "id": self.contact_fields.id,
            "emailAddress": self.contact_fields.email_address,
            "firstName": self.contact_fields.first_name,
            "lastName": self.contact_fields.last_name
        }

    def sync_id_from_eloqua(self, response):
        """
        Updates the contact_id value based on a response from the Eloqua API.
        :param response: HTTP response from Eloqua API
        :type response: requests.Response
        """
        self.contact_id = response.json()["id"]

    def create(self):
        """
        Creates a contact that matches the criteria specified by the request body.
        If the contact was created successfully, proceeds to update the contact_id value in the
        Contact object based on the response from the Eloqua API.
        """
        response = self.session.post(url="/api/REST/1.0/data/contact", json=self.make_json_body())
        response.raise_for_status()
        self.sync_id_from_eloqua(response)

    def update(self):
        """
        Updates the contact specified by the id parameter. All properties should be included in
        PUT requests, as some properties will be considered blank if not included.
        """
        response = self.session.put(url=f"/api/REST/1.0/data/contact/{self.contact_id}",
                                    json=self.make_json_body())
        response.raise_for_status()

    def delete(self):
        """Deletes a contact specified by the id parameter."""
        response = self.session.delete(url=f"/api/REST/1.0/data/contact/{self.contact_id}")
        response.raise_for_status()

    def find_contact_by_email(self, email):
        response = self.session.get(url=f"/api/REST/1.0/data/contacts?search=C_EmailAddress="
                                        f"'{email}'&depth=complete")
        return response.json()

    def retrieve_list_of_contacts(self, params):
        """
        Retrieves all contacts that match the criteria specified by the request parameters.
        :param params: search query parameters must be one or more of: 'count', 'depth',
        'last_updated_at', 'order_by', 'page', 'search', and 'view_id'
        :type params: dict
        :return: request HTTP response
        :rtype: requests.Response
        """
        url = assemble_url(params)
        response = self.session.get(url)
        return response.json()
