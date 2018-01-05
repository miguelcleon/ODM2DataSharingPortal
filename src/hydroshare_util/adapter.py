from hs_restclient import HydroShare, HydroShareHTTPException


class HydroShareAdapter(HydroShare):
    def getUserInfo(self, headers=None):
        return self.get_user_info(headers=headers)

    def get_user_info(self, headers=None):
        """
                Query the GET /hsapi/userInfo/ REST end point of the HydroShare server.

                :raises: HydroShareHTTPException to signal an HTTP error

                :return: A JSON object representing user info, for example:

                {
                    "username": "username",
                    "first_name": "First",
                    "last_name": "Last",
                    "email": "user@domain.com"
                }
                """
        url = "{url_base}/userInfo/".format(url_base=self.url_base)

        response = self._request('GET', url, headers=headers)
        if response.status_code != 200:
            raise HydroShareHTTPException((url, 'GET', response.status_code))

        return response.json()