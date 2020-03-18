import math

import pymysql
import scrapy

from buaa_lib_crawler.items import Paper


class PaperSpider(scrapy.Spider):
    """论文列表爬虫"""

    name = 'paper'
    page_size = 20

    def start_requests(self):
        conn = pymysql.connect(
            self.settings.get('MYSQL_HOST'),
            self.settings.get('MYSQL_USER'),
            self.settings.get('MYSQL_PASSWORD'),
            self.settings.get('MYSQL_DATABASE')
        )
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT id FROM scholar')
        scholar_ids = [r['id'] for r in cursor]
        conn.close()

        form_data = {
            'currentBibType': '',
            'currentIndb': '',
            'currentYear': '',
            'currentProject': '',
            'Id': None,
            'currenLanguage': '',
            'PageIndex': '1',
            'PageSize': str(self.page_size),
            'pageType': '0',
            'pageTypeVal': '公开成果',
            'searchValue': '0'
        }
        for scholar_id in scholar_ids:
            form_data['Id'] = str(scholar_id)
            yield scrapy.FormRequest(
                'http://ir.lib.buaa.edu.cn/Scholar/SchloarAchivement',
                formdata=form_data, callback=self.parse,
                cb_kwargs={'scholar_id': scholar_id, 'page_index': 1}
            )

    def parse(self, response, **kwargs):
        # 解析论文列表
        paper_lis = response.css('body > ul > li')
        for paper_li in paper_lis:
            p = Paper()
            p['scholar_id'] = kwargs['scholar_id']
            title_tag = paper_li.css('div.num_number_right > p.num_title > a')
            p['id'] = int(title_tag.css('::attr(href)').re_first('/(\\d+)$'))
            p['title'] = title_tag.css('::text').get()
            p['author'] = paper_li.css('div.num_number_right > p.num_author::text').get()
            yield p

        # 跟踪后续分页链接
        if kwargs['page_index'] == 1:
            total_num = int(response.css('body > div.titlebar.twenty > div.title > span::text')
                            .re_first('\\d+'))
            page_num = math.ceil(total_num / self.page_size)
            form_data = {
                'currentBibType': '',
                'currentIndb': '',
                'currentYear': '',
                'currentProject': '',
                'Id': str(kwargs['scholar_id']),
                'currenLanguage': '',
                'PageIndex': None,
                'PageSize': str(self.page_size),
                'pageType': '0',
                'pageTypeVal': '公开成果',
                'searchValue': '0'
            }
            for i in range(2, page_num + 1):
                form_data['PageIndex'] = str(i)
                yield scrapy.FormRequest(
                    'http://ir.lib.buaa.edu.cn/Scholar/SchloarAchivement',
                    formdata=form_data, callback=self.parse,
                    cb_kwargs={'scholar_id': kwargs['scholar_id'], 'page_index': i}
                )
