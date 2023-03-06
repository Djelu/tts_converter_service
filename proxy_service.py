import http.client

from bs4 import BeautifulSoup


def get_proxy_info(proxy_count):
    conn = http.client.HTTPSConnection("hidemy.name")
    headers = {
        'cookie': "cf_clearance=76YHMKbsvXpv9UcHbjd1o1vpkF8YQ5l_ARQp66E7gGQ-1677956234-0-160; _ym_uid=167795624013051281; _ym_d=1677956240; _ym_isad=1; _gid=GA1.2.618453944.1677956240; _tt_enable_cookie=1; _ttp=Q_OcDWcpOLRAQqrS-d6hq19jN7g; PAPVisitorId=b24807e1048f03dc754c93lIzRqjh9AQ; PAPVisitorId=b24807e1048f03dc754c93lIzRqjh9AQ; _ga_KJFZ3PJZP3=GS1.1.1677959665.2.1.1677959669.0.0.0; _ga=GA1.1.252897160.1677956240",
        'authority': "hidemy.name",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        'accept-language': "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7",
        'cache-control': "max-age=0",
        'sec-ch-ua': "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Google Chrome\";v=\"110\"",
        'sec-ch-ua-mobile': "?0",
        'sec-ch-ua-platform': "Windows",
        'sec-fetch-dest': "document",
        'sec-fetch-mode': "navigate",
        'sec-fetch-site': "none",
        'sec-fetch-user': "?1",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    conn.request("GET", "/en/proxy-list/?maxtime=1000&type=hs&anon=34#list", headers=headers)

    res = conn.getresponse()
    html = res.read()
    soup = BeautifulSoup(html, "html.parser")
    proxy_table = soup.find("table")

    proxies = []
    for row in proxy_table.tbody.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 7:
            continue
        address = cells[0].text.strip()
        port = cells[1].text.strip()
        proxies.append({"address": address, "port": port})
        if len(proxies) == proxy_count:
            break
    conn.close()
    return proxies
