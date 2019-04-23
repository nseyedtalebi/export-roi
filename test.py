import sys

import omero
from omero.gateway import BlitzGateway

conn = BlitzGateway('root','omero-root-password',host='192.168.1.22')
if not conn.connect():
	sys.exit(1)

for project in conn.listProjects():
	for dataset in project.listChildren():
		for image in dataset.listChildren():
			if image.getROICount() > 0:
				print "Found ROIs for image %s" % image.getName()
				roi_service = conn.getRoiService()
				result = roi_service.findByImage(image.getId(), None)
				for roi in result.rois:
					for s in roi.copyShapes():
						#prints way too much info
						#print roi_service.getPoints(s.getId().getValue())