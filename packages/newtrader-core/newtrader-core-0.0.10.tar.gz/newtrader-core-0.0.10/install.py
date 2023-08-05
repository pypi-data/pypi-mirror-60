from tqdm import tqdm
import os
import requests

frequencies = ['5min', '15min', '30min', '1h', '4h', '6h', '1D', '5D', '15D', '1W', '1M', '1Y']
base_url = 'https://ewr1.vultrobjects.com/fxcm/'

bundle_name = 'ratio'

affs = ['_' + f + '.h5' for f in frequencies]
affs.append('.h5')

print('start downloading bundle files.')

for aff in affs:
    filename = bundle_name + aff
    url = base_url + filename
    # Streaming, so we can iterate over the response.

    print(f'downloading {filename}')

    if os.path.exists(os.path.join('data', 'bundle', filename)):
        print(f'{os.path.join("data", "bundle", filename)} has already exists.'
              f'If you want to download it again,please delete it manually.')
        continue

    r = requests.get(url, stream=True)
    # Total size in bytes.
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(os.path.join('data', 'bundle', filename), 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)
    t.close()
    if total_size != 0 and t.n != total_size:
        print(f"ERROR, something went wrong when downloading: {filename}")
