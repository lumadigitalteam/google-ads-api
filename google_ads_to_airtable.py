import requests
import json
from datetime import datetime

# Credenziali e configurazioni
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'
refresh_token = 'YOUR_REFRESH_TOKEN'
developer_token = 'YOUR_DEVELOPER_TOKEN'
customer_id = 'YOUR_CUSTOMER_ID'
airtable_token = 'YOUR_AIRTABLE_PERSONAL_ACCESS_TOKEN'
airtable_base_id = 'YOUR_AIRTABLE_BASE_ID'
airtable_table_name = 'YOUR_AIRTABLE_TABLE_NAME'

# Ottieni l'access token
def get_access_token():
    url = 'https://oauth2.googleapis.com/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(url, data=payload)
    return response.json().get('access_token')

# Richiedi i dati delle campagne Google Ads
def get_google_ads_data(access_token):
    ads_url = f'https://googleads.googleapis.com/v11/customers/{customer_id}/googleAds:search'
    query = """
        SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks, metrics.cost_micros
        FROM campaign
        WHERE segments.date DURING LAST_7_DAYS
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'developer-token': developer_token
    }
    payload = {
        'query': query
    }
    response = requests.post(ads_url, headers=headers, json=payload)
    
    # Verifica il codice della risposta
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Errore nella richiesta API Google Ads: {response.status_code}, {response.text}")
        return []

# Inserisci i dati in Airtable
def send_to_airtable(campaigns):
    airtable_url = f'https://api.airtable.com/v0/{airtable_base_id}/{airtable_table_name}'
    headers = {
        'Authorization': f'Bearer {airtable_token}',
        'Content-Type': 'application/json'
    }

    for campaign in campaigns:
        airtable_data = {
            'fields': {
                'Campaign Name': campaign['campaign.name'],
                'Impressions': campaign['metrics.impressions'],
                'Clicks': campaign['metrics.clicks'],
                'Cost': campaign['metrics.cost_micros'] / 1000000,
                'Date': datetime.now().strftime('%Y-%m-%d')
            }
        }
        response = requests.post(airtable_url, headers=headers, json=airtable_data)
        if response.status_code == 200:
            print(f"Dati campagna aggiunti con successo per: {campaign['campaign.name']}")
        else:
            print(f"Errore nell'aggiunta dei dati per: {campaign['campaign.name']}, Errore: {response.content}")

# Flusso principale
if __name__ == "__main__":
    access_token = get_access_token()
    campaigns = get_google_ads_data(access_token)
    if campaigns:
        send_to_airtable(campaigns)
