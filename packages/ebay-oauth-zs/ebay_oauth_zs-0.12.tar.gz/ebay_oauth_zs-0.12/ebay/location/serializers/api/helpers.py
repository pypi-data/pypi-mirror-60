import pandas as pd
from ebay.location.serializers.api.feed import EbayLocationFlatSerializer


def nested_location_to_flat(ebay_location_data):
    location_data = ebay_location_data.pop("location")
    address_data = location_data.pop("address")
    address_data["countryCode"] = address_data.pop("country")

    if not ebay_location_data.get("name", None):
        ebay_location_data["name"] = ebay_location_data["merchantLocationKey"]

    ebay_location_data.update(**address_data)
    return ebay_location_data


def feed_to_dict_list(file_path):
    df = pd.read_csv(file_path)
    return [row.to_dict() for row_num, row in df.iterrows()]


def dict_list_to_ebay_locations(dict_list, marketplace_user_account):
    for data in dict_list:
        data.update({"marketplace_user_account": marketplace_user_account.id})
        serializer = EbayLocationFlatSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)


def feed_to_ebay_locations(file_path, marketplace_user_account):
    dict_list = feed_to_dict_list(file_path)
    dict_list_to_ebay_locations(dict_list, marketplace_user_account)


def ebay_locations_to_feed(qs, file_path=None):
    df_dict = {}
    for location in qs:
        data = EbayLocationFlatSerializer(location).data
        for key, value in data.items():
            if key in df_dict.keys():
                df_dict[key].append(value)
            else:
                df_dict[key] = [value]
    df = pd.DataFrame.from_dict(df_dict)
    if file_path:
        df.to_csv(file_path, index=None)
    return df
