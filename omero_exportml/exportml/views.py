# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json 
import os 

from django.http import HttpResponseServerError
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import omero
from omero.gateway import BlitzGateway

import img_from_roi

def index(request):
	conn = BlitzGateway('root','omero-root-password',host=os.environ['OMEROHOST'])
	if not conn.connect():
		return HttpResponseServerError("Could not connect to Omero server")
	projects = []
	thumbnails = {}
	for project in conn.listProjects():
		can_get_rois = False
		p = {'id':project.id,
			 'name':project.name,
		     'datasets':[]
		     }
		for dataset in project.listChildren():
			ds = {'id':dataset.id,
			'name':dataset.name,
			'images':[]
			}
			for image in dataset.listChildren():
				#if image.getROICount() > 0:
				img_meta = image.simpleMarshal()
				if dataset.name != 'ROI_images' and len(img_from_roi.getRectangles(conn,image)) >0:
					img_meta['can_get_rois'] = True
				ds['images'].append(img_meta)
				size_x = image.getSizeX()
				size_y = image.getSizeY()
				if size_x*0.005 > 256:
					thumbnails[image.id] = image.getThumbnail(size=(size_x*0.005,size_y*0.005))
				else:
					thumbnails[image.id] = image.getThumbnail(size=(size_x*0.1,size_y*0.1))
			p['datasets'].append(ds)
		projects.append(p)
	conn.close()
	return render(request, 'exportml/index.html',{'projects':projects,'thumbnails':thumbnails})

def make_roi_images(request,image_id):
	conn = BlitzGateway('root','omero-root-password',host='192.168.1.22')
	if not conn.connect():
		return HttpResponseServerError("Could not connect to Omero server")
	parameterMap = {'Data_Type':'Image',
	'IDs':[long(image_id)],
	'New_Dataset':True,
	'New_Dataset_Name':'ROI_images',
	'Entire_Stack':False
	}
	msg = img_from_roi.makeImagesFromRois(conn,parameterMap)
	conn.close()
	return render(request, 'exportml/gen_roi_message.html', {'messages':msg})
	#return HttpResponse(img_from_roi.makeImagesFromRois(conn,parameterMap))


def export_rois(request,image_id):
	conn = BlitzGateway('root','omero-root-password',host=os.environ['OMEROHOST'])
	if not conn.connect():
		return HttpResponseServerError("Could not connect to Omero server")
	image = conn.getObject("Image",image_id)
	rectangles = [{'x':rectangle[0],
				   'y':rectangle[1],
				   'width':rectangle[2],
				   'height':rectangle[3],
				   'zStart':rectangle[4],
				   'zStop':rectangle[5],
				   'tStart':rectangle[6],
				   'tStop':rectangle[7],
				   } for rectangle in img_from_roi.getRectangles(conn,image)]
	img_meta = image.simpleMarshal()
	img_meta['rectangles'] = rectangles
	return JsonResponse(img_meta)