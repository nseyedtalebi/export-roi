import sys

import omero
from omero.gateway import BlitzGateway

conn = BlitzGateway('root','omero-root-password',host='192.168.1.22')
if not conn.connect():
	sys.exit(1)

projects = []
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
		p['datasets'].append(ds)
	if has_images:
		projects.append(p)
for p in projects:
	print(p)
				
'''roi_service = conn.getRoiService()
				result = roi_service.findByImage(image.getId(), None)
				for roi in result.rois:
					for s in roi.copyShapes():
						#prints way too much info, would be good for ragged shapes
						#print roi_service.getPoints(s.getId().getValue())
						#print s
						#For now, just get rectangle working
						if type(s) == omero.model.RectangleI:
							print("Hey!")'''