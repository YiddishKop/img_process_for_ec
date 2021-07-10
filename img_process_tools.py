import cv2, os
import numpy as np

SHOP_INFOS = {'chl':'潮虹乐', 'ywsxstyd':'意万斯线上体验店', 'zqxlzyd':'正清鞋类专营店', 'zqydhwzyd':'正清运动户外专营店'}

def crop_to_800(img):
    '''
    @summary:
        crop 前一步应该是 resize 图像
        resize 需要保证参数 img 图像的宽或者高是 800
    @parameter:
        - img : return from resize_to_800, an opencv object
    '''
    
    # 读取图片失败异常
    if len(img.shape) == 0:
        raise Exception("读取图片文件失败，请核对路径是否正确")

    h, w, _ = img.shape

    # 图片宽高都不是800像素异常
    if h != 800 and w != 800:
        raise Exception("\n原图像素:\n 高 = {}\n 宽 = {}\n 都不是 800 像素".format(h, w))

    cropped = img[0:800, 0:800]  # 裁剪坐标为[y0:y1, x0:x1]
    # cv2.imwrite("./img/test_800.jpg", cropped)
    return cropped


def flip_img(img):
    '''
    @summary:
        整个图片的处理流程为： original img -> resize -> crop -> flip -> merge
    @parameter:
        img: 作为水印融合的前一步，接收从 crop_to_800 返回的 opencv2 对象
    '''
    # Flipped Horizontally 水平翻转
    h_flip = cv2.flip(img, 1)
    cv2.imwrite("girl-h.jpg", h_flip)
    return h_flip



def watermark(img, shop_id, b_or_w = 'b', alpha = 0.8):
    '''
    DONE: src_path 更换成 img
    原因是，我希望 resize crop 等处理的图像结果，可以直接在这里使用
    alpha 通道，表示透明度，alpha=0表示全透明，alpha=255表示不透明
    jpg 图片只能读取 rgb 三通道，png 指定参数后可以读取四通道(第四通道为透明度通道)
    图片要求是800*800的方正图；
    水印图无要求;
    shop_id: 'chl'          -> 潮虹乐
             'ywsxstyd'     -> 意万斯淘宝
             'zqxlzyd'      -> 正清
             'zqydhwzyd'    -> 正清
    '''
    print(b_or_w)

    if b_or_w is not 'w' and b_or_w is not 'b':
        raise Exception("\n水印颜色（第三个参数）只能是 b or w ！\n您输入的是: {}".format(b_or_w))

    # 根据 shop_id 设定水印图片路径
    mask_path = ''
    if shop_id == 'chl':
        mask_path = './img/aaa.png'
    elif shop_id == 'ywsxstyd' and b_or_w == 'b':
        mask_path = './img/ccc_b.png'
    elif shop_id == 'ywsxstyd' and b_or_w == 'w':
        mask_path = './img/ccc_w.png'
    elif shop_id == 'zqxlzyd' and b_or_w == 'b':
        mask_path = './img/ccc_b.png'
    elif shop_id == 'zqxlzyd' and b_or_w == 'w':
        mask_path = './img/ccc_w.png'
    elif shop_id == 'zqydhwzyd' and b_or_w == 'b':
        mask_path = './img/bbb_b.png'
    elif shop_id == 'zqydhwzyd' and b_or_w == 'w':
        mask_path = './img/bbb_w.png'

    # 获取图片宽高
    img_h,img_w = img.shape[0], img.shape[1]
    # 读取水印
    # -1 指明不需要读取 png 的透明度通道
    mask = cv2.imread(mask_path, -1)

    # 设定水印放缩比例
    rate = None
    if shop_id == 'chl':
        rate = int(img_h * 0.08) / mask.shape[0]
    elif shop_id == 'ywsxstyd':
        rate = int(img_h * 0.23) / mask.shape[0]
    elif shop_id == 'zqxlzyd':
        rate = int(img_h * 0.23) / mask.shape[0]
    elif shop_id == 'zqydhwzyd':
        rate = int(img_h * 0.16) / mask.shape[0]

    print(rate)

    # 对水印进行缩放
    mask = cv2.resize(mask, None, fx=rate, fy=rate)
    mask_h, mask_w = mask.shape[0], mask.shape[1]
    mask_channels = cv2.split(mask)
    dst_channels = cv2.split(img)
    b, g, r, a = cv2.split(mask)

    # 设定 mask 在图片的坐标
    if shop_id == 'chl':
        # 1. 设定左上坐标 (h,w)
        ul_points = (int(img_h * 0.1), int(int(img_w/2) - mask_w/2))
        # 2. 设定右下坐标 (h,w)
        dr_points = (int(img_h * 0.1) + mask_h, int(int(img_w/2) + mask_w/2))
    if shop_id == 'ywsxstyd':
        ul_points = (45, 65)
        dr_points = (45 + mask_h, 65 + mask_w)
    if shop_id == 'zqxlzyd':
        ul_points = (45, 65)
        dr_points = (45 + mask_h, 65 + mask_w)
    if shop_id == 'zqydhwzyd':
        ul_points = (45, 65)
        dr_points = (45 + mask_h, 65 + mask_w)

    # 融合
    for i in range(3):
        # 原图指定区域透明度强化 -> 重叠区域变透明一些
        dst_channels[i][ul_points[0] : dr_points[0], ul_points[1] : dr_points[1]] = dst_channels[i][ul_points[0] : dr_points[0], ul_points[1] : dr_points[1]] * (255.0 - a * alpha) / 255
        # 叠加原图和水印图
        dst_channels[i][ul_points[0] : dr_points[0], ul_points[1] : dr_points[1]] += np.array(mask_channels[i] * (a * alpha / 255), dtype=np.uint8)
    dst_img = cv2.merge(dst_channels)
    # cv2.imwrite(r'img\1_1.jpg', dst_img)
    return dst_img



