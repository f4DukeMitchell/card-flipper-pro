from services.ebay_auth import get_ebay_access_token

if __name__ == "__main__":
    try:
        token = get_ebay_access_token()
        print("✅ Access token retrieved:")
        print(token)
    except Exception as e:
        print("❌ Failed to retrieve token:")
        print(e)
