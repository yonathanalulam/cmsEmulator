import os
import requests


def fetch_cern_data():
    url = "http://opendata.cern.ch/record/545/files/Dimuon_DoubleMu.csv"
    filename = "../Dimuon_DoubleMu.csv"

    if os.path.exists(filename):
        return filename

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return filename

    except Exception as e:
        if os.path.exists(filename):
            os.remove(filename)
        raise e


if __name__ == "__main__":
    fetch_cern_data()