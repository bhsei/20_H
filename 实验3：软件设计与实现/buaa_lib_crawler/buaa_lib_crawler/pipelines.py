# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class SaveItemToMySQLPipeline:
    spider_name = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get('MYSQL_HOST'),
            crawler.settings.get('MYSQL_USER'),
            crawler.settings.get('MYSQL_PASSWORD'),
            crawler.settings.get('MYSQL_DATABASE')
        )

    def __init__(self, host, user, password, database):
        self.conn = pymysql.connect(host, user, password, database, charset='utf8')
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def save_item(self, item):
        raise NotImplementedError

    def process_item(self, item, spider):
        if spider.name == self.spider_name:
            self.save_item(item)
        return item

    def close_spider(self, spider):
        self.conn.close()


class DepartmentPipeline(SaveItemToMySQLPipeline):
    spider_name = 'department'

    def save_item(self, item):
        self.cursor.execute('SELECT id FROM department WHERE id=%s', item['id'])
        if not self.cursor.fetchone():
            self.cursor.execute('INSERT INTO department VALUES (%s,%s)', (item['id'], item['name']))
            self.conn.commit()


class ScholarPipeline(SaveItemToMySQLPipeline):
    spider_name = 'scholar'

    def save_item(self, item):
        self.cursor.execute('SELECT id FROM scholar WHERE id=%s', item['id'])
        if not self.cursor.fetchone():
            self.cursor.execute('INSERT INTO scholar VALUES (%s,%s,%s,%s,%s)',
                                (item['id'], item['name'], item['department_id'],
                                 item['title'], item['laboratory']))
            self.conn.commit()


class PaperPipeline(SaveItemToMySQLPipeline):
    spider_name = 'paper'

    def save_item(self, item):
        self.cursor.execute('SELECT id FROM paper WHERE id=%s', item['id'])
        if not self.cursor.fetchone():
            self.cursor.execute('INSERT INTO paper VALUES (%s,%s,%s)',
                                (item['id'], item['title'], item['author']))
        self.cursor.execute('SELECT * FROM scholar_paper WHERE scholar_id=%s AND paper_id=%s',
                            (item['scholar_id'], item['id']))
        if not self.cursor.fetchone():
            self.cursor.execute('INSERT INTO scholar_paper VALUES (%s,%s)',
                                (item['scholar_id'], item['id']))
        self.conn.commit()
