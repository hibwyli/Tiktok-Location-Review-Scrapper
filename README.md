# TikTok POI Review Scraper
Use this because its **FREE** and  Apify charges you 1$/1000 reviews .  
Sorry but the service is just a scammer wanna keep a secret api for no reason.

## Technology
- Python 3 + `requests`
- TikTok API `https://api22-normal-c-alisg.tiktokv.com/tiktok/poi/review/get/v1` ( someone hides this for money i guess)
- Pagination via `cursor` + `has_more`, dedup by `review_id`, sort by `create_time` (newest first)

## Setup
```bash
pip install -r requirements.txt
```

## Usage
```bash
python3 tool/scrape.py 23661696389879272
# -> data/23661696389879272.json

# Custom POI
python3 tool/scrape.py <poi_id>
```

## POI ID
From place URL `https://www.tiktok.com/place/Name-<poi_id>` - number after last `-`.
Or short `https://vt.tiktok.com/ZS...` -> redirect `share_poi_id`.

## More details (dont care if you just need data)

### How the API was leaked
1. **Emulator** Pixel 7 Android 14 (KVM, 4GB/6c) with TikTok `com.ss.android.ugc.trill`, CA `c8750f0d.0` pushed to `/system/etc/security/cacerts` (via `adb root` + `remount` on `google_apis` image, PlayStore image is production and cannot `adb root`)
2. **mitmdump** `mitmdump --listen-port 8080 -s tiktok_addon.py` + emulator `http_proxy 10.0.2.2:8080` + `iptables DROP udp dpt:443` to force QUIC->TCP, log `api22-normal-c-alisg.tiktokv.com/tiktok/poi/review/get/v1?poi_id=...`
3. **Frida libsscronet bypass** TikTok uses Cronet `libsscronet.so` for `poi/review` so `TrustManagerImpl` hook alone not enough -> hook native `SSL_CTX_set_custom_verify` in `libsscronet.so` via Frida (`tiktok_specific.js` wait for `libsscronet` then `Interceptor.replace` callback return 0). Without this `Client TLS handshake failed ... does not trust proxy` for `tiktokv.com`.

After bypass `200 OK` with `reviews[]`, `cursor`, `has_more`. Simplified Chrome UA `https://api22-normal-c-alisg.tiktokv.com/tiktok/poi/review/get/v1?poi_id=23661696389879272&scene=7&count=20&cursor=60` works without `x-argus` (tested via `curl -A Mozilla/5.0`), so final scraper uses plain `requests` + pagination `cursor`/`has_more` + dedup `review_id`.
