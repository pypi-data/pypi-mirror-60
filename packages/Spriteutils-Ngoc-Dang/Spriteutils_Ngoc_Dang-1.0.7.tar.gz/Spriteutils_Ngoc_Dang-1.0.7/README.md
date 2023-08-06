# Sprites Detection
A [**sprite**](<https://en.wikipedia.org/wiki/Sprite_(computer_graphics)>) is a small [**raster graphic**](https://en.wikipedia.org/wiki/Raster_graphics) (a **bitmap**) that represents an object such as a [character, a vehicle, a projectile, etc.](https://www.youtube.com/watch?v=a1yBP5t-fSA)

## Sprite Sheet

It is not uncommon for games to have tens to hundreds of sprites. Loading each of these as an individual image would consume a lot of memory and processing power. To help manage sprites and avoid using so many images, many games use [**sprite sheets**](https://www.youtube.com/watch?v=crrFUYabm6E) (also known as **image sprites**).

A sprite sheet consists of multiple sprites in one image. In other words, sprite sheets pack multiple sprites into a single picture. Using sprite sheet, video game developers create sprite sheet animation representing one or several animation sequences while only loading a single file:

![Metal Slug Sprites](metal_slug_sprite_sheet_large.png)

## Sprite Bounding Box

A frame (**bounding box**) can be used to delimit the sprite in the sprite sheet. This bounding box is defined with two 2D points `top_left` and the `bottom_right`, which their respective coordinates `x` and `y` are relative to the top-left corner of the sprite sheet's image.

For example:

![Shape Bounding Boxes](metal_slug_sprite_detection_bounding_boxes.png)

## Sprite Mask

The mask of a sprite defines the 2D shape of the sprite. For example, the sprite sheet 
contains 3 following sprites:


![Metal Slug Standing Stance](1.png)

The masks of these sprites are respectively:

![](2.png)

## Aim of the project
- Detect sprites packed in an image (sheet) and draw their masks and bounding boxes into a new image with the same size of the original image. <br/>
- Present a 2D map of all the the sprites with their labels. <br/>

## Usage Information
### Prerequisites
- `Python 3.6` is required. <br/>
- `pip` is requied, to install `sudo apt install pip`
### Usage
- `pip install Friendlyngoc` from your terminal
- Example of functioning:

    - Input as a spritesheet
    !['3.png'](spritesheet.png)

    - A image with sprite masks
    !['spritesheet.png'](4.png)

    ```python
    >>> from Friendlyngoc_spriteutil.spriteutil import SpriteSheet
    >>> sprite_sheet = SpriteSheet('spritesheet.png')
    >>> sprites, labels = sprite_sheet.find_sprites()
    >>> len(sprites)
    22
    >>> # Create the mask image with bounding boxes.
    >>> image = sprite_sheet.create_sprite_labels_image()
    >>> image.save('sprites_masks.png')
    ```

## Contact Information
- Email: `Email: ngoc.dang@f4.intek.edu.vn` <br/>
- Phone number: `Phone: (+84) 90 690 2056`