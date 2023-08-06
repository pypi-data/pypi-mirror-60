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

    def getProducts(self,product_id,**kwargs):
        params={}
        url=os.path.join('opensearch','get_search.json')
        if product_id:
            params['product']=product_id
        else:
            raise AdampyError("Insert the product id, it's required")

        for par in kwargs:
            params[par]=kwargs[par]

        if 'geometry' in kwargs:
            response=self.client.client(url,params,"POST").json()
        else:
            response=self.client.client(url,params,"GET").json()
        return response
