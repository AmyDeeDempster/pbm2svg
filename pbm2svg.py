#!/usr/bin/env python3

import svgwrite
import sys
MAGNIFY = 5

def main():
	# See if we want to invert the black and white pixels.
	inv_flag = "-i"
	try:
		pos = sys.argv.index(inv_flag)
		del sys.argv[pos]
		invert = True
	except ValueError:
		invert = False

	# Get the input and output filenames.
	try:
		in_file_n = sys.argv[1]
	except IndexError:
		print("Need input file.")
		exit()
	try:
		out_file_n = sys.argv[2]
	except IndexError:
		print("No outfile file specified. Will add ‘.svg’ to input file.")
		out_file_n = in_file_n + ".svg"

	# Parse that input file.
	bitmap = Bitmap(in_file_n)

	# Now the long process of drawing the SVG.
	vector = svgwrite.Drawing(filename=out_file_n)
	vector.viewbox(width = bitmap.width * MAGNIFY, height = bitmap.height * MAGNIFY)

	style = """

	rect {
		fill: white;
	}
	path, ellipse {
		stroke-width: 0.5px;
		stroke: black;
		stroke-linecap: round;
		stroke-linejoin: bevel;
	}

	#b0 rect {
		fill: black;
	}	
	#b0 ellipse {
		stroke: white;
		fill: none;
	}	
	#b0 path {
		stroke-width: 0.2px;
		stroke: white;
	}
	"""	

	vector.defs.add(
		vector.style(style)
	)

	zero = vector.g(id="b0")
	one  = vector.g(id="b1")
	square = vector.rect(
		insert=(dup(0)),
		size=(dup(5)),
	)

	zero.add(square)
	zero.add(
		vector.ellipse(
			# An oval to represent a zero.
			center=(dup(MAGNIFY / 2)),
			r=(0.9, 1.3),
		)
	)
	zero.add(
		vector.path(
			# A path to draw a line through the zero.
			d="M3.75,1.25 l-2.5,2.5"
		)
	)

	one.add(square)
	one.add(
		vector.path(
			# A path that looks like ‘1’.
			d="M2.5,1 l-0.5,0.5 M2.5,1 v3",
		)
	)

	vector.defs.add(one)
	vector.defs.add(zero)

	# vector.add(
	# 	vector.rect(size=(dup("100%")))
	# )

	digits = ("#b0", "#b1")
	if invert:
		print("Inverting black and white pixels, as requested.")
		digits = digits[::-1]

	# Add the actual 0 and 1 images to the SVG.
	for y in range(bitmap.height):
		for x in range(bitmap.width):
			bit = bitmap.matrix[y][x]
			href = digits[bit]
			vector.add(
				vector.use(
					href,
					insert=(x * MAGNIFY, y * MAGNIFY),
				)
			)

	# We’ve finished.
	vector.save()
	print("%d×%d output saved as %s" % (bitmap.width, bitmap.height, out_file_n))


class Bitmap:
	def __init__(self, in_file_n):
		mirror = False
		with open(in_file_n) as in_file_h:
			dims = False
			bit_list = list()
			for line in in_file_h.readlines():
				if "P" in line or "#" in line:
					if "mirror" in line:
						print("Input file contains instruction to mirror it left-right.")
						mirror = True
					continue
				if not dims:
					dims = line.split(" ")
					width, height = [int(n) for n in dims]
					continue
				# else:
				for bit in line:
					# We don’t care about non-nums like whitespace.
					try:
						bit_list.append(int(bit))
					except ValueError:
						continue

		bit_matrix = list()
		current = 0
		while current < len(bit_list):
			cur_line = tuple(bit_list[current:current + width])
			if mirror:
				cur_line = cur_line + cur_line[::-1]
			bit_matrix.append(cur_line)
			current += width

		self.matrix = tuple(bit_matrix)
		self.width  = width * 2 if mirror else width
		self.height = height


def dup(single):
	return (single, single)

main()
