from PIL import Image
import app.filesystem as fs
import os
import skimage


def strip_img_alpha_channel(img_dir_path, extensions=[".jpg", ".jpeg", ".png"]):
    for filename in os.listdir(img_dir_path):
        if not fs.is_type(filename, extensions):
            continue
        filepath = os.path.join(img_dir_path, filename)
        img = skimage.io.imread(filepath)
        img_no_alpha = img[:,:,:3]
        skimage.io.imsave(filepath, img_no_alpha)


def create_pair(output_dir_path, img_a_path, img_b_path, img_a_name, img_b_name):
    img_a = Image.open(img_a_path)
    img_b = Image.open(img_b_path)
    widths, heights = zip(*(i.size for i in [img_a, img_b]))
    img_pair = Image.new('RGB', (sum(widths), max(heights)))
    img_pair.paste(img_a, (0, 0))
    img_pair.paste(img_b, (img_a.size[0], 0))
    img_pair.save(fs.filepath(output_dir_path, img_a_name))


def extract_subimages(img_path, 
                    output_dir_path, 
                    subimage_width, 
                    subimage_height, 
                    num_subimages_x, 
                    num_subimages_y, 
                    append=False,
                    rotation=0, 
                    flip_h=False,
                    flip_v=False):
    if num_subimages_x < 2 or num_subimages_y < 2:
        raise ValueError("number of subimages arguments must be a value greater than 1")
    if not append:
        fs.rm(output_dir_path)
    if not fs.exists(output_dir_path):
        fs.mkdir(output_dir_path)
    img = Image.open(img_path)
    img = rotate(img, rotation)
    img = flip(img, flip_h, flip_v)
    img_width, img_height = img.size
    dx = float(img_width-subimage_width) / (num_subimages_x-1)
    dy = float(img_height-subimage_height) / (num_subimages_y-1)
    max_num_subimages = num_subimages_x * num_subimages_y
    counter = len(fs.ls(output_dir_path)) + 1
    for j in range(num_subimages_y):
        for i in range(num_subimages_x):
            xo = int(round(dx * i))
            yo = int(round(dy * j))
            subimage = img.crop((xo, yo, xo+subimage_width, yo+subimage_height))
            num_leading_zeros = len(str(max_num_subimages))+1
            filename = ("{:0"+str(num_leading_zeros)+"d}.png").format(counter)
            subimage.save(fs.filepath(output_dir_path, filename))
            counter += 1


def rotate(img, angle_deg_ortho):
    if angle_deg_ortho == 90:
        return img.transpose(Image.ROTATE_90)
    elif angle_deg_ortho == 180:
        return img.transpose(Image.ROTATE_180)
    elif angle_deg_ortho == 270:
        return img.transpose(Image.ROTATE_270)
    return img


def flip(img, flip_h, flip_v):
    img_flipped = img
    if flip_h:
        img_flipped = img_flipped.transpose(Image.FLIP_LEFT_RIGHT)
    if flip_v:
        img_flipped = img_flipped.transpose(Image.FLIP_TOP_BOTTOM)
    return img_flipped





  