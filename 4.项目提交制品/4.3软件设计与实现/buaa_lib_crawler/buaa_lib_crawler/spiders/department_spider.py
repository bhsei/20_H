import json

import scrapy

from buaa_lib_crawler.items import Department


class DepartmentSpider(scrapy.Spider):
    """院系列表爬虫"""

    name = 'department'

    def start_requests(self):
        yield scrapy.FormRequest('http://ir.lib.buaa.edu.cn/Scholar/LoadDepartmentTree',
                                 formdata={'order': '0'}, callback=self.parse)

    def parse(self, response):
        departments = json.loads(response.text)
        for d in departments:
            if d['id'] > 0:
                yield Department(id=d['id'], name=d['title'])
