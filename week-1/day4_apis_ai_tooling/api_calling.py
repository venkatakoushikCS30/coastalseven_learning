import requests

base_url = "https://jsonplaceholder.typicode.com/users"

# ======================================================
# 1. GET REQUEST (Read data)
# ======================================================
print("\n================ GET REQUEST ================\n")

try:
    response = requests.get(base_url, timeout=5)
    response.raise_for_status()

    data = response.json()

    print("Status Code:", response.status_code)
    print("First User Name:", data[0]["name"])

except requests.exceptions.RequestException as e:
    print("GET Error:", e)


# ======================================================
# 2. POST REQUEST (Create new data)
# ======================================================
print("\n================ POST REQUEST ================\n")

new_user = {
    "name": "Bunny",
    "email": "bunny@example.com",
    "address": {
        "city": "Andhra Pradesh"
    }
}

try:
    response = requests.post(base_url, json=new_user, timeout=5)
    response.raise_for_status()

    print("Status Code:", response.status_code)
    print("Created User Response:", response.json())

except requests.exceptions.RequestException as e:
    print("POST Error:", e)


# ======================================================
# 3. PUT REQUEST (Replace full data)
# ======================================================
print("\n================ PUT REQUEST ================\n")

updated_user = {
    "name": "Bunny Updated",
    "email": "updated@example.com",
    "address": {
        "city": "Hyderabad"
    }
}

try:
    response = requests.put(base_url + "/1", json=updated_user, timeout=5)
    response.raise_for_status()

    print("Status Code:", response.status_code)
    print("Updated User:", response.json())

except requests.exceptions.RequestException as e:
    print("PUT Error:", e)


# ======================================================
# 4. PATCH REQUEST (Partial update)
# ======================================================
print("\n================ PATCH REQUEST ================\n")

patch_data = {
    "email": "patched@example.com"
}

try:
    response = requests.patch(base_url + "/1", json=patch_data, timeout=5)
    response.raise_for_status()

    print("Status Code:", response.status_code)
    print("Patched User:", response.json())

except requests.exceptions.RequestException as e:
    print("PATCH Error:", e)


# ======================================================
# 5. DELETE REQUEST (Remove data)
# ======================================================
print("\n================ DELETE REQUEST ================\n")

try:
    response = requests.delete(base_url + "/1", timeout=5)

    print("Status Code:", response.status_code)

    if response.status_code == 200 or response.status_code == 204:
        print("User deleted successfully (fake API simulation)")

except requests.exceptions.RequestException as e:
    print("DELETE Error:", e)