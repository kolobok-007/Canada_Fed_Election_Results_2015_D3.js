# -*- coding: utf-8 -*-
"""
@author: mvenkov
"""
def parse_coordinates(input_string, poly_num):
	# Parses a string of coordinates into a list of float corrdinates
	array = input_string.split(' ')
	final = []
	for a in array:
		XY = a.split(',')
		final.append([float(XY[0]),float(XY[1]),poly_num])
	return final

def parse_gml(gml_file):
	# Extracts data out of GML file and outputs a dictionary
	print 'Parsing GML file...'
	import xml.etree.ElementTree as ET
	import codecs
	from collections import defaultdict

	tree = ET.parse(gml_file)
	count=0
	num_tag = '{http://www.safe.com/gml2}FEDNUM'#gml2
	name_tag = '{http://www.safe.com/gml2}ENNAME'#gml2
	prov_tag = '{http://www.safe.com/gml2}PROVCODE'#gml2
	coor_tag = '{http://www.opengis.net/gml}coordinates'#gml

	out_dict = defaultdict(dict)
	data_row={'name':u'',
			  'prov':u'',
			  'coor':[]}

	NUM = None
	poly_num=1

	for element in tree.iter():
		# If tag for ridding code is detected that means this is a start of a new ridding or polygon
		if element.tag == num_tag:
			# Writing is done at the start of processing the next ridding. So don't write anything the very first time round.
			# Some riddings are made from two polygons. For example a main land and an island could be part of one district.
			# In case of multiple polygons they will be part of the same dictionary record with different poly_num
			if count!=0 and NUM not in out_dict.keys():		
				out_dict[NUM]=dict(data_row)
				data_row={'name':u'',
			  	'prov':u'',
			  	'coor':[]}
			  	poly_num=1

			NUM=element.text		
			count+=1
		# Prcoess the rest of the tags
		if element.tag == name_tag:
			data_row['name']=element.text
		if element.tag == prov_tag:
			data_row['prov']=element.text
		if element.tag == coor_tag:
			data_row['coor'] =data_row['coor']+ parse_coordinates(element.text, poly_num)
			poly_num+=1

	#The very last data point
	out_dict[NUM]=dict(data_row)

	print 'Finished parsing GML file'
	return out_dict

def flatten_dict(input_dict):
	# Converts dictionary into a list that can be saved a CSV file
	print 'Flattening dictionary...'
	num = None
	name = None
	prov = None
	poly_num=0
	coor = []
	output = []
	row=1
	# Full description
	# output.append(['num','name','prov','poly_num','X','Y','Path'])

	# Reduced size
	output.append(['num','prov','poly_num','X','Y','Path'])

	import pprint
	#pprint.pprint(input_dict)

	for entry in input_dict:
		num = entry
		prov = input_dict[entry]['prov']
		coor = input_dict[entry]['coor']

		for X, Y, poly_num in coor:
			# output.append([num, name, prov,poly_num, X, Y, row])
			# Reduced size:
			output.append([num,prov, poly_num, X, Y, row])
			row+=1
	print 'Finished flattening'
	return output

def to_str(table):
	# encodes a table into a str file
	name=None
	output=[]
	for row in table:
		name = row[1]
		if isinstance(name,unicode):
			row[1]=name.encode('utf-8')
		output.append(row)
	return output

if __name__=='__main__':
	import csv
	import os

	folder =os.path.dirname(os.path.realpath(__file__))+r'\\data\\'
	gml_file=folder+'FED_CA_2_2_ENG.gml'

	parsed = parse_gml(gml_file)

	# Explicitly encode to STR to avoid issues with French letters
	final = to_str(flatten_dict(parsed))

	print 'Writing to file...'
	outfile= folder + 'final.csv'
	with open(outfile,'wb') as f:
		writer = csv.writer(f)
		writer.writerows(final)

	print 'End of script'