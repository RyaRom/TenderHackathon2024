import os

import asyncio
import httpx
import json
import csv

base_url = "https://zakupki.mos.ru/newapi/api/Auction/Get?auctionId="


async def download_file(file_id, file_name, auction_folder):
    print("downloading")
    file_url = f"https://zakupki.mos.ru/newapi/api/FileStorage/Download?id={file_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(file_url)

    if response.status_code == 200:
        file_path = os.path.join(auction_folder, file_name.replace(" ",""))
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"[INFO]: File {file_name} saved in folder {auction_folder}.")
    else:
        print(f"[ERROR]: Failed to download file {file_name}. Status code: {response.status_code}")


def flatten_json(nested_json, prefix=''):
    flat_dict = {}
    for key, value in nested_json.items():
        new_key = f"{prefix}{key}" if prefix == '' else f"{prefix}-{key}"
        if value is None:
            continue

        if isinstance(value, dict):
            flat_dict.update(flatten_json(value, new_key))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                flat_dict.update(flatten_json(item, f"{new_key}-{i}"))
        else:
            flat_dict[new_key] = value
    return flat_dict

def download_json(json_data, auction_folder, auction_id):
    path = os.path.join(auction_folder, f"response_{auction_id}.json")
    with open(path, mode='w', encoding='utf-8') as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)
    print(f"[INFO]: Data for auction {auction_id} saved as CSV in {auction_folder}.")


async def process_auction_page(auction_id):
    print(f"[INFO]: Processing auction with ID {auction_id}")
    auction_url = f"{base_url}{auction_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(auction_url)

    if response.status_code == 200:
        try:
            data = response.json()
            files = data.get("files", [])
            auction_folder = os.path.join("downloaded_files", str(auction_id))
            if not os.path.exists(auction_folder):
                os.makedirs(auction_folder)

            for file in files:
                await download_file(file["id"], file["name"], auction_folder)

            flattened_data = flatten_json(data)
            # json_to_csv(flattened_data, auction_folder, auction_id)
            download_json(flattened_data, auction_folder, auction_id)

        except json.JSONDecodeError:
            print(f"[ERROR]: Invalid answer from auction {auction_id}. The response is not valid JSON.")
    else:
        print(f"[ERROR]: Failed to fetch data for auction {auction_id}. Status code: {response.status_code}")

#
# async def main():
#     # may be modified for async parsing
#     await process_auction_page(9869986)
#     # for i in range(50849, 9281689):
#     #     await process_auction_page(i)
#     # print("[INFO]: Processing completed.")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
