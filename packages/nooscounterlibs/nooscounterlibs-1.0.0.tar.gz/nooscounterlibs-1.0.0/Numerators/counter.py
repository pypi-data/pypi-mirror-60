import requests


class Numerator(object):
    def __init__(self, api_code, api_path):
        self.api_code = api_code
        self.api_path = api_path
        self._api_url = "https://{}.execute-api.eu-central-1.amazonaws.com/Prod/{}".format(self.api_code, self.api_path)

    def counter(self, numerator_code):
        """
        "op": "counter",
        "numerator": "TEST"
        :param numerator_code:
        :return:
        """
        response = requests.post(self._api_url, json={"op": "counter", "numerator": numerator_code})
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("complete"):
                return {
                    "counter": response_data.get("numerator_counter"),
                    "format": response_data.get("numeretor_format")
                }

        return None
