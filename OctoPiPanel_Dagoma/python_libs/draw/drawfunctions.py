#!/usr/bin/env python

import python_libs.draw.hollowtext as hollowtext
import pygame

def draw_text(surface, text, position, align="none", font="", color=(0, 255, 0), outline=True, outline_color=(1, 1, 1)):	
	label = font.render(text, 1, color)
	if position[0] == "right":
		x = screensize[0]
	elif position[0] == "left":
		x = 0
	else:
		x = position[0]		
	if position[1] == "top":
		y = 0
	elif position[1] == "bottom":
		y = screensize[1]-font.get_height()
	else:
		y = position[1]
	if align == "left":
		x = x
	elif align == "right":
		x = x-label.get_width()
	elif align == "center":
		x = x-(label.get_width()/2)		
	pos = (x, y)
	if outline == True:
		text = hollowtext.textOutline(font, text, color, outline_color)
		surface.blit( text, (pos[0], pos[1]))
	else:
		surface.blit( label, (pos[0], pos[1]))

def draw_image(surface, img, position, align="none"):
	x = position[0]
	y = position[1]
	if align == "right":
		x = x-img.get_width()
	elif align == "center":
		x = x-(img.get_width()/2)
	surface.blit(img, (x, y))
	
def draw_button(surface, img, position, text="none", font="none", color=(0, 255, 0), outline=True, outline_color=(1, 1, 1), align="none"):
	x = position[0]
	y = position[1]
	if align == "right":
		x = x-img.get_width()
	elif align == "center":
		x = x-(img.get_width()/2)
	if text != "none":
		label = font.render(text, 1, color)
		label_position = ( x+(img.get_width()/2)-(label.get_width()/2), y+(img.get_height()/2)-(font.get_height()/2) )
	surface.blit(img, (x, y))
	
	if outline == True:
		text = hollowtext.textOutline(font, text, color, outline_color)
		surface.blit( text, label_position)
	else:
		surface.blit( label, label_position)
		
#	surface.blit( label, (x+(img.get_width()/2)-(label.get_width()/2), y+(img.get_height()/2)-(font.get_height()/2) ))
	
def draw_roundrect(surface, color, rect, width, xr, yr): 
	clip = surface.get_clip()
	

	# left and right
	surface.set_clip(clip.clip(rect.inflate(0, -yr*2)))
	pygame.draw.rect(surface, color, rect.inflate(1-width,0), width)

	# top and bottom
	surface.set_clip(clip.clip(rect.inflate(-xr*2, 0)))
	pygame.draw.rect(surface, color, rect.inflate(0,1-width), width)

	# top left corner
	surface.set_clip(clip.clip(rect.left, rect.top, xr, yr))
	pygame.draw.ellipse(surface, color, pygame.Rect(rect.left, rect.top, 2*xr, 2*yr), width)

	# top right corner
	surface.set_clip(clip.clip(rect.right-xr, rect.top, xr, yr))
	pygame.draw.ellipse(surface, color, pygame.Rect(rect.right-2*xr, rect.top, 2*xr, 2*yr), width)

	# bottom left
	surface.set_clip(clip.clip(rect.left, rect.bottom-yr, xr, yr))
	pygame.draw.ellipse(surface, color, pygame.Rect(rect.left, rect.bottom-2*yr, 2*xr, 2*yr), width)

	# bottom right
	surface.set_clip(clip.clip(rect.right-xr, rect.bottom-yr, xr, yr))
	pygame.draw.ellipse(surface, color, pygame.Rect(rect.right-2*xr, rect.bottom-2*yr, 2*xr, 2*yr), width)

	surface.set_clip(clip)
