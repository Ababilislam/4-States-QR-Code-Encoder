la = [1, 1, 1, 1, 1, 1, 1, 0, 0, '00', '00', '11', '10', '00', '00', '11', '10', 0, 1, 1, 1, 1, 1, 1, 1]

import numpy as np
from PIL import Image
import glob
import os

# open images by providing path of images
img1 = Image.open("1.jpg")
img2 = Image.open("2.jpeg")
img3 = Image.open("3.jpg")
img4 = Image.open("4.jpg")
# ++++++++++++++++++++++image resize++++=
img1 = img1.resize((50, 50))
img2 = img2.resize((50, 50))
img3 = img3.resize((50, 50))
img4 = img4.resize((50, 50))
imga = img2.resize((5, 5))



# need to convert image in to numpy arrary
img_array_1 = np.array(img1)
img_array_2 = np.array(img2)
img_array_3 = np.array(img3)
img_array_4 = np.array(img4)
img_array_a = np.array(imga)
h1 = np.hstack((img_array_1,img_array_1))
print(h1)
# h1 = np.hstack((h1))

for i in la:
    # print(i, end=' ')
    k = int(i)
    # print(type(k))
    # print(k,end=',')
    if i == 0 or "00":
        f = 0
        # h1=np.array(h1)
        # h1 = np.hstack((h1,img_array_1))
    # elif i == '01;' or "1" or 1:
    #     f = 1
    #     h1 = np.hstack((h1,img_array_2))
    # elif i == '10' or "10" or 10:
    #     f = 3
    #     h1 = np.hstack((h1,img_array_3))
    # elif i == '11' or "11" or 11:
    #     f = 4
    #     h1 = np.hstack((h1,img_array_4))

finalImage = Image.fromarray(h1)
#
finalImage.save('collage.png')
# # _________________i need to resize image ______________
# print("{}".format(img1.format))
# print("size:{}".format(img1.size))
# print("mode:{}".format(img1.mode))
#
# # +++++++++++++++++++++++ append images in to list+++++++++
# unsize_image_list = []
# image_list = []
# for file_name in glob.glob('*.jpg'):
#     print(file_name)
#     img = Image.open(file_name)
#     unsize_image_list.append(img)
# # print(unsize_image_list)
# # +++++++++++++++Imge resizing++++++++++++
# for image in unsize_image_list:
#     # image.show()
#     image=image.resize((50, 50))
#     image_list.append(image)
#     # image.show()
# # print(image_list)
# # ++++++++save resize image_++++++++++=
# for i, image in enumerate(image_list):
#     image.save('{}{}{}'.format('resize50*50/image', i+1, '.png'))
# # =======================image resizing done====================


# create arrays of above images
# img_array_1 = np.array(img1)
# img_array_2 = np.array(img2)
# img_array_3 = np.array(img3)
# img_array_4 = np.array(img4)
# # print(img1_array)
# # ====== collaging images ======
# h1 = np.hstack((img_array_1, img_array_2, img_array_3, img_array_4))
# h2 = np.hstack((img_array_4, img_array_3, img_array_2,img_array_1))
#
# arrayImageFinal= np.vstack((h1, h2))
#
# finalImage=Image.fromarray(arrayImageFinal)
#
# finalImage.save('collage.png')
