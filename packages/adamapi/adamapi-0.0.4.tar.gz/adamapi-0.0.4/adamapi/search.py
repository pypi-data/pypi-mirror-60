"""
Copyright (c) 2020 MEEO s.r.l.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from datetime import timedelta,datetime
import os
import logging
from osgeo import gdal,ogr
from matplotlib import pyplot as plt
import imageio
import json
logger=logging.getLogger('adamapi')

from . import AdampyError

class Search():
    def __init__(self,client):
        self.LOG=logger
        self.client=client


    def getAvailableDate(self,product_id):
        if not product_id:
            raise AdampyErro("Insert the product id, it's required")
        else:
            params={}
            params['product']=product_id

        response=self.client.client(os.path.join('opensearch','image_list.json'),params,"GET")
        return response.json()

    def getAvailableTile(self,product_id,dates):
        if not product_id:
            raise AdampyError("Insert the product id, it's required")

        if not dates:
            raise AdampyError("Insert time_start, it's required")

        tile_list={}
        params={}
        params['product']=product_id
        params['api']='api'

        for date in dates:
            params['start_date']=date
            params['end_date']=date
            response=self.client.client(os.path.join('opensearch','get_tiles.json'),params,"POST").json()
            tile_list[date]=response['prop']
        return tile_list







