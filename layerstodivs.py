#!/usr/bin/env python
# -*- coding: <utf-8> -*-
#
# Quite flexible GIMP python-fu script to export layers.
# It supports all GIMP formats, depends on file save options
#
# Version 1.0
#
# Authors: Lars Pontoppidan <leverpostej@gmail.com>, headwar
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

def export_layers(img, draw, path, visibility, filetype, css, csshover, backlayer):

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

	# create the html file
	f = open(path+"/myhtml.html", "w");
	f.write("<!doctype html>\n<html>\n\t<head>\n\t\t<style>\n\t\t\t.container { position:relative; }\n\t\t\t.backimg { position: absolute; border: none; }\n\t\t\t.hoverimg { position: absolute; border: none; "+css+" }\n\t\t\t.hoverimg:hover{ "+csshover+" }\n\t\t</style>\n\t</head>\n\n\t<body>\n\t\t<div class=\"container\">\n")

	filetypes = [".png",".jpg",".gif"]
	filenames = []

	for layer in layers[::-1]:
		filename = ""
		name = pdb.gimp_item_get_name(layer)
		# if an @ is in the layer name, the part after the @ char is the link
		if "@" in name:
			layernameurl = name.split("@")
			filename = layernameurl[0]
			linkname = layernameurl[1]
		else:
			filename = name
			linkname = ""
		# for the images filenames, remove all non alphanum + .-_ chars
		filename= re.sub(r'[^.-_a-zA-Z0-9]', '', filename)
		# avoid duplicate filenames
		while filename in filenames:
			filename=filename+'0'
		filenames.append(filename)
		# add the file type
		filename=filename+filetypes[filetype]
		pathfilename = path+"/"+filename
		f.write("\t\t\t")
		# if there is a link in the layer name :
		if linkname:
			f.write("<a href=\""+linkname+"\" alt=\""+name+"\">")
		myclass = "hoverimg"
		# if the last layer (hence now the first, as the 'for' is in reverse order) is a background :
		if backlayer:
			myclass = "backimg"
			backlayer = 0

		f.write("<div class=\""+myclass+"\" style=\"left: "+str(layer.offsets[0])+
			"px; top: "+str(layer.offsets[1])+"px; width: "+str(layer.width)+
			"px; height: "+str(layer.height)+"px; background-image: url('"+filename+"');\"></div>")

		# if there is a link in the layer name :
		if linkname:
			f.write("</a>")
		f.write("\n")

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
        (PF_OPTION, "visibility", "Visibility", 1, ["All", "Visible", "Invisible"]),
        (PF_OPTION, "filetype", "File type", 0, [".png",".jpg",".gif"]),
		(PF_STRING, "css", "Custom CSS", ""),
		(PF_STRING, "csshover", "Custom CSS on hover", "z-index:100; box-shadow: 0 0 16px 10px yellow;"),
		(PF_TOGGLE, "backlayer", "The lowest layer is a background", 1)
	],
	[],
	export_layers,
	"<Image>/File/Save/"
)

main()
