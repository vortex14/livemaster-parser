from typhoon.components.processor.executable.text_pipelines.base_pipeline import BasePipeline
import urllib.parse, re
from datetime import datetime
from typhoon.extensions.elogger import TyphoonLogger, ProcessorLogger, SchedulerLogger, FetcherLogger


class FirstCallback(BasePipeline):


    def get_product(self):
        response = self.response
        price = int("".join(re.findall("[0-9]+", response.doc(".price__main").text())))
        
        material = response.doc(".js-translate-item-materials").text()
        
        sales = int(re.findall("[0-9]+", response.doc(".master-info__statistics").text())[0])
        
        size = response.doc(".js-translate-item-size").remove("span").text()
        
        desc = response.doc(".js-translate-item-description").text()
        
        images = []
        
        for each in response.doc(".photo-switcher__slides a").items():
            images.append( each.attr("href") )
        
        product = {
            "url": response.url,
            "title": response.doc('title').text(),
            "price": price,
            "sales": sales,
            "material": material,
            "size": size,
            "description": desc,
            "images": images,
            "id": response.url.split("/item/")[1].split("-")[0]
        }

        return product

    async def run(self):

        if not self.response.save.get("catalog"):
            for each in self.response.doc('.item-preview__image-container').items():
                await self.crawl(each.attr.href.split("?")[0], callback=self.handler.first_group, force_update=True, save={"catalog": True})
        else:
            product = self.get_product()
            self.LOG.debug("+++++++++ SEND PRODUCT TO TR +++++++++++++++")
            await self.finish(product, force_update=True)
    