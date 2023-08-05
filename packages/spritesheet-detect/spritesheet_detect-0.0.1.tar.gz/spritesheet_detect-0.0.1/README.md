# Sprites Detection

## Introduction

A [**sprite**](<https://en.wikipedia.org/wiki/Sprite_(computer_graphics)>) is a small [**raster graphic**](https://en.wikipedia.org/wiki/Raster_graphics) (a **bitmap**) that represents an object such as a [character, a vehicle, a projectile, etc.](https://www.youtube.com/watch?v=a1yBP5t-fSA)

### Sprite Sheet

It is not uncommon for games to have tens to hundreds of sprites. Loading each of these as an individual image would consume a lot of memory and processing power. To help manage sprites and avoid using so many images, many games use [**sprite sheets**](https://www.youtube.com/watch?v=crrFUYabm6E) (also known as **image sprites**).

A sprite sheet consists of multiple sprites in one image. In other words, sprite sheets pack multiple sprites into a single picture. Using sprite sheet, video game developers create sprite sheet animation representing one or several animation sequences while only loading a single file:


### Sprite Bounding Box

A frame (**bounding box**) can be used to delimit the sprite in the sprite sheet. This bounding box is defined with two 2D points `top_left` and the `bottom_right`, which their respective coordinates `x` and `y` are relative to the top-left corner of the sprite sheet's image.


## What the project does
- Detect sprites packed in an image (sheet) and draw their masks and bounding boxes into a new image with the same size of the original image. <br/>
- Present a 2D map of all the the sprites with their labels. <br/>


## Usage Information
### Prerequisites
- Python 3.7 is required. <br/>
### Usage
- Use git to clone the link `https://github.com/intek-training-jsc/sprite-sheet-hoaithu1.git` to your local directory. <br/>
- Change the your current working directory to where you git the project. <br/>
- Open terminal and type `pipenv install -e Pipfile` to install virtual environment. <br/>
- For example: <br/>
```python
>>> from spritesheet_detect.spriteutil import SpriteSheet
>>> sprite_sheet = SpriteSheet('Barbarian.gif')
>>> sprites, labels = sprite_sheet.find_sprites()
>>> len(sprites)
39
>>> # Create the mask image with bounding boxes.
>>> image = sprite_sheet.create_sprite_labels_image()
>>> image.save('barbarian_bounding_boxes.png')
```

## Contact Information
- If you have any problems using this library, please use the contact below. <br/>
`Email: hoai.le@f4.intek.edu.vn`

