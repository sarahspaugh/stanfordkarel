from karel.kareldefinitions import * 
import tkinter as tk
import cmath


class KarelCanvas(tk.Canvas):
	def __init__(self, width, height, master, world=None, karel=None, bg="white"):
		super().__init__(master, width=width, height=height, bg=bg)
		self.world = world
		self.karel = karel
		self.icon = DEFAULT_ICON
		self.draw_world()
		self.draw_karel()

	def set_icon(self, icon):
		self.icon = icon

	def redraw_all(self):
		self.delete("all")
		self.draw_world()
		self.draw_karel()
		self.update()

	def redraw_karel(self):
		self.delete("karel")
		self.draw_karel()
		self.update()

	def redraw_beepers(self):
		self.delete("beeper")
		self.draw_all_beepers()
		self.update()

	def redraw_corners(self):
		self.delete("corner")
		self.draw_corners()
		self.update()

	def draw_world(self):
		self.init_geometry_values()
		self.draw_bounding_rectangle()
		self.label_axes()
		self.draw_corners()
		self.draw_all_beepers()
		self.draw_all_walls()

	def init_geometry_values(self):
		self.update()

		# Calculate the maximum possible cell size in both directions
		# We will use the smaller of the two as the bounding cell size
		horizontal_cell_size = (self.winfo_width() - 2 * BORDER_OFFSET) / self.world.num_avenues
		vertical_cell_size = (self.winfo_height() - 2 * BORDER_OFFSET) / self.world.num_streets

		# Save this as an instance variable for later use
		self.cell_size = min(horizontal_cell_size, vertical_cell_size)

		self.boundary_height = self.cell_size * self.world.num_streets
		self.boundary_width = self.cell_size * self.world.num_avenues

		# Save all these as instance variables as well
		self.left_x = self.winfo_width() / 2 - self.boundary_width / 2
		self.top_y = self.winfo_height() / 2 - self.boundary_height / 2
		self.right_x = self.left_x + self.boundary_width
		self.bottom_y = self.top_y + self.boundary_height

	def draw_bounding_rectangle(self):
		# Draw the external bounding lines of Karel's world
		self.create_line(self.left_x, self.top_y, self.right_x, self.top_y, width=LINE_WIDTH)
		self.create_line(self.left_x, self.top_y, self.left_x, self.bottom_y, width=LINE_WIDTH)
		self.create_line(self.right_x, self.top_y, self.right_x, self.bottom_y, width=LINE_WIDTH)
		self.create_line(self.left_x, self.bottom_y, self.right_x, self.bottom_y, width=LINE_WIDTH)

	def label_axes(self):
		# Label the avenue axes
		for avenue in range(1, self.world.num_avenues + 1):
			label_x = self.calculate_corner_x(avenue)
			label_y = self.bottom_y + LABEL_OFFSET
			self.create_text(label_x, label_y, text=str(avenue), font="Arial 10")
		
		# Label the street axes
		for street in range(1, self.world.num_streets + 1):
			label_x = self.left_x - LABEL_OFFSET
			label_y = self.calculate_corner_y(street)
			self.create_text(label_x, label_y, text=str(street), font="Arial 10")

	def draw_corners(self):
		# Draw all corner markers in the world 
		for avenue in range(1, self.world.num_avenues + 1):
			for street in range(1, self.world.num_streets + 1):
				color = self.world.corner_color(avenue, street)
				corner_x = self.calculate_corner_x(avenue)
				corner_y = self.calculate_corner_y(street)
				if not color:
					self.create_line(corner_x, corner_y - CORNER_SIZE, corner_x, corner_y + CORNER_SIZE, tag="corner")
					self.create_line(corner_x - CORNER_SIZE, corner_y, corner_x + CORNER_SIZE, corner_y, tag="corner")
				else:
					self.create_rectangle(corner_x - self.cell_size / 2, corner_y - self.cell_size / 2,
										  corner_x + self.cell_size / 2, corner_y + self.cell_size / 2, 
										  fill=color, tag="corner", outline="")

	def draw_all_beepers(self):
		for location, count in self.world.beepers.items():
			self.draw_beeper(location, count)

	def draw_beeper(self, location, count):
		# handle case where defaultdict returns 0 count by not drawing beepers
		if count == 0: return 

		corner_x = self.calculate_corner_x(location[0])
		corner_y = self.calculate_corner_y(location[1])
		beeper_radius = self.cell_size * BEEPER_CELL_SIZE_FRAC

		points = [corner_x, corner_y - beeper_radius, corner_x + beeper_radius, corner_y, corner_x, corner_y + beeper_radius, corner_x - beeper_radius, corner_y]
		self.create_polygon(points, fill="light grey", outline="black", tag="beeper")

		if count > 1: 
			self.create_text(corner_x, corner_y, text=str(count), font="Arial 12", tag="beeper")

	def draw_all_walls(self):
		for wall in self.world.walls:
			self.draw_wall(wall)

	def draw_wall(self, wall):
		avenue, street, direction = wall.avenue, wall.street, wall.direction
		corner_x = self.calculate_corner_x(avenue)
		corner_y = self.calculate_corner_y(street)

		if direction == Direction.NORTH:
			self.create_line(corner_x - self.cell_size / 2, 
							 corner_y - self.cell_size / 2, 
							 corner_x + self.cell_size / 2, 
							 corner_y - self.cell_size / 2,
							 width=LINE_WIDTH)
		if direction == Direction.SOUTH:
			self.create_line(corner_x - self.cell_size / 2, 
							 corner_y + self.cell_size / 2, 
							 corner_x + self.cell_size / 2, 
							 corner_y + self.cell_size / 2, 
							 width=LINE_WIDTH)
		if direction == Direction.EAST:
			self.create_line(corner_x + self.cell_size / 2,
							 corner_y - self.cell_size / 2,
							 corner_x + self.cell_size / 2,
							 corner_y + self.cell_size / 2, 
							 width=LINE_WIDTH)
		if direction == Direction.WEST:
			self.create_line(corner_x - self.cell_size / 2,
							 corner_y - self.cell_size / 2,
							 corner_x - self.cell_size / 2,
							 corner_y + self.cell_size / 2,
							 width=LINE_WIDTH)

	def draw_karel(self):
		corner_x = self.calculate_corner_x(self.karel.avenue)
		corner_y = self.calculate_corner_y(self.karel.street)
		center = (corner_x, corner_y)

		if self.icon == "karel":
			karel_origin_x = corner_x - self.cell_size / 2 + KAREL_LEFT_HORIZONTAL_PAD * self.cell_size
			karel_origin_y = corner_y - self.cell_size / 2 + KAREL_VERTICAL_OFFSET * self.cell_size

			self.draw_karel_outer_body(karel_origin_x, karel_origin_y, center, self.karel.direction.value)
			self.draw_karel_inner_components(karel_origin_x, karel_origin_y, center, self.karel.direction.value)
			self.draw_karel_legs(karel_origin_x, karel_origin_y, center, self.karel.direction.value)
		elif self.icon == "simple":
			self.draw_simple_karel_icon(center, self.karel.direction.value)

	def draw_karel_outer_body(self, x, y, center, direction):
		points = []
		
		# Top-left point (referred to as origin) of Karel's body
		points.extend((x,y))

		# Calculate Karel's height and width as well as missing diag segments
		width = self.cell_size * KAREL_WIDTH
		height = self.cell_size * KAREL_HEIGHT
		lower_left_missing = (self.cell_size * KAREL_LOWER_LEFT_DIAG) / math.sqrt(2)
		upper_right_missing = (self.cell_size * KAREL_UPPER_RIGHT_DIAG) / math.sqrt(2)

		# These two points define Karel's upper right
		points.extend((x + width - upper_right_missing, y))
		points.extend((x + width, y + upper_right_missing))

		# Karel's bottom right edge
		points.extend((x + width, y + height))

		# These two points define Karel's lower left 
		points.extend((x + lower_left_missing, y + height))
		points.extend((x, y + height - lower_left_missing))

		# Complete the polygon
		points.extend((x,y))

		self.rotate_points(center, points, direction)

		self.create_polygon(points, fill="white", outline="black", width=KAREL_LINE_WIDTH, tag="karel")

	def draw_karel_inner_components(self, x, y, center, direction):
		inner_x = x + self.cell_size * KAREL_INNER_OFFSET
		inner_y = y + self.cell_size * KAREL_INNER_OFFSET

		inner_height = self.cell_size * KAREL_INNER_HEIGHT
		inner_width = self.cell_size * KAREL_INNER_WIDTH

		points = [inner_x, inner_y, inner_x + inner_width, inner_y, inner_x + inner_width, inner_y + inner_height, inner_x, inner_y + inner_height, inner_x, inner_y]
		self.rotate_points(center, points, direction)
		self.create_polygon(points, fill="white", outline="black", width=KAREL_LINE_WIDTH, tag="karel")

		karel_height = self.cell_size * KAREL_HEIGHT
		mouth_horizontal_offset = self.cell_size * KAREL_MOUTH_HORIZONTAL_OFFSET
		mouth_vertical_offset = self.cell_size * KAREL_MOUTH_VERTICAL_OFFSET
		mouth_width = self.cell_size * KAREL_MOUTH_WIDTH
		mouth_y = inner_y + inner_height + mouth_vertical_offset

		points = [x + mouth_horizontal_offset, mouth_y, x + mouth_horizontal_offset + mouth_width, mouth_y]
		self.rotate_points(center, points, direction)
		self.create_polygon(points, fill="white", outline="black", width=KAREL_LINE_WIDTH, tag="karel")

	def draw_karel_legs(self, x, y, center, direction):
		leg_length = self.cell_size * KAREL_LEG_LENGTH
		foot_length = self.cell_size * KAREL_FOOT_LENGTH
		leg_foot_width = self.cell_size * KAREL_LEG_FOOT_WIDTH

		vertical_offset = self.cell_size * KAREL_LEG_VERTICAL_OFFSET
		horizontal_offset = self.cell_size * KAREL_LEG_HORIZONTAL_OFFSET

		# Generate points for left leg
		points = []
		points.extend((x, y + vertical_offset))
		points.extend((x - leg_length, y + vertical_offset))
		points.extend((x - leg_length, y + vertical_offset + foot_length))
		points.extend((x - leg_length + leg_foot_width, y + vertical_offset + foot_length))
		points.extend((x - leg_length + leg_foot_width, y + vertical_offset + leg_foot_width))
		points.extend((x, y + vertical_offset + leg_foot_width))
		points.extend((x, y + vertical_offset))

		self.rotate_points(center, points, direction)
		self.create_polygon(points, fill="black", outline="black", width=KAREL_LINE_WIDTH, tag="karel")

		# Reset point of reference to be bottom left rather than top_left
		y = y + self.cell_size * KAREL_HEIGHT

		# Generate points for right leg
		points = []
		points.extend((x + horizontal_offset, y))
		points.extend((x + horizontal_offset, y + leg_length))
		points.extend((x + horizontal_offset + foot_length, y + leg_length))
		points.extend((x + horizontal_offset + foot_length, y + leg_length - leg_foot_width))
		points.extend((x + horizontal_offset + leg_foot_width, y + leg_length - leg_foot_width))
		points.extend((x + horizontal_offset + leg_foot_width, y))
		points.extend((x + horizontal_offset, y))

		self.rotate_points(center, points, direction)
		self.create_polygon(points, fill="black", outline="black", width=KAREL_LINE_WIDTH, tag="karel")

	def draw_simple_karel_icon(self, center, direction):
		simple_karel_width = self.cell_size * SIMPLE_KAREL_WIDTH
		simple_karel_height = self.cell_size * SIMPLE_KAREL_HEIGHT
		center_x, center_y = center
		points = []
		points.extend((center_x - simple_karel_width / 2 , center_y - simple_karel_height / 2))
		points.extend((center_x - simple_karel_width / 2 , center_y + simple_karel_height / 2))
		points.extend((center_x, center_y + simple_karel_height / 2))
		points.extend((center_x + simple_karel_width / 2, center_y))
		points.extend((center_x, center_y - simple_karel_height / 2))
		points.extend((center_x - simple_karel_width / 2 , center_y - simple_karel_height / 2))
		self.rotate_points(center, points, direction)
		self.create_polygon(points, fill="white", outline="black", width=KAREL_LINE_WIDTH, tag="karel")

	def calculate_corner_x(self, avenue):
		return self.left_x + self.cell_size / 2 + (avenue - 1) * self.cell_size

	def calculate_corner_y(self, street):
		return self.top_y + self.cell_size / 2 + (self.world.num_streets - street) * self.cell_size

	@staticmethod
	def rotate_points(center, points, direction):
		"""
		Rotation logic derived from http://effbot.org/zone/tkinter-complex-canvas.htm
		"""
		cangle = cmath.exp(direction*1j)
		center = complex(center[0], center[1])
		for i in range(0, len(points), 2):
			x = points[i]
			y = points[i+1]
			v = cangle * (complex(x, y) - center) + center
			points[i] = v.real 
			points[i+1] = v.imag
