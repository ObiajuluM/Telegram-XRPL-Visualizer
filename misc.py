from telebot import *
from xrpl.models import AccountInfo, AccountInfo, Tx, LedgerEntry
from xrpl.clients import JsonRpcClient
import requests
from xrpl.models.requests.ledger_entry import Offer
from xrpl.utils import drops_to_xrp, ripple_time_to_datetime



telegram_key = ""

welcome_msg = (
    "👋 Welcome to Telegram XRPL Explorer,\nHow can i help you navigate the XRP Ledger for information?. Use command /mainnet and /testnet to switch between networks"
)

dashboard = types.ReplyKeyboardMarkup(
    one_time_keyboard=True, resize_keyboard=True
)
dashboard.add("💳 Account", "🏧 Payment Transaction",
               "🪙 Token", "🖼️ NFT",
                "💹 Token Offer", "🔒 Escrow",
                "🧾 Check", "🖼️ NFT Offer", row_width=3)

enter_pay = "Enter the payment transaction id..."
enter_acc = "Enter the account address..."
enter_token = "Enter the token and issuer name in this format USD.rE16eRf6h..."
enter_nft = "Enter the nft id..."
enter_tko = "Enter the offer id..."
enter_escrow = "Enter the escrow id..."
enter_check = "Enter the check id..."
enter_nfofer = "Enter the nft offer id..."


def validate_hex_to_symbol(hex: str = None) -> str:
    result = ""
    try:
        if len(hex) > 3:
            bytes_string = bytes.fromhex(str(hex)).decode("utf-8")
            hex = bytes_string.rstrip("\x00")
            result = hex
    except Exception as e:
        return result
    finally:
        return result


def validate_symbol_to_hex(symbol: str = None) -> str:
    result = ""
    try:
        if len(symbol) > 3:
            bytes_string = bytes(str(symbol).encode("utf-8"))
            symbol = bytes_string.hex().upper().ljust(40, "0")
            result = symbol
    except Exception as e:
        return result
    finally:
        return result


def xrp_format_to_transfer_fee(format: int) -> float:
    """convert xrp fee format to usable fee in percentage"""
    base_fee = 1_000_000_000  # 1000000000 == 0%
    val = format - base_fee
    return val / base_fee * 100


def token_market_info(token: str, issuer: str) -> dict:
    """retrieve token market info, use to retrieve token price; image; \n
    see x_constants.market_info_type\n
    will probably only work on mainnet"""
    return requests.get(
        f"https://s1.xrplmeta.org/token/{validate_symbol_to_hex(token)}:{issuer}"
    ).json()


def xrp_format_to_nft_fee(format: int) -> float:
    """convert xrp fee format to usable fee in percentage"""
    assert format <= 50000
    max_fee = 50
    return (max_fee * format) / 50000


def get_account_info(client: JsonRpcClient, wallet_addr: str):
    """returns information about an account"""
    query = AccountInfo(account=wallet_addr, ledger_index="validated")
    result = client.request(query).result
    if "account_data" in result:
        account_data = result["account_data"]
        return f"""
            ℹ️ Information about the account: {account_data['Account']}

📇 Index: {account_data['index']}

🪙 XRP Balance: {str(drops_to_xrp(account_data['Balance']))}

🖇️ Sequence: {account_data["Sequence"]}

📔 Tick Size: {account_data['TickSize'] if 'TickSize' in account_data else 0}

🫴 Token Transfer Fee: {xrp_format_to_transfer_fee(account_data["TransferRate"]) if 'TransferRate' in account_data else 0}

🔗 URL: {validate_hex_to_symbol(account_data["Domain"]) if "Domain" in account_data else ''}

📧 Email: {validate_hex_to_symbol(account_data["EmailHash"]) if "EmailHash" in account_data else '' }
"""


def get_nft_info(nft_id: int) -> dict:  # external api
    """returns information about an NFT \n this method uses an external api\n
    will probably only work on mainnet"""
    response = requests.get(f"https://api.xrpldata.com/api/v1/xls20-nfts/nft/{nft_id}").json()
    if "data" in response and isinstance(response["data"]["nft"], dict):
        nft = response["data"]["nft"]
        return f"""
        ℹ️ Information about the NFT: {nft_id}

👤 Issuer: {nft['Issuer']}

🔑👤 Owner: {nft['Owner']}

🪪 Taxon: {nft['Taxon']}

🖇️ Sequence: {nft['Sequence']}

🫴 Transfer Fee: {xrp_format_to_nft_fee(nft["TransferFee"])}

🔗 URI: {validate_hex_to_symbol(nft["URI"])}

🏴 Flags: {nft['Flags']}
"""


