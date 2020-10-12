from PIL import Image
import requests
import time
import os


def timeCount(calcMode, t_start):
    t_end = time.time()
    final_time = round((t_end - t_start), 2)
    print("{0}:最终计算时间 {1} s".format(calcMode, final_time))


def del_file(path):
    for i in os.listdir(path):
        file_data = path + '\\' + i
        if os.path.isfile(file_data):
            os.remove(file_data)
        else:
            del_file(file_data)


def cut_image(image, num):
    width, height = image.size
    item_width = int(width / num)
    item_length = int(height / num)
    box_list = []
    count = 0
    for j in range(0, num):
        for i in range(0, num):
            count += 1
            box = (i * item_width, j * item_length, (i + 1) * item_width, (j + 1) * item_length)
            box_list.append(box)
    print('总切割数为{0}'.format(count))
    image_list = [image.crop(box) for box in box_list]
    return image_list


def save_images(image_list, path):
    index = 1
    for image in image_list:
        image.save('{0}'.format(path) + '/' + str(index) + '.png')
        index += 1


def coloring(image_list, output_path):
    index = 1
    jsonList = []
    for i in range(len(image_list)):
        path = '{0}'.format(output_path) + '/' + str(index) + '.png'
        r = requests.post(
            "https://api.deepai.org/api/colorizer",
            files={
                'image': open(path, 'rb'),
            },
            headers={'api-key': '3c5d4931-bd47-4627-aa59-3bd342dee37c'}
        )
        index += 1
        rJSON = r.json()
        jsonList.append(rJSON['output_url'])
    return jsonList


def text_save(filename, data):  # filename为写入CSV文件的路径，data为要写入数据列表.
    file = open(filename, 'a')
    for i in range(len(data)):
        s = str(data[i]).replace('[', '').replace(']', '')  # 去除[],这两行按数据不同，可以选择
        s = s.replace("'", '').replace(',', '') + '\n'  # 去除单引号，逗号，每行末尾追加换行符
        file.write(s)
    file.close()
    print("保存成功")


if __name__ == '__main__':
    t_start = time.time()
    # input_path = r'originalCutImage.png'
    input_path = r'test001.jpg'
    output_path = r'.\cutImage_output'
    txt_file = r'outputImageAddress.txt'
    cut_num = 2

    # 打开图像
    image = Image.open(input_path)

    # 分割图像
    image_list = cut_image(image, cut_num)
    timeCount("切割完成", t_start)

    # 保存图像

    if os.path.exists(r'.\cutImage_output\1.png'):
        del_file(output_path)
    else:
        save_images(image_list, output_path)
        timeCount("保存完成", t_start)

    # # 上色
    # webList = coloring(image_list, output_path)
    # timeCount("上色完成", t_start)
    #
    # # 输出网址
    # if os.path.exists(txt_file):
    #     os.remove(txt_file)
    # text_save(txt_file, webList)
    # timeCount("输出完成", t_start)
