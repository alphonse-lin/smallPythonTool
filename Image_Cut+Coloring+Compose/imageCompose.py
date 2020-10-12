import os
import PIL.Image as Image
import time


def timeCount(calcMode, t_start):
    t_end = time.time()
    final_time = round((t_end - t_start), 2)
    print("{0}:最终计算时间 {1} s".format(calcMode, final_time))


def get_new_img_xy(infile):
    im = Image.open(infile)
    (x, y) = im.size
    return x, y


def image_compose(image_column, image_rownum, image_names, image_save_path, x_new, y_new):
    to_image = Image.new('RGB', (image_column * x_new, image_rownum * y_new))
    # 循环遍历
    total_num = 0
    for y in range(1, image_rownum + 1):
        for x in range(1, image_column + 1):
            from_image = Image.open(image_names[image_column * (y - 1) + x - 1])
            to_image.paste(from_image, ((x - 1) * x_new, (y - 1) * y_new))
            total_num += 1
            if total_num == len(image_names):
                break
    return to_image.save(image_save_path)


def get_image_list_fullpath(dir_path):
    file_name_list = os.listdir(dir_path)
    image_fullpath_list = []
    for file_name_one in file_name_list:
        file_one_path = os.path.join(dir_path, file_name_one)
        if os.path.isfile(file_one_path):
            image_fullpath_list.append(file_one_path)
        else:
            img_path_list = get_image_list_fullpath(file_one_path)
            image_fullpath_list.extend(img_path_list)
    return image_fullpath_list


def merge_images(image_dir_path, image_column, output_path):
    image_fullpath_list = get_image_list_fullpath(image_dir_path)
    print("image_fullpath_list", len(image_fullpath_list))
    for x in image_fullpath_list:
        print("{0}\n".format(x))

    # image_save_path = r'{0}_final.jpg'.format(image_dir_path)
    image_save_path = output_path
    image_rownum_yu = len(image_fullpath_list) % image_column
    if image_rownum_yu == 0:
        image_rownum = len(image_fullpath_list) // image_column
    else:
        image_rownum = len(image_fullpath_list) // image_column + 1

    x_list = []
    y_list = []
    for img_file in image_fullpath_list:
        img_x, img_y = get_new_img_xy(img_file)
        x_list.append(img_x)
        y_list.append(img_y)

    x_new = int(x_list[len(x_list) // 5 * 4])
    y_new = int(y_list[len(y_list) // 5 * 4])
    print(x_new)
    print(y_new)
    image_compose(image_column, image_rownum, image_fullpath_list, image_save_path, x_new, y_new)


def change_name(image_dir_path):
    file_name_list = os.listdir(image_dir_path)
    for file_name_one in file_name_list:
        first = file_name_one[7:-5]
        new_name = str(first.zfill(3)) + '.jpg'
        os.renames(os.path.join(image_dir_path, file_name_one), os.path.join(image_dir_path, new_name))
    print('改变完成')


if __name__ == '__main__':
    t_start = time.time()
    image_dir_path = r'E:\迅雷下载\图片任务组_20200822_2237\\'
    image_colnum = 20
    output_path = r'E:\迅雷下载\output\final.jpg'

    # 改变文件名字
    # change_name(image_dir_path)

    merge_images(image_dir_path, image_colnum,output_path)
    timeCount("输出完成", t_start)
