#!/usr/bin/env python
# -*- coding: <utf-8> -*-
#
# Quite flexible GIMP python-fu script to export layers.
# It supports all GIMP formats, depends on file save options
#
# Version 1.0
#
# Author: Lars Pontoppidan <leverpostej@gmail.com>
# Copyright (C) 2012 Lars Pontoppidan
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from gimpfu import *
import os, re
from os.path import expanduser

def dump(obj):
	print "type: "+type(obj) +"\nattributes: "+ dir(obj)

def dbg(message):
	print message


def export_layers(img, draw, path, visibility, filetype, css, csshover):

	def traverse(layer,options):
		vis = options['visibility']
		include_layer = (vis == 0 or (vis == 1 and layer.visible) or (vis == 2 and not layer.visible))
		include_group_layer = (vis == 0 or (vis == 1 and layer.visible) or (vis == 2 and not layer.visible))
		if (type(layer) == gimp.GroupLayer):
			if include_group_layer:
				for l in layer.layers:
					traverse(l,options)
		else:
			if include_layer:
				options['keepers'].append(layer)

	layers = []
	options = {
		'visibility' : visibility,
		'keepers' : layers
	}
	for layer in img.layers:
		traverse(layer,options)

	f = open(path+"/myhtml.html", "w");
	f.write("<!doctype html>\n<html>\n\t<head>\n\t\t<style>\n\t\t\t.container { position:relative; }\n\t\t\t.hoverimg { position: absolute; border: none; "+css+" }\n\t\t\t.hoverimg:hover{ "+csshover+" }\n\t\t</style>\n\t</head>\n\n\t<body>\n\t\t<div class=\"container\">\n")

	for layer in layers:
		filename = ""
		name = pdb.gimp_item_get_name(layer)

		if "@" in name:
			layernameurl = name.split("@")
			filename = layernameurl[0]+filetype
			linkname = layernameurl[1]
		else:
			filename = name+filetype
			linkname = ""

		pathfilename = path+"/"+filename
		if linkname:
			f.write("\t\t\t<a href=\""+linkname+"\" alt=\""+name+"\">")
		else:
			f.write("\t\t\t")
		f.write("<div class=\"hoverimg\" style=\"left: "+str(layer.offsets[0])+
			"px; top: "+str(layer.offsets[1])+"px; width: "+str(layer.width)+
			"px; height: "+str(layer.height)+"px; background-image: url('"+filename+"');\"></div>")
		if linkname:
			f.write("</a>\n")
		else:
			f.write("\n")

		dbg("Saving: '"+pathfilename+"'")
		pdb.gimp_file_save(img, layer, pathfilename, pathfilename)

	f.write("\t\t</div>\n\t</body>\n</html>\n")
	f.close()
register(
	"export_layers_css",
	"Export layers to CSS. Each file will be named after its layer. Name your layers filename@url to auto create a link to url.",
	"Script to export separate layers to CSS blocks",
	"Lars Pontoppidan, Headwar",
	"Lars Pontoppidan, Headwar",
	"2012, 2016",
	"E_xport layers to CSS...",
	"*",
	[
		(PF_IMAGE, "img", "Input image", None),
        (PF_DRAWABLE, "draw", "Input drawable", None),
		(PF_DIRNAME, "path", "Output directory", expanduser("~")),
        (PF_OPTION, "visibility", "Visibility", 1, ("All", "Visible", "Invisible")),
        (PF_STRING, "filetype", "File type", ".png"),
		(PF_STRING, "css", "Custom CSS", ""),
		(PF_STRING, "csshover", "Custom CSS on hover", "z-index:100; box-shadow: 0 0 16px 10px yellow;"),
	],
	[],
	export_layers,
	"<Image>/File/Save/"
)

main()
