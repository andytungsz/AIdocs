import os
import time
import torch.nn as nn
import torch

import torchvision.transforms as transforms

from PIL import Image
from matplotlib import pyplot as plt
import torchvision.models as models
#import environments
from pyasm.common.Environment import get_data_dir

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
device = torch.device("cpu")

vis = True
vis_row = 4

norm_mean = [0.485, 0.456, 0.406]
norm_std = [ 0.229, 0.224, 0.225]

inference_transform = transforms.Compose([
    
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(norm_mean, norm_std),
    ])
    
classes = ["ants", "bees"]

def img_transform(img_rgb, transform=None):
    if transform is None:
        raise ValueError(" can not find transform !")

    img_t = transform(img_rgb)
    return img_t

def  get_img_name(img_dir, format = 'jpg'):
    
    file_names = os.listdir(img_dir)
    img_names = list(filter(lambda x: x.endswith(format),file_names))
    if len(img_names) < 1:
        raise ValueError("{} can not find {} format data ".format(img_dir, format))
    return img_names

def get_model(m_path, vis_model=False):
    resnet18 = models.resnet18()

    num_ftrs = resnet18.fc.in_features
    resnet18.fc = nn.Linear(num_ftrs, 2)

    checkpoint = torch.load(m_path)
    resnet18.load_state_dict(checkpoint['model_state_dict'])

    if vis_model:
        from torchsummary import summary
        summary(resnet18, input_size=(3, 224, 224), device="cpu")
    return resnet18

if __name__ == "__main__":
    #img_dir = os.path.join(environments.hymenoptera_data_dir, "val/bees")
    #img_dir = os.path.join(environments.get_data_dir(), "val/bees")
    img_dir = os.path.join("./data", "val/bees")

    model_path = "./checkpoint_14_epoch.pkl"
    time_total = 0
    img_list, img_pred = list(), list()

    #1. data input
    img_names = get_img_name(img_dir)
    num_img = len(img_names)

    #model 
    resnet18 = get_model(model_path, True)
    resnet18.to(device)
    resnet18.eval()

    with torch.no_grad():
        for idx, img_names in enumerate(img_names):
            path_img = os.path.join(img_dir, img_names)
            img_rgb = Image.open(path_img).convert('RGB')

            img_tensor = img_transform(img_rgb, inference_transform)
            img_tensor.unsqueeze_(0)
            img_tensor = img_tensor.to(device)

            time_tic = time.time()
            outputs = resnet18(img_tensor)
            time_toc = time.time()

            _, pred_int = torch.max(outputs.data, 1)
            pred_str = classes[int(pred_int)]
            
            if vis:
                img_list.append(img_rgb)
                img_pred.append(pred_str)

                if (idx+1) % (vis_row*vis_row) == 0 or num_img == idx+1:
                    for i in range(len(img_list)):
                        plt.subplot(vis_row, vis_row, i+1).imshow(img_list[i])
                        plt.title("predict:{}".format(img_pred[i]))
                    plt.show()
                    plt.close()
                    img_list, img_pred = list(), list()

            time_s = time_toc-time_tic
            time_total += time_s

            print('{:d}/{:d}: {} {:.3f}s '.format(idx + 1, num_img, img_name, time_s))

    print("\ndevice:{} total time:{:.1f}s mean:{:.3f}s".
          format(device, time_total, time_total/num_img))
    if torch.cuda.is_available():
        print("GPU name:{}".format(torch.cuda.get_device_name()))










