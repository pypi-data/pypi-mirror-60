import sys
import os
import numpy as np
import scipy
import argparse
import json
import jsbeautifier
import subprocess

def get_dimension(a_str):
	ll = a_str.split(" ")
	for i in range(len(ll)):
		if ll[i]=="TIFF" or ll[i]=="TIF":
			this_field = ll[i+1].split("x")
			dim1, dim2 = this_field
			dim1 = int(dim1)
			dim2 = int(dim2)
			return dim1, dim2
	return -1, -1

def dirname(a_path):
	dirname = os.path.dirname(a_path)
	if dirname=="":
		dirname = "."
	return dirname

def main():
	parser = argparse.ArgumentParser(description="giotto_step1_modify_json.py", formatter_class=argparse.ArgumentDefaultsHelpFormatter)

	parser.add_argument("--input", dest="input_json", type=str, required=True)
	parser.add_argument("--add-image", dest="add_image", type=str, required=False)
	parser.add_argument("--change-positions", dest="positions", type=int, nargs="+", required=False)
	parser.add_argument("--change-stain-ids", dest="stainids", type=int, nargs="+", required=False)
	parser.add_argument("--change-offset", dest="offset", type=str, required=False)
	parser.add_argument("--change-segmentation", dest="segmentation", type=str, required=False)
	parser.add_argument("--rotate-clockwise-image", dest="rotate", type=int, choices=[90, 180, 270], required=False)
	parser.add_argument("--scale-image", dest="scale", type=float, nargs="+", required=False)
	parser.add_argument("--flip-image", dest="scale", type=str, choices=["horizontal", "vertical"], required=False)
	parser.add_argument("--output", dest="output_json", type=str, required=True)

	args = parser.parse_args()

	f = open(args.input_json)
	this_json = json.load(f)
	f.close()

	if args.positions is not None:
		this_json["positions"] = args.positions
		for k in this_json:
			if k.startswith("new_task_"):
				if "positions" in this_json[k]:
					this_json[k]["positions"] = this_json["positions"]
	
		
	if args.stainids is not None:
		this_json["stain_ids"] = args.stainids
		for k in this_json:
			if k.startswith("new_task_"):
				if "stain_ids" in this_json[k]:
					this_json[k]["stain_ids"] = this_json["stain_ids"]

	ac = {}
	for k in this_json:
		if k.startswith("new_task_"):
			ac[this_json[k]["task"]] = k

	if args.offset is not None:
		for t_field in ["stitch_image", "stitch_coord", "stitch_segmentation_roi"]:
			if t_field in ac:
				this_json[ac[t_field]]["offset"] = args.offset

	if args.segmentation is not None:
		if "extract_roi_zip" in ac:
			this_json[ac["extract_roi_zip"]]["input"] = args.segmentation


	is_multi_fov = False
	if len(this_json["positions"])==1:
		is_multi_fov = False
	else:
		is_multi_fov = True

	if args.add_image is not None:

		if not is_multi_fov:
			proc = subprocess.Popen(["identify", args.add_image], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			print("Command: identify %s" % args.add_image)
			(out, err) = proc.communicate()
			print("program output:", out)
			dim1, dim2 = get_dimension(str(out))
			max_dim = max(dim1, dim2)
			new_image = dirname(args.add_image) + "/" + "extent_" + os.path.basename(args.add_image)
			if dim1==dim2:
				print("Correct dimension for image. No need to pad.")
				this_json[ac["decouple_tiff"]]["input"] = args.add_image
			else:
				proc = subprocess.Popen(["convert", args.add_image, "-background", "black", "-extent", \
				"%dx%d" % (max_dim, max_dim), new_image], stdout=subprocess.PIPE)
				print("Command: convert %s -background black -extent %dx%d %s" % (args.add_image, max_dim, \
				max_dim, new_image))
				(out, err) = proc.communicate()
				this_json[ac["decouple_tiff"]]["input"] = new_image
			this_json["tiff_width"] = max_dim
			this_json["tiff_height"] = max_dim
		else:
			a_pos = this_json["positions"] #array of positions
			max_dim = 0
			for a in a_pos:
				t_image = args.add_image.replace("[POSITION]", "%d" % a)
				proc = subprocess.Popen(["identify", t_image], stdout=subprocess.PIPE)
				print("Command: identify %s" % t_image)
				(out, err) = proc.communicate()
				dim1, dim2 = get_dimension(str(out))
				max_dim = max(dim1, dim2)
				new_image = dirname(t_image) + "/" + "extent_" + os.path.basename(t_image)
				if dim1==dim2:
					print("Correct dimension for image. No need to pad.")
					this_json[ac["decouple_tiff"]]["input"] = dirname(args.add_image) + "/" + os.path.basename(args.add_image)
				else:
					proc = subprocess.Popen(["convert", t_image, "-background", "black", "-extent", \
					"%dx%d" % (max_dim, max_dim), new_image], stdout=subprocess.PIPE)
					print("Command: convert %s -background black -extent %dx%d %s" % (t_image, max_dim, \
					max_dim, new_image))
					(out, err) = proc.communicate()
					this_json[ac["decouple_tiff"]]["input"] = dirname(args.add_image) + "/" + "extent_" + os.path.basename(args.add_image)
			this_json["tiff_width"] = max_dim
			this_json["tiff_height"] = max_dim
					
	fw = open(args.output_json, "w")
	fw.write(jsbeautifier.beautify(json.dumps(this_json)))
	fw.close()

if __name__=="__main__":
	main()	
