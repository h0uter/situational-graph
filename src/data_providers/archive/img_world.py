from matplotlib import image
import matplotlib.pyplot as plt
import os

class ImgWorld():

    def __init__(self, img):
        self.img = img
        print(self.img.shape)
        self.height, self.width, _ = self.img.shape

    def observe_local_grid(self, pos, size):
        '''crops the image around pos with size'''
        x, y = pos
        # cannot sample near edge of the image world.
        return self.img[y-size:y+size, x-size:x+size]


def show_img(img):
    plt.imshow(img)
    plt.show()
    plt.pause(0.001)

if __name__ == '__main__':
    
    full_path = os.path.join('resource', 'floor-plan-villa.png')
    img = image.imread(full_path)
    show_img(img)
    
    img_world = ImgWorld(img)

    show_img(img_world.observe_local_grid((700,500), 200))