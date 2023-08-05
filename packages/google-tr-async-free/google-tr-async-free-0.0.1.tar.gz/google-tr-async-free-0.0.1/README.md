# google-tr-async-free

Google translate for free -- local cache and throttling (averag 1.5 calls/s, first 1000 calls exempted).. Let's hope it lasts.

### Installation

```pip install google-tr-async-free```

or

* Install (pip or whatever) necessary requirements, e.g. ```
pip install requests_cache js2py``` or ```
pip install -r requirements.txt```
* Drop the file google_tr.py in any folder in your PYTHONPATH (check with import sys; print(sys.path)
* or clone the repo (e.g., ```git clone https://github.com/ffreemt/google-tr-async-free.git``` or download https://github.com/ffreemt/google-tr-async-free/archive/master.zip and unzip) and change to the google-tr-free folder and do a ```
python setup.py develop```

### Usage

```
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
arun = lambda x: loop.run_until_complete(x)

from google_tr_async import google_tr_async
_ = [google_tr_async('hello world'),
  google_tr_async('hello world', to_lang='de'),
  google_tr_async('hello world', to_lang='fr'),
  google_tr_async('hello world', to_lang='ja')]
res = arun(asyncio.gather(*_))

print(res[0])  # ->'你好，世界'
print(res[1])  # ->'Hallo Welt'
print(res[2])  # ->'Bonjour le monde'
print(res[3])  # ->'こんにちは世界'
```

### Acknowledgments

* Thanks to everyone whose code was used
