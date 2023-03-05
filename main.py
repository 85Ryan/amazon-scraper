import os
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup, Tag
import csv
from time import sleep
from threading import Thread


# 读取 .env 文件
load_dotenv()

# 获取 .env 文件中定义的 COOKIE 变量
COOKIE = os.environ.get("COOKIE")


# 从商品评论页面提取评价信息


def get_product_review(review_url):
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cookie': COOKIE,
    }
    response = requests.get(review_url, headers=headers)

    review_info = {}

    # 判断是否请求成功（200）
    if response.status_code == 200:
        # 解析返回内容为 BeautifulSoup 对象
        soup = BeautifulSoup(response.text, "html.parser")

        # 商品评分
        rating_tag = soup.find("span", {"data-hook": "rating-out-of-text", "class": "a-size-medium a-color-base"})
        review_info["Rating"] = rating_tag.text.split(" out")[0] if rating_tag else None

        # 商品评分数 & 评论数
        rating_counter_tag = soup.find("div", {"data-hook": "cr-filter-info-review-rating-count", "class": "a-row a-spacing-base a-size-base"})
        rating_counter = rating_counter_tag.text.strip() if rating_counter_tag else None

        if rating_counter:
            parts = str(rating_counter).split(", ")
            review_info["Ratings"] = parts[0].split(" ")[0]
            review_info["Reviews"] = parts[1].split(" ")[0]
        else:
            review_info["Ratings"] = "N/A"
            review_info["Reviews"] = "N/A"

        return review_info
    else:
        # 如果请求失败，则输出错误提示，并返回空列表
        print("页面 %s 无法提取信息，错误代码：%d"%(review_url,response.status_code))
        return {}

# 从商品详情页面中提取商品信息

def get_product_info(index, product_url):
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cookie': COOKIE,
    }
    response = requests.get(product_url, headers=headers)

    product_info = {}

    # 判断是否请求成功（200）
    if response.status_code == 200:
        # 解析返回内容为 BeautifulSoup 对象
        soup = BeautifulSoup(response.text, "html.parser")
        
        # 商品序号
        product_info["NO."] = index + 1
        
        # 商品 ASIN
        title_tag = soup.find("div", {"id": "title_feature_div"})
        product_info["ASIN"] = title_tag.get("data-csa-c-asin") if isinstance (title_tag, Tag) else None

        # 商品名称
        name_tag = soup.find("span", id="productTitle")
        product_info["Name"] = name_tag.text.strip()[:50] if name_tag else None

        # 商品销售方
        seller_tag = soup.find("div", {"class": "tabular-buybox-text", "tabular-attribute-name": "Sold by"})
        product_info["Seller"] = seller_tag.text.strip() if seller_tag else None

        # 发货方式
        shipper_tag = soup.find("div", {"class": "tabular-buybox-text", "tabular-attribute-name": "Ships from"})
        product_info["Shipper"] = shipper_tag.text.strip() if shipper_tag else None

        # 商品品牌
        brand_tag = soup.select_one("tr.a-spacing-small.po-brand td:nth-of-type(2) span")
        product_info["Brand"] = brand_tag.text.strip() if brand_tag else None

        # 商品价格
        price_tag = soup.select_one("#corePrice_feature_div span.a-offscreen")
        product_info['Price'] = price_tag.text.strip() if price_tag else None

        # 商品分类
        category_tag = soup.select('ul.a-unordered-list.a-horizontal.a-size-small > li')
        # 一级分类
        product_info["Category"] = category_tag[0].text.strip() if category_tag else None
        # 二级分类
        product_info["Secondary Category"] = category_tag[2].text.strip() if category_tag else None

        # 商品大类排名 & 商品发布日期
        detail_tables = soup.find_all("table", {"id": ["productDetails_techSpec_section_1", "productDetails_detailBullets_sections1"]})

        rows = []
        for table in detail_tables:
            rows.extend(table.find_all('tr'))

        # 初始化 BSR & DATE
        product_info["BSR"] = ''
        product_info["Published at"] = ''

        for row in rows:
            th = row.find("th")
            if th and "Best Sellers Rank" in th.text:
                rank_text = row.find("td").text.strip()
                product_info["BSR"] = rank_text.split(" in")[0].replace("#", "")
            if th and "Date First Available" in th.text:
                date_text = row.find("td").text.strip().replace("\u200e", "")
                product_info["Published at"] = date_text
        
        # 商品评论详情页面
        review_url = product_url.replace("/dp/", "/product-reviews/")
        # 获取商品评价信息
        review_info = get_product_review(review_url)

        product_info.update(review_info)

        # 商品链接
        product_info["Link"] = product_url

        return product_info
    else:
        # 如果请求失败，则输出错误提示，并返回空列表
        print("页面 %s 无法提取信息，错误代码：%d"%(product_url,response.status_code))
        return {}


# 从搜索结果列表中提取商品链接


def get_product_links(product_url):

    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.com/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cookie': COOKIE,
    }

    response = requests.get(product_url, headers=headers)

    # 判断是否请求成功（200）
    if response.status_code == 200:
        # 解析返回内容为 BeautifulSoup 对象
        soup = BeautifulSoup(response.text, 'html.parser')
        # 定义一个列表，用于存储提取的链接
        product_links = []

        # 商品位，不含广告商品
        products = soup.find_all("div", {'data-component-type': 's-search-result'})

        # 遍历每个商品，获取商品链接
        for product in products:
            link = product.h2.a['href'].split('ref=')[0]
            if link:
                product_links.append('https://www.amazon.com' + link)
        # 返回提取的链接列表
        return product_links
    else:
        # 如果请求失败，则输出错误提示，并返回空列表
        print("页面 %s 无法提取信息，错误代码：%d"%(product_url,response.status_code))
        return []



# 定义一个函数，用于将数据导出 csv 文件


def export_data(keywords, data):
    keywords = keywords.lower().replace(" ", "_")
    with open(f"exports/amazon_{keywords}_data.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)



# 主程序入口
if __name__ == '__main__':

    keywords = input("请输入搜索关键词: ")

    print(f"开始搜索 {keywords} 的商品信息...")

    # 初始化列表
    data = []
    all_product_links = []

    threads = []

    def search_page(page):
        # 搜索结果页链接
        search_url = f"https://www.amazon.com/s?k={keywords}&page={page}"
        print(f"正在搜索第 {page} 页...")
        
        product_links = get_product_links(search_url)
        all_product_links.extend(product_links)

    for page in range(1, 4):
        t = Thread(target=search_page, args=(page,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    threads.clear()

    def search_product(index, product_link):
        print(f"正在搜索 {product_link} ...")
        product_info = get_product_info(index, product_link)
        if product_info:
            data.append(product_info)
            print(f"成功获取第 {product_info['NO.']} 条信息！")
        else:
            print(f"无法获取 {product_link} 的信息！")

    for index, product_link in enumerate(all_product_links):
        t = Thread(target=search_product, args=(index, product_link))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    
    export_data(keywords, data)
    print("成功导出所有数据！")