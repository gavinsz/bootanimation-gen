# coding=utf-8
__author__ = 'snomy'


import os
import shutil
from PIL import Image
from PIL import ImageFilter
import zipfile
import sys


# ---------------------- 函数 --------------------------
def isFullBlack(xy, image):
    point_cnt = 0
    xy_left = (xy[0]-1, xy[1]+0)
    xy_right = (xy[0]+1, xy[1]+0)
    xy_up = (xy[0]+0, xy[1]-1)
    xy_bottom = (xy[0]+0, xy[1]+1)


    lst = [xy, xy_left, xy_right, xy_up, xy_bottom]
    for i in lst:
        xxx = i[0]
        yyy = i[1]
        if i[0] < 0:
            xxx = 0
        if i[0] >= image.size[0]:
            xxx =  xy[0]
        if i[1] < 0:
            yyy = 0
        if i[1] >= image.size[1]:
            yyy = xy[1]


        if image.getpixel((xxx, yyy)) != (0, 0, 0, 255):
            point_cnt += 1
    return point_cnt


# ---------------------- 程序执行 --------------------------
# 步进多少像数分割图片
MOVE_PIX = 32


# 判断logo.png是否存在，不存在退出
if not os.path.exists("logo.png"):
    print("logo.png is not existent")
    sys.exit()


# 判断guang.png是否存在，不存在退出
if not os.path.exists("guang.png"):
    print("guang.png is not existent")
    sys.exit()


# 1. 输入每秒显示几张
if len(sys.argv) >= 2:
    pics_per_second = eval(sys.argv[1])
    if pics_per_second <= 0:
        print("too small")
        sys.exit()
    if pics_per_second > 60:
        print("too large")
        sys.exit()
    if 1<= pics_per_second <= 60:
        print(pics_per_second, "frame/s")
else:
    while True:
        pics_per_second = input("frame/s: ")
        if pics_per_second <= 0:
            print("too small")
        if pics_per_second > 60:
            print("too large")
        if 1<= pics_per_second <= 60:
            break


Im = Image.open("logo.png")
print("logo.png")
print(Im.mode, Im.size, Im.format)


Im_guang = Image.open("guang.png")
print("guang.png")
print(Im_guang.mode, Im_guang.size, Im_guang.format)


# 先删除文件夹
if os.path.exists("part0"):
    shutil.rmtree("part0")
# 创建文件夹
os.mkdir("part0")


# 判断文件是否存在
if os.path.exists("desc.txt"):
    os.remove("desc.txt")


# 2. 生成 desc.txt 文件
hDescFile = open("desc.txt", mode='w')
hDescFile.write("%d %d %d\n" % (Im.size[0], Im.size[1], pics_per_second))
hDescFile.write("p 0 0 part0\n")
hDescFile.close()


# 2.5 判断是否存在掩膜图片，没有则生成掩膜图片，有则使用现有的
img_mask = Image.new('RGBA', Im.size)
if not os.path.exists("mask.png"):
    print("mask.png is not existent")
    img_mask.paste(Im, (0, 0))
    for height in range(img_mask.size[1]):
        for width in range(img_mask.size[0]):
            #if img_mask.getpixel((width, height)) != (0, 0, 0, 255):
            cnt = isFullBlack((width, height), Im)
            if cnt == 5:
                img_mask.putpixel((width, height), ((0, 0, 0, 0)))
            elif cnt == 4:
                img_mask.putpixel((width, height), ((0, 0, 0, 50)))
            elif cnt == 3:
                img_mask.putpixel((width, height), ((0, 0, 0, 100)))
            elif cnt == 2:
                img_mask.putpixel((width, height), ((0, 0, 0, 150)))
            elif cnt == 1:
                img_mask.putpixel((width, height), ((0, 0, 0, 200)))
    #img_mask.save("img_mask.png")
else:
    print("use mask.png")
    img_mask = Image.open("mask.png")
    print(img_mask.mode, img_mask.size, img_mask.format)


# 3. 生成 每张图片
index = 0
while True:
    if MOVE_PIX*index > Im.size[0]:
        break
    new_img = Image.new('RGB', Im.size)
    new_img.paste(Im, (0, 0))
    new_img.paste(Im_guang, (MOVE_PIX*index, 0), Im_guang)
    new_img.paste(img_mask, (0, 0), img_mask)
    save_path = "part0/%04d.png" % index
    print(save_path)
    new_img.save(save_path, "PNG")
    index += 1
#end while


# 4. 生成zip文件
if os.path.exists("bootanimation.zip"):
    os.remove("bootanimation.zip")


zpfd = zipfile.ZipFile("bootanimation.zip", mode='w', compression=zipfile.ZIP_STORED)
zpfd.write("desc.txt")
startdir = "part0"
for dirpath, dirnames, filenames in os.walk(startdir):
    for filename in filenames:
        zpfd.write(os.path.join(dirpath, filename))
zpfd.close()
print(" -------- make bootanimation.zip OK --------")


# 5. 清理文件
if os.path.exists("part0"):
    shutil.rmtree("part0")


if os.path.exists("desc.txt"):
    os.remove("desc.txt")