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
                    
                    # On limite à 3 transactions pour ne pas surcharger l'API (Rate Limit)
                    for tx_hash in block_data.get('txids', [])[:3]:
                        try:
                            # Appel API pour chaque transaction pour avoir le montant
                            tx_resp = requests.get(f'https://api.blockcypher.com/v1/eth/main/txs/{tx_hash}', timeout=3)
                            if tx_resp.status_code == 200:
                                tx_data = tx_resp.json()
                                # Conversion Wei -> ETH (1 ETH = 10^18 Wei)
                                amount_eth = tx_data.get('total', 0) / 10**18
                                
                                # Blockcypher donne le temps de réception
                                received_time = tx_data.get('received')
                                if received_time:
                                    # Format ISO 8601 retourné par l'API (ex: 2023-10-27T10:00:00Z)
                                    tx_time = datetime.fromisoformat(received_time.replace('Z', '+00:00'))
                                else:
                                    tx_time = datetime.now(timezone.utc)

                                transactions.append({
                                    'hash': tx_hash,
                                    'amount': f"{amount_eth:.6f}", # Formatage à 6 décimales
                                    'time': tx_time
                                })
                        except Exception as inner_e:
                            print(f"Erreur détail transaction {tx_hash}: {inner_e}")

    except Exception as e:
        print(f"Erreur lors de la récupération des transactions Ethereum: {e}")

    return render(request, 'ethereum.html', {'transactions': transactions, 'currency': 'Ethereum'})
