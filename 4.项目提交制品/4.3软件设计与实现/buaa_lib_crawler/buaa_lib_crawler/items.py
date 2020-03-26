# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Department(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()


class Scholar(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    department_id = scrapy.Field()
    title = scrapy.Field()
    laboratory = scrapy.Field()


class Paper(scrapy.Item):
    id = scrapy.Field()
    scholar_id = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
