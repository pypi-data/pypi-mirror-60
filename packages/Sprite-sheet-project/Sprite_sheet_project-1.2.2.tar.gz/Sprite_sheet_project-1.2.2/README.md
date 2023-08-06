#  Sprite Sheet
A sprite is a small raster graphic (a bitmap) that represents an object such as a character, a vehicle, a projectile, etc.
    
Sprites are a popular way to create large, complex scenes as you can manipulate each sprite separately from the rest of the scene. This allows for greater control over how the scene is rendered, as well as over how the players can interact with the scene.
    
    This Package is a useful tool to find  Sprite Sheet of image (lower than 2048*2048).
#### Requirements:
    Linux
    
#### Install:

    #cd to your image folder
    
    $cd image
    
    $pip install Sprite-sheet-project==1.2.2
    $python3

    >>> from sprite_nvqMinh.spriteutil import SpriteSheet
    >>> import timeit
    >>> from PIL import Image
    >>> start = timeit.timeit()
    >>> image = Image.open('1.png')
    >>> sprite_sheet = SpriteSheet(image)
    >>> sprites, labels = sprite_sheet.find_sprites()
    >>> print(len(sprites))
    >>> image = sprite_sheet.create_sprite_labels_image()
    >>> image.save('save2.png')
    >>> end = timeit.timeit()
    >>> print(end)

#### Functional testing:
    Step 1 : clone from github to your  git repository
       git@github.com:intek-training-jsc/sprite-sheet-nvqMinh29101992.git
    Step 2 : git branch to see all branches
    Step 3 : git checkout <branch_name> to see each part of this project
      
## Contributing
    Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
## License

    This project is licensed under the MIT License - see the LICENSE.md file for details
