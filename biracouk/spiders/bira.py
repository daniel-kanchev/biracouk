import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from biracouk.items import Article


class BiraSpider(scrapy.Spider):
    name = 'bira'
    start_urls = ['https://bira.co.uk/news/']

    def parse(self, response):
        articles = response.xpath('//div[@class="article-highlight"]')
        for article in articles:
            link = article.xpath('.//div[@class="article-highlight-body"]/a/@href').get()
            date = article.xpath('.//div[@class="date"]/h4/text()').get()
            author = article.xpath('.//div[@class="article-highlight-body"]/a[2]//text()').get().split()[-1]
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date, author=author))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date, author):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        if date:
            date = datetime.strptime(date.strip(), '%d.%m')
            date = date.strftime('%m/%d')

        content = response.xpath('//div[@id="fullwidth-content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('author', author)

        return item.load_item()
