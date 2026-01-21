from django.shortcuts import render
from datetime import datetime, timezone
import requests

def bitcoin_transactions(request):
    transactions = []
    try:
        # API publique de Blockchain.info pour les transactions non confirmées
        response = requests.get('https://blockchain.info/unconfirmed-transactions?format=json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            # On prend les 10 premières transactions
            for tx in data.get('txs', [])[:10]:
                # Calcul du montant total en BTC (somme des sorties)
                total_value = sum(out.get('value', 0) for out in tx.get('out', []))
                # Le timestamp de l'API est en UTC (secondes depuis l'époque)
                # On crée un objet datetime "aware" (avec info de fuseau horaire UTC)
                tx_time = datetime.fromtimestamp(tx.get('time'), tz=timezone.utc)
                
                transactions.append({
                    'hash': tx.get('hash'),
                    'amount': total_value / 100000000.0, # Conversion Satoshi -> BTC
                    'time': tx_time
                })
    except Exception as e:
        print(f"Erreur lors de la récupération des transactions Bitcoin: {e}")

    return render(request, 'bitcoin.html', {'transactions': transactions, 'currency': 'Bitcoin'})

def ethereum_transactions(request):
    transactions = []
    try:
        # API publique de Blockcypher pour obtenir le dernier bloc Ethereum
        response = requests.get('https://api.blockcypher.com/v1/eth/main', timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_url = data.get('latest_url')
            if latest_url:
                block_resp = requests.get(latest_url, timeout=5)
                if block_resp.status_code == 200:
                    block_data = block_resp.json()
                    # On récupère les hash des transactions du dernier bloc
                    for tx_hash in block_data.get('txids', [])[:10]:
                        transactions.append({
                            'hash': tx_hash,
                            'amount': 'N/A', # Nécessiterait un appel API par transaction
                            'time': datetime.now(timezone.utc) # On utilise maintenant UTC explicitement
                        })
    except Exception as e:
        print(f"Erreur lors de la récupération des transactions Ethereum: {e}")

    return render(request, 'ethereum.html', {'transactions': transactions, 'currency': 'Ethereum'})
