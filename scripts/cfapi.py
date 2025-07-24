import hashlib
import time
import random
import requests
import string
def generate_api_sig(method, params, api_key, api_secret):
        rand = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        params["apiKey"] = api_key
        params["time"] = str(int(time.time()))
        sorted_params = sorted(params.items())
        param_str = '&'.join(f"{k}={v}" for k, v in sorted_params)
        sig_str = f"{rand}/{method}?{param_str}#{api_secret}"
        hashed = hashlib.sha512(sig_str.encode()).hexdigest()
        return rand + hashed
def call_cf_api(method, params, api_key, api_secret):
        params = params.copy()
        sig = generate_api_sig(method, params, api_key, api_secret)
        params["apiKey"] = api_key
        params["time"] = str(int(time.time()))
        params["apiSig"] = sig
        response = requests.get(f"https://codeforces.com/api/{method}", params=params)
        response.raise_for_status()
        return response.json()
print(call_cf_api("blogEntry.view", {"blogEntryId": 115267, "locale": "en"}, "19a2721ed2432d02ddc7937bf7f7bc878fff35ed", "119383057ee1ddd2e2163b339ce90fd615396dbe"))