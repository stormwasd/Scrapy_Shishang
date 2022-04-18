"""
@Description :
@File        : grasp_fashion_huanqiu
@Project     : Scrapy_ShiShang
@Time        : 2022/4/11 18:35
@Author      : LiHouJian
@Software    : PyCharm
@issue       :
@change      :
@reason      :
"""

import scrapy
from scrapy.utils import request
from Scrapy_ShiShang.items import ScrapyShishangItem
from Scrapy_ShiShang import upload_file
from datetime import datetime
from jsonpath import jsonpath
import json


class GraspFashionHuanqiuSpider(scrapy.Spider):
    name = 'grasp_fashion_huanqiu'
    allowed_domains = ['fashion.huanqiu.com']
    # start_urls = ['http://www.chinasspp.com/']
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }

    def start_requests(self):
        for i in range(0, 1):
            url = f'https://fashion.huanqiu.com/api/list2?node=/e3pn4vu2g/e3pn4vuih&offset={i * 20}&limit=20'
            headers = {
                'authority': 'fashion.huanqiu.com',
                'pragma': 'no-cache',
                'cache-control': 'no-cache',
                'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
                'accept': '*/*',
                'x-requested-with': 'XMLHttpRequest',
                'sec-ch-ua-mobile': '?0',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'sec-fetch-dest': 'empty',
                'referer': 'https://fashion.huanqiu.com/news',
                'accept-language': 'zh-CN,zh;q=0.9',
                'cookie': 'UM_distinctid=17e285262523df-08157b5f21e45f-3b39580e-384000-17e28526253830; _ga=GA1.2.1420258345.1646375558; Hm_lvt_1fc983b4c305d209e7e05d96e713939f=1649671461; REPORT_UID_=WZpnfnflfucUlObu9jrEayimzCN4rTna; CNZZDATA1000010102=315537858-1649664515-https%253A%252F%252Fwww.baidu.com%252F%7C1649669035; Hm_lpvt_1fc983b4c305d209e7e05d96e713939f=1649673207'
            }
            req = scrapy.Request(
                url,
                callback=self.parse,
                dont_filter=True,
                headers=headers)
            yield req

    def parse(self, response):
        url_list_ids = jsonpath(json.loads(response.text), '$..aid')
        titles = jsonpath(json.loads(response.text), '$..title')
        for i in range(len(url_list_ids)):
            url = 'https://fashion.huanqiu.com/article/' + url_list_ids[i]
            req = scrapy.Request(
                url, callback=self.parse_detail, dont_filter=True)
            news_id = request.request_fingerprint(req)
            title = titles[i]
            req.meta.update({"news_id": news_id})
            req.meta.update({"title": title})
            yield req

    def parse_detail(self, response):
        news_id = response.meta['news_id']
        title = response.meta['title']
        pub_time = response.xpath(
            "//div[@class='metadata-info']/p[@class='time']/text()").extract_first().split()[0]
        source = response.xpath(
            "//div[@class='metadata-info']/p[1]/span[@class='source']/span/a/text()").extract_first()
        content = ''.join(response.xpath(
            "//div[@class='l-con clear']").extract())
        content_img = response.xpath(
            "//article/section/p/i[@class='pic-con']/img/@src").extract()
        if content_img:
            content_img_list = list()
            for index, value in enumerate(content_img):
                img_name = title + str(index)
                if value.startswith('//'):
                    res = upload_file.send_file(
                        'https:' + value, img_name, self.headers)
                else:
                    res = upload_file.send_file(value, img_name, self.headers)
                if res['msg'] == 'success':
                    content = content.replace(value, res['url'][0])
                    content_img_list.append(res['url'][0])
                else:
                    self.logger.info(f'内容图片 {value} 上传失败，返回数据：{res}')

            imgs = ','.join(content_img_list)
        else:
            imgs = None

        item = ScrapyShishangItem()
        item['news_id'] = news_id
        item['category'] = '时尚'
        item['content_url'] = response.url
        item['title'] = title
        item['issue_time'] = pub_time
        item['title_image'] = None
        item['information_source'] = '环球网-时尚资讯'
        item['content'] = content
        item['source'] = source
        item['author'] = None
        item['images'] = imgs
        item['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['cleaning_status'] = 0
        self.logger.info(item)
        yield item


if __name__ == '__main__':
    import scrapy.cmdline as cmd

    cmd.execute(['scrapy', 'crawl', 'grasp_fashion_huanqiu'])
