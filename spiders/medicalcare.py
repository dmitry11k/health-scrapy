import scrapy

class MedicalcareSpider(scrapy.Spider):
    name = 'medicalcare'
    allowed_domains = ['healthpoint.co.nz']
    start_urls = ['https://www.healthpoint.co.nz/gps-accident-urgent-medical-care/']

    # custom_settings = {'FEED_URI': "parse_%(time)s.csv",
    #                     'FEED_FORMAT': 'csv'}

    def parse(self, response):
        for region_href in response.css('.result-list ul.basic-list>li>a::attr("href")'):
            urlr = response.urljoin(region_href.extract())
            yield scrapy.Request(urlr, callback=self.parse_region, dont_filter=True)

    def parse_region(self, response):
        for href in response.css("#paginator-services h4>a::attr('href')"):
            url = response.urljoin(href.extract())
            next_page = response.css('#paginator-services .pagination>.next::attr("href")').extract_first()
            yield scrapy.Request(url, callback=self.parse_clinic_contents, dont_filter=True)
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse_region)

    def parse_clinic_contents(self, response):
        address = response.css('div[itemprop=address]>p').extract()
        if not address:
            street_address = None
        else:
            street_address = address[0].replace('<br>', ' ').replace('</br>', ' ').replace('</p>', '').replace('<p>', '')
        yield {'Region': response.css('.service-location>p ::text').get(),
               'Clinic': response.css('.section-heading>h1 ::text').get(),
               'Phone': response.css('.contact-list p[itemprop=telephone] ::text').get(),
               'E-mail': response.css('.contact-list a[href^="mailto:"] ::text').get(),
               'Web-site': response.css('.contact-list a[itemprop=url] ::text').get(),
               'Street address': street_address,
               'Practitioner count': len(response.css('li.person')) }

