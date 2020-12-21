import shutil
import os


def remove_file(old_path, new_path):
    print(old_path)
    print(new_path)
    filelist = os.listdir(old_path)  # 列出该目录下的所有文件,listdir返回的文件列表是不包含路径的。
    step = 4
    for i in range(len(filelist)):
        if (i % step == 0):
            src = os.path.join(old_path, filelist[i])
            dst = os.path.join(new_path, filelist[i])
            print('image index:', i)
            shutil.move(src, dst)
    print('images count:{0}'.format(int(len(filelist) / step)))


if __name__ == '__main__':
    old_path = r'E:\114_temp\001_古道\赵一一的照片建模\20201220_测试_内部结构\3rd\照片'
    new_path = r'E:\114_temp\001_古道\赵一一的照片建模\20201220_测试_内部结构\3rd\照片_筛选'
    remove_file(old_path, new_path)
