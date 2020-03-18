import math

import pymysql
import scrapy

from buaa_lib_crawler.items import Scholar


class ScholarSpider(scrapy.Spider):
    """学者列表爬虫"""

    name = 'scholar'
    page_size = 16

    def start_requests(self):
        conn = pymysql.connect(
            self.settings.get('MYSQL_HOST'),
            self.settings.get('MYSQL_USER'),
            self.settings.get('MYSQL_PASSWORD'),
            self.settings.get('MYSQL_DATABASE')
        )
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT id FROM department')
        department_ids = [r['id'] for r in cursor]
        conn.close()

        form_data = {
            'DepartmentId': None,
            'Keyword': '姓名/ORCID',
            'Order': 'FullName',
            'PageIndex': '1',
            'PageSize': str(self.page_size),
            'RecommendMember': '0'
        }
        for department_id in department_ids:
            form_data['DepartmentId'] = str(department_id)
            yield scrapy.FormRequest(
                'http://ir.lib.buaa.edu.cn/Scholar/MemberList',
                formdata=form_data, callback=self.parse,
                cb_kwargs={'department_id': department_id, 'page_index': 1}
            )

    def parse(self, response, **kwargs):
        # 解析学者列表
        scholar_lis = response.css('#scholar_detail > li')
        for scholar_li in scholar_lis:
            s = Scholar()
            s['id'] = int(scholar_li.css('div.scholar_pic > a::attr(href)').re_first('/(\\d+)$'))
            s['name'] = scholar_li.css('div.card_operate_name > p.card_name::text').get().strip()
            s['department_id'] = kwargs['department_id']
            s['title'] = scholar_li.css('div.card_operate_name > p.partment > span::text').get()
            s['laboratory'] = scholar_li.css('div.partment::text').get().strip()
            yield s

        # 跟踪后续分页链接
        if kwargs['page_index'] == 1:
            total_num = int(response.css('#spTotal::text').get())
            page_num = math.ceil(total_num / self.page_size)
            form_data = {
                'DepartmentId': str(kwargs['department_id']),
                'Keyword': '姓名/ORCID',
                'Order': 'FullName',
                'PageIndex': None,
                'PageSize': str(self.page_size),
                'RecommendMember': '0'
            }
            for i in range(2, page_num + 1):
                form_data['PageIndex'] = str(i)
                yield scrapy.FormRequest(
                    'http://ir.lib.buaa.edu.cn/Scholar/MemberList',
                    formdata=form_data, callback=self.parse,
                    cb_kwargs={'department_id': kwargs['department_id'], 'page_index': i}
                )
