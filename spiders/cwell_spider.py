import scrapy
import json
from scrapy.exporters import JsonItemExporter
import re
import string

cat_list = []

BASE_URL = "https://www.carewell.com"
PRODUCT_API_URL = "https://ock210.a.searchspring.io/api/search/search.json?resultsFormat=native&siteId=ock210&domain="



class CarewellSpider(scrapy.Spider):
    name = "carewell"
    start_urls = ["https://www.carewell.com/catalog/incontinence/"]


    def parse(self, response):
        # Extract the content of the <script> tag with id "__NEXT_DATA__"
        script_content = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()

        if script_content:
            # Use regular expressions or a JSON parser to extract the data
            match = re.search(r'({.*})', script_content)
            if match:
                json_data = match.group(1)
                data = json.loads(json_data)

                # Navigate to the product data within the JSON structure
                layout_static_props = data.get('props', {}).get('pageProps', {}).get('layoutStaticProps', {})
                category_tree = layout_static_props.get('categoryTree', [])

                catalog = self.sort_categories(category_tree)
                # print(catalog, type(catalog))


                # for each_category in cat_list:

                    # product_data_url = f"{BASE_URL}/_next/data/TmH8cIOH8SHgIJt9rqPSZ{each_category}.json?{'&'.join(['categoryPaths=' + segment for segment in each_category.split('/') if segment])}"


                    # yield scrapy.Request(product_data_url, callback=self.parse_hierarchy)
                    # yield scrapy.Request(product_data_url, callback=parse_hierarchy)

                    # item = response.meta['item']  # Get the item passed from the previous callback
                    # print(item)
                    # # additional_data = item['additional_data']
                    # # print("***************************************")
                    # # print(x)

                # Save the product data to a JSON file
                # with open('carewell_products_new.json', 'w', encoding='utf-8') as json_file:
                #     json.dump(catalog, json_file, ensure_ascii=False, indent=3)
        # Add more scraping logic if needed

        # Close the spider
        self.crawler.engine.close_spider(self, 'Crawling completed.')

    def sort_categories(self,categories, level=1, parentCategoryId=None):
        sorted_categories = []

        for category in categories:
            catalog = {
                'categoryId': category.get('entityId'),
                'categoryName': category.get('name'),
                'categoryPath': category.get('path'),
                'level':level,
                'parentCategoryId':parentCategoryId,

            }

            if category.get("children"):
                # Recursively sort the children and concatenate the results.
                sorted_children = self.sort_categories(category["children"], level + 1, catalog['categoryId'])
                catalog['subcategories'] = []
                catalog['subcategories'].extend(sorted_children)
            else:
                cat_list.append(catalog.get('categoryPath'))

                product_data_url = f"{BASE_URL}/_next/data/TmH8cIOH8SHgIJt9rqPSZ{catalog.get('categoryPath')}.json?{'&'.join(['categoryPaths=' + segment for segment in catalog.get('categoryPath').split('/') if segment])}"
                print(product_data_url)

                yield scrapy.Request(product_data_url, callback=self.parse_hierarchy)
            sorted_categories.append(catalog)
            
        # with open('carewell_products_new.json', 'w', encoding='utf-8') as json_file:
        #     json.dump(catalog, json_file, ensure_ascii=False, indent=3)
        # return sorted_categories
    
    
    def parse_hierarchy(self,response):
        hierarchy_filter = '>'.join(response.json().get('pageProps').get("categoryMatch").get("names"))
        # print(hierarchy_filter)
        products_api_call = f"{PRODUCT_API_URL}{BASE_URL}&bgfilter.categories_hierarchy={hierarchy_filter}"
        # yield {"hierarchy_filter" : hierarchy_filter}
        print(products_api_call)
        yield scrapy.Request(products_api_call, callback=self.products_fetch)
        # yield scrapy.Request(products_api_call, callback=products_fetch)

    def products_fetch(self,response):
        print(response.json().get('pagination'))







