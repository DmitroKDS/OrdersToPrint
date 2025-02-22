import config
from requests_oauthlib import OAuth1Session

class MfestMagentaApi:

    def __init__(self) -> None:
        self.magento_connector = OAuth1Session(config.MFEST_ACCES_TOKEN, client_secret = config.MFEST_CLIENT_SECRET, resource_owner_key = config.MFEST_RESOURCE_OWNER_KEY, resource_owner_secret = config.MFEST_RESOURCE_OWNER_SECRET)
    
    
    def get_order_info(self, order: int) -> dict:
        response = self.magento_connector.get(
            f"https://mfest.com.ua/rest/V1/orders?searchCriteria[filter_groups][2][filters][0][field]=increment_id&searchCriteria[filter_groups][2][filters][0][value]={order}&searchCriteria[filter_groups][2][filters][0][condition_type]=eq"
        ).json()["items"][0]

        return response