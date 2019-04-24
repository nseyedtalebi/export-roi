# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseServerError
from django.shortcuts import render
from django.http import HttpResponse
import omero
from omero.gateway import BlitzGateway

import img_from_roi

def index(request):
	conn = BlitzGateway('root','omero-root-password',host='192.168.1.22')
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
	#roi_service = conn.getRoiService()
	#result = roi_service.findByImage(long(image_id), None)
	#for roi in result.rois:
	#	for s in roi.copyShapes():
	#		#prints way too much info, would be good for ragged shapes
	#		#print roi_service.getPoints(s.getId().getValue())
	#		#print s
	#		#For now, just get rectangle working
	#		if type(s) == omero.model.RectangleI:
	#			print("Hey!")'''
	#rois = [result.rois]
	parameterMap = {'Data_Type':'Image',
	'IDs':[long(image_id)],
	'New_Dataset':True,
	'New_Dataset_Name':'ROI_images',
	'Entire_Stack':False
	}
	return HttpResponse(img_from_roi.makeImagesFromRois(conn,parameterMap))