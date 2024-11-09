import os
import requests
import json
import csv
from time import sleep

base_url = "https://zakupki.mos.ru/newapi/api/Auction/Get?auctionId="


def download_file(file_id, file_name, auction_folder):
    file_url = f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={file_id}"
    response = requests.get(file_url)

    if response.status_code == 200:
        file_path = os.path.join(auction_folder, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"[INFO]: File {file_name} saved in folder {auction_folder}.")
    else:
        print(f"[ERROR]: Failed to download file {file_name}. Status code: {response.status_code}")


def flatten_json(nested_json, prefix=''):
    flat_dict = {}
    for key, value in nested_json.items():
        new_key = f"{prefix}{key}" if prefix == '' else f"{prefix}-{key}"

        if isinstance(value, dict):
            flat_dict.update(flatten_json(value, new_key))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                flat_dict.update(flatten_json(item, f"{new_key}-{i}"))
        else:
            flat_dict[new_key] = value
    return flat_dict


def json_to_csv(json_data, auction_folder, auction_id):
    output_csv = os.path.join(auction_folder, f"response_{auction_id}.csv")
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=json_data.keys())
        writer.writeheader()
        writer.writerow(json_data)
    print(f"[INFO]: Data for auction {auction_id} saved as CSV in {auction_folder}.")


def process_auction_page(auction_id):
    auction_url = f"{base_url}{auction_id}"
    response = requests.get(auction_url)

    if response.status_code == 200:
        try:
            data = response.json()
            files = data.get("files", [])
            auction_folder = os.path.join("downloaded_files", str(auction_id))
            if not os.path.exists(auction_folder):
                os.makedirs(auction_folder)

            for file in files:
                download_file(file["id"], file["name"], auction_folder)

            # Преобразуем данные в "плоский" формат и сохраняем в CSV
            flattened_data = flatten_json(data)
            json_to_csv(flattened_data, auction_folder, auction_id)

        except json.JSONDecodeError:
            print(f"[ERROR]: Invalid answer from auction {auction_id}. The response is not valid JSON.")
    else:
        print(f"[ERROR]: Failed to fetch data for auction {auction_id}. Status code: {response.status_code}")


if __name__ == "__main__":
    for auction_id in range(50849, 9281689):
        print(f"[INFO]: Processing auction with ID {auction_id}")
        process_auction_page(auction_id)
        # sleep(1)

    print("[INFO]: Processing completed.")