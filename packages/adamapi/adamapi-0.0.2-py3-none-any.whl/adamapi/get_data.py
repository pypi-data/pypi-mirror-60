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


class GetData(object):
    def __init__(self,client):
        self.LOG=logger
        self.client=client

    def getData(self, product_id, time_start=None,time_end=None , geometry=None , tile=None , output_format='tif',scale=1,filter=False,output_fname=None):
        if (time_start is None and time_end is None) or product_id is None:
            self.LOG.exception("insert datasetId time_start and time_end parameters")
        params={}
        file_data=[]
        index=0
        images=[]

        start_date=datetime.strptime(time_start,'%Y-%m-%d')
        end_date=datetime.strptime(time_end,'%Y-%m-%d')
        delta=timedelta(1)
        while end_date >= start_date:
            index=0
            params={
                    'start_date':end_date.strftime("%Y-%m-%d"),
                    'end_date':end_date.strftime("%Y-%m-%d"),
                    'product':product_id,
                    'scale':scale,
                    'filter':filter
                    }

            if tile:
                if ':'in tile:
                    path,row=tile.split(':')
                    params['path']=path
                    params['row']=row
                else:
                    params['mgrs_tile']=tile

            if geometry:
                params['wkt_string']=ogr.CreateGeometryFromJson(geometry).ExportToWkt()
                response=self.client.client(os.path.join('subset','subset.json'),params,"POST")
                self.LOG.info("Get Data request executed")
            else:
                response=self.client.client(os.path.join('subset','subset.json'),params,"GET")
                self.LOG.info("Get Data request executed")

            if response.status_code != 200:
                end_date-=delta
                continue
            else:
                response=response.json()
                for(key,value)  in response.items():
                    try:
                        subset_resp=response['merge']
                    except:
                        subset_resp=response[key]

                    if output_format in ['gif','png']:
                        image_response=self.client.client(os.path.join('media','maps',subset_resp['mapserver']),{},"GET")
                    else:
                        image_response=self.client.client(os.path.join('media','maps',subset_resp['merged']),{},"GET")

                    if output_fname:
                        fname=output_fname+"_"+end_date.strftime("%Y-%m-%d")+"_"+str(index)+"."+output_format
                    else:
                        fname=str(product_id)+"_"+end_date.strftime("%Y-%m-%d")+"_"+str(index)+"."+output_format
                    index+=1
                    with open(fname,'wb') as f:
                        f.write(image_response.content)

                    file_data.append(fname)
                end_date-=delta
        if output_format=='gif':
            for image in file_data:
                images.append(imageio.imread(image))
                os.remove(image)
            if not os.path.exists("gif_image"):
                os.mkdir("gif_image")
            if output_fname:
                imageio.mimsave("gif_image/"+output_fname+".gif",images,duration=1)
            else:
                imageio.mimsave("gif_image/"+str(product_id)+".gif",images,duration=1)

        self.LOG.info("Get Data request finished and image produced")
        return file_data

    def getChart(self,product_id,time_start,time_end,latitude,longitude,output_format='json',output_fname=None):
        params={}
        values=[]
        dates=[]
        params['pid']=product_id
        params['start_date']=time_start
        params['end_date']=time_end
        params['lat']=latitude
        params['lon']=longitude
        if output_format=='json':
            params['type']='api'

        response=self.client.client(os.path.join('chart','chart.json'),params,"GET")
        serie=response.json()
        if output_format=='json':
            fname=serie
        else:
            for s in serie['serie']:
                dates.append(s[0].split("T")[0])
                values.append(s[1])

            plt.figure(figsize=(12,7))
            plt.xticks(rotation = -45)
            plt.xlabel('DATE',fontweight = 'bold', fontsize = 15)
            plt.ylabel(serie['ylabel'], fontweight = 'bold', fontsize = 15)
            plt.title(serie['label']+" from "+time_start+" to "+time_end, fontweight = 'bold', fontsize = 20,pad = 20)
            plt.plot(dates,values)
            if output_fname:
                fname=output_fname+".png"
            else:
                fname="chart_"+str(product_id)+".png"

            plt.savefig(fname)
        return fname