def pay_txn_info(client: JsonRpcClient, txid: str) -> dict:
    """return more information on a single pay transaction"""
    query = Tx(transaction=txid)
    result = client.request(query).result
    if "Account" in result:
        return f"""
        ℹ️ Information about the payment transaction: {txid}

👤🫳 Sender: {result["Account"]}

🪙 Token: {"XRP" if isinstance(result["meta"]["delivered_amount"], str) else validate_hex_to_symbol(result["meta"]["currency"])}

👤🫴 Receiver: {result["Destination"]}

👤 Issuer: {"" if isinstance(result["meta"]["delivered_amount"], str) else result["meta"]["delivered_amount"]["issuer"]}

💰 Amount: {str(drops_to_xrp(result["Amount"])) if isinstance(result["meta"]["delivered_amount"], str) else result["meta"]["delivered_amount"]["value"]}

🫴 TxFee: {str(drops_to_xrp(result["Fee"]))}

⌛ Date: {ripple_time_to_datetime(result["date"])}

🆔 Txid: {result["hash"]}

🤔 Txtype: {result["TransactionType"]}

🏴 Flags: {result["Flags"] if 'Flags' in result else ''} 

🖇️ Sequence: {result["Sequence"]}

🔏 Signature: {result["TxnSignature"]}

📇 Index: {result["meta"]["TransactionIndex"]}

📄 Final Result: {result["meta"]["TransactionResult"]}
"""

def get_token_info(client: JsonRpcClient, issuer: str, token: str) -> dict:
    """returns information about a token"""
    token_info = {}
    tk = {}
    metrics = {}
    market = token_market_info(token, issuer)
    metrics = {}
    if "metrics" in market:
        metrics = market["metrics"]
    if "meta" in market and "token" in market["meta"]:
        tk = market["meta"]["token"]
    query = AccountInfo(account=issuer, ledger_index="validated")
    result = client.request(query).result
    if "account_data" in result:
        account_data = result["account_data"]
        return f"""
        ℹ️ Information about the token: {token}.{issuer}

👤 Issuer: {account_data["Account"]}

📔 Tick Size: {account_data["TickSize"] if "TickSize" in account_data else 0}

🫴 Transfer Fee: {xrp_format_to_transfer_fee(account_data["TransferRate"]) if "TransferRate" in account_data else 0}

📇 Index: {account_data["index"]}

🔗 Domain: { validate_hex_to_symbol(account_data["Domain"]) if "Domain" in account_data else ''}

📧 Email: {validate_hex_to_symbol(account_data["EmailHash"]) if "EmailHash" in account_data else ""}

🚰 Supply: {metrics["supply"] if "supply" in metrics else ""}

💹 Market Cap: {metrics["marketcap"] if "holders" in metrics else ""}

💵 Price: {metrics["price"] if "price" in metrics else ""}

👥 Holders: {metrics["holders"] if "holders" in metrics else ""}

🧑‍🏫 Description: {tk["description"] if "description" in tk else ""}
"""

def get_nft_offer_info(offer_id: str) -> dict:
    """return information about an nft offer"""
    response = requests.get(f'https://api.xrpldata.com/api/v1/xls20-nfts/offer/id/{offer_id}').json()
    if "data" in response and isinstance(response["data"]["offer"], dict):
        offer = response["data"]["offer"]
        return f"""
        ℹ️ Information about the NFT offer: {offer_id}

👤🫳 Owner: {offer["owner"]}

🖼️📇 Nftoken ID: {offer["NFTokenID"]}

👤🫴 Destination: {offer["Destination"] if "Destination" in offer else ""}

🪙🫳 For Token: {"XRP" if isinstance(offer["Amount"], str) else validate_hex_to_symbol(offer["Amount"]["currency"])}

👤 Issuer: {"" if isinstance(offer["Amount"], str) else offer["Amount"]["issuer"]}

💰🫳 For Amount: {str(drops_to_xrp(offer["Amount"])) if isinstance(offer["Amount"], str) else offer["Amount"]["value"]}

📇 Index: {offer["OfferID"]}

🏴 Flags: {offer["Flags"]}

💀 Expiry Date:  {str(ripple_time_to_datetime(offer["Expiration"])) if "Expiration" in offer and offer["Expiration"] != None else ""}       
"""

