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
		has_images = False
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
				if image.getROICount() > 0:
					ds['images'].append(image.simpleMarshal())
					has_images = True
					thumbnails[image.id] = image.getThumbnail(size=(image.getSizeX()*0.005,image.getSizeY()*0.005))
			p['datasets'].append(ds)
		if has_images:
			projects.append(p)
	conn.close()
	return render(request, 'exportml/index.html',{'projects':projects,'thumbnails':thumbnails})

def get_roi_patches(request,image_id):
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