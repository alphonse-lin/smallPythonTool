from aip import AipImageClassify
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import numpy as np
import json

App_ID = '22872593'
API_KEY = 'oddNiVyIU4D3ItC2hdime4YV'
SECRET_KEY = '1FllGTWmMt55WDxP8DtBZ630rFhHrNAb'

client = AipImageClassify(App_ID, API_KEY, SECRET_KEY)


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def save_json(json_file, output_path):
    json_str = json.dumps(json_file, sort_keys=True, indent=2)
    file = open(output_path, 'w')
    file.write(json_str)
    file.close()


def draw_rect(ori_image, output_result):
    im = np.array(Image.open(ori_image), dtype=np.uint8)
    fig, ax = plt.subplots(1)

    ax.imshow(im)
    for i in range(int(vechile_count)):
        vechile_type = output_result['vehicle_info'][i]['type']
        top_left_x = output_result['vehicle_info'][i]['location']['left']
        top_left_y = output_result['vehicle_info'][i]['location']['top']
        width = output_result['vehicle_info'][i]['location']['width']
        height = output_result['vehicle_info'][i]['location']['height']
        try:
            rect_edgecolor = vechile_categories[vechile_type]
        except KeyError as e:
            pass

        rect = patches.Rectangle((top_left_x, top_left_y), width, height, fill=False, edgecolor=rect_edgecolor,
                                 linewidth=2)
        ax.add_patch(rect)

    fig.savefig(output_path, transparent=True)
    plt.show()


def preset(output_result):
    v_all_count = {}
    all_categories = ["car", "truck", "bus", "motorbike", "tricycle"]
    all_count = []
    for i in range(len(all_categories)):
        amt = output_result['vehicle_num'][all_categories[i]]
        v_all_count[all_categories[i]] = amt
        all_count.append(int(amt))
    v_count = sum(all_count)
    v_categories = {
        all_categories[0]: 'red',
        all_categories[1]: 'blue',
        all_categories[2]: 'green',
        all_categories[3]: 'purples',
        all_categories[4]: 'orange',
    }
    v_all_count['sum'] = v_count

    return v_count, v_categories, v_all_count


if __name__ == '__main__':
    input_path = r'./image/OIP2.jpg'
    output_path = r'./image/OIP2_output.jpg'
    output_json_path = r'./image/json_out.json'

    image = get_file_content(input_path)
    result = client.vehicleDetect(image)
    save_json(result, output_json_path)

    vechile_count, vechile_categories, vechile_all_count = preset(result)
    draw_rect(input_path, result)

    print(vechile_all_count)

#
# # for i in range(int(vehicleCount)):
# xmin = result['vehicle_info'][0]['location']['left']
# ymin = result['vehicle_info'][0]['location']['top']
# xmax = xmin + result['vehicle_info'][0]['location']['width']
# ymax = ymin - result['vehicle_info'][0]['location']['height']
# cv2.rectangle(updateImage, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
#
# cv2.imwrite(drawedImage,updateImage)