def get_offer_info(client:JsonRpcClient, offer_id: str):
    query = LedgerEntry(ledger_index="validated", offer=offer_id)
    result = client.request(query).result
    if "node" in result:
        return f"""
        ℹ️ Information about the offer: {offer_id}

👤🫳 Creator: {result["node"]["Account"]}

🖇️ Sequence: {result["node"]["Sequence"]}

📇 Index: {result["index"]}

🪙🫳 Buy Token: {"XRP" if isinstance(result["node"]["TakerPays"], str) else validate_hex_to_symbol(result["node"]["TakerPays"]["currency"])}

👤 Issuer: {"" if isinstance(result["node"]["TakerPays"], str) else result["node"]["TakerPays"]["issuer"]}

💰🫳 Buy Amount: {str(drops_to_xrp(result["node"]["TakerPays"])) if isinstance(result["node"]["TakerPays"], str) else result["node"]["TakerPays"]["value"]}

🪙🫴 Sell Token: {"XRP" if isinstance(result["node"]["TakerGets"], str) else validate_hex_to_symbol(result["node"]["TakerGets"]["currency"])}

👤 Issuer: {"" if isinstance(result["node"]["TakerGets"], str) else result["node"]["TakerGets"]["issuer"]}

💰🫴Sell Amount: {str(drops_to_xrp(result["node"]["TakerGets"])) if isinstance(result["node"]["TakerGets"], str) else result["node"]["TakerPays"]["value"]}

💀 Expiry Date: {str(ripple_time_to_datetime(result["node"]["Expiration"])) if "Expiration" in result["node"] else "Doesn't Expire"}
"""

def get_xrp_escrow_info(client: JsonRpcClient, escrow_id: str):
    """returns information about an escrow"""
    query = LedgerEntry(ledger_index="validated", escrow=escrow_id)
    result = client.request(query).result
    if "Account" in result["node"] and isinstance(result["node"]["Amount"], str):
        return f"""
        ℹ️ Information about the escrow: {escrow_id}

👤🫳 Sender: {result["index"]}

🪙 Token: {str(drops_to_xrp(result["node"]["Amount"]))}

👤🫴 Receiver: {result["node"]["Destination"]}

📇 Index: {result["index"]}

⏮️ PreviousTxnID: {result["node"]["PreviousTxnID"] if "PreviousTxnID" in result["node"] else ""}

💀 Expiry Date: {str(ripple_time_to_datetime(result["node"]["CancelAfter"])) if "CancelAfter" in result["node"] else "Doesn't Expire"}

📅 Redeem Date: {str(ripple_time_to_datetime(result["node"]["FinishAfter"])) if "FinishAfter" in result["node"] else "No time for redemption"}

💁‍♂️ Condition: {result["node"]["Condition"] if "Condition" in result["node"] else "No condition is required to finish this escrow"}
"""

def get_check_info(client:JsonRpcClient, check_id: str):
    """returns information on a check"""
    query = LedgerEntry(ledger_index="validated", check=check_id)
    result = client.request(query).result
    if "Account" in result["node"]:
        return f"""
        ℹ️ Information about the check: {check_id}

👤🫳 Sender: {result["node"]["Account"]}

🪙 Token: {"XRP" if isinstance(result["node"]["SendMax"], str) else validate_hex_to_symbol(result["node"]["SendMax"]["currency"])}

💰 Amount: {str(drops_to_xrp(result["node"]["SendMax"])) if isinstance(result["node"]["SendMax"], str) else result["node"]["SendMax"]["value"]}

👤 Issuer: {"" if isinstance(result["node"]["SendMax"], str) else result["node"]["SendMax"]["issuer"]}

👤🫴 Receiver: {result["node"]["Destination"]}

🖇️ Sequence: {result["node"]["Sequence"]}

📇 Index: {result["index"]}

💀 Expiry Date: {result["node"]["Expiration"] if "Expiration" in result["node"] else "Doesn't Expire"}          
"""