## 读取图像，解决imread不能读取中文路径的问题
def cv_imread(img_file_path):
    '''
    @summary:
        读取图像，解决imread不能读取中文路径的问题
    @parameter:
        img_file_path: 图片绝对路径
    '''
    cv_img=cv2.imdecode(np.fromfile(img_file_path, dtype=np.uint8),-1)
    ## imdecode读取的是rgb，如果后续需要opencv处理的话，需要转换成bgr，转换后图片颜色会变化
    # cv_img=cv2.cvtColor(cv_img,cv2.COLOR_RGB2BGR)
    return cv_img

## 解决存储图像的路径包含中文进而导致失败的问题
def cv_imwrite(dst_path, img):
    '''
    @summary:
        解决存储图像的路径包含中文进而导致失败的问题
    @parameter:
        - dst_path: 保存输出图片的位置（绝对路径）
        - img: opencv2 图像对象
    '''
    cv2.imencode('.jpg', img)[1].tofile(dst_path)


def resize_img_to_800(img_file_path):
    '''
    @summery:
        crop 前一步应该是 resize 图像
        resize 导致图像的宽或者高是 800
    @parameter:
        - img_file_path: the obsolute path of an image
    '''
    
    img = cv_imread(img_file_path)

    print(img)

    # 读取图片失败异常
    if img is None:
        raise Exception("读取图片文件失败，请核对路径是否正确")
    
    h, w, _ = img.shape
    size = None
    
    new_img = np.zeros((3,3),dtype=np.uint8)

    print("\n缩放前的图片尺寸为：{}\n".format(img.shape))
    

    if w > h:
        size = (800, int(800/h*w))
        new_img = cv2.resize(img, size)
    else:
        size = (int(800/w*h), 800)
        new_img = cv2.resize(img, size)

    print("\n缩放后的图片尺寸为：{}\n".format(new_img.shape))

    return new_img



def process_imgs(imgs):
    '''
    @parameters:
        - imgs 就是图片绝对路径的字符串
    '''
    # 潮虹乐
    for shop in SHOP_INFOS:
        imgs_dir, _ = os.path.split(imgs[0])
        shop_dir = os.path.join(imgs_dir + '/' + SHOP_INFOS[shop])
        if not os.path.exists(shop_dir):
            os.mkdir(shop_dir)
        for (id,i) in enumerate(imgs, 1):
            # 生成三套图：详情图（无水印），黑色水印图，白色水印图
            # 检测 shop，如果其为意万斯线上体验店或者正清运动户外专营店，需要左右翻转图像
            resized_img = resize_img_to_800( i )
            cropped_img = crop_to_800(resized_img)
            if shop == 'ywsxstyd' or shop =='zqydhwzyd':
                # 左右翻转图像
                flipped_img = flip_img(cropped_img)
                # 无水印图像
                dst_img = flipped_img
                dst_path = shop_dir + '/' + r'{}.jpg'.format(id)
                cv_imwrite(dst_path, dst_img)
                # 黑色水印 'b'
                dst_img_b = watermark( dst_img, shop)
                dst_path_b = shop_dir + '/' + r'{}'.format(id) + '_b' + '.jpg'
                cv_imwrite(dst_path_b, dst_img_b)
                # 白色水印 'w'
                dst_img_w = watermark( dst_img, shop, 'w')
                dst_path_w = shop_dir + '/' + r'{}'.format(id) + '_w' + '.jpg'
                cv_imwrite(dst_path_w, dst_img_w)
            else:
                # 无水印图像
                dst_img = cropped_img
                dst_path = shop_dir + '/' + r'{}.jpg'.format(id)
                cv_imwrite(dst_path, dst_img)
                # 黑色水印 'b'
                dst_img_b = watermark( dst_img, shop)
                dst_path_b = shop_dir + '/' + r'{}'.format(id) + '_b' + '.jpg'
                cv_imwrite(dst_path_b, dst_img_b)
                # 白色水印 'w'
                dst_img_w = watermark( dst_img, shop, 'w')
                dst_path_w = shop_dir + '/' + r'{}'.format(id) + '_w' + '.jpg'
                cv_imwrite(dst_path_w, dst_img_w)