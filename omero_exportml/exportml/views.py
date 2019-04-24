# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseServerError
from django.shortcuts import render
from django.http import HttpResponse
import omero
from omero.gateway import BlitzGateway

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

	return render(request, 'exportml/index.html',{'projects':projects,'thumbnails':thumbnails})