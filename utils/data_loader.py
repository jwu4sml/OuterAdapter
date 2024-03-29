from torchvision import datasets, transforms
from torch.utils.data import Dataset
import torch
import numpy as np
from PIL import Image


class TimestampTransform:
    """Rotate by one of the given angles."""

    def __init__(self, timestamp):
        self.angle = 30*timestamp
        self.p = 0.05*timestamp

    def __call__(self, x):
        # Rotate the image
        x = x.rotate(self.angle)

        # Add salt&pepper noise
        np.random.seed(23)
        intensity_range = (0, 255)
        output = np.asarray(x)
        msk = np.random.binomial(1, self.p / 2, output.shape)
        output = msk * intensity_range[0] + (1 - msk) * output
        msk = np.random.binomial(1, self.p / 2, output.shape)
        output = msk * intensity_range[1] + (1 - msk) * output
        output = np.clip(output, 0, 255)
        return Image.fromarray(output.astype(np.uint8))


def make_dataset(image_list, labels):
    if labels:
      len_ = len(image_list)
      images = [(image_list[i].strip(), labels[i, :]) for i in range(len_)]
    else:
      if len(image_list[0].split()) > 2:
        images = [(val.split()[0], np.array([int(la) for la in val.split()[1:]])) for val in image_list]
      else:
        images = [(val.split()[0], int(val.split()[1])) for val in image_list]
    return images


def rgb_loader(path):
    with open(path, 'rb') as f:
        with Image.open(f) as img:
            return img.convert('RGB')


def l_loader(path):
    with open(path, 'rb') as f:
        with Image.open(f) as img:
            return img.convert('L')


class ImageList(Dataset):
    def __init__(self, image_list, labels=None, transform=None, target_transform=None, mode='RGB'):
        imgs = make_dataset(image_list, labels)
        self.imgs = imgs
        self.transform = transform
        self.target_transform = target_transform
        if mode == 'RGB':
            self.loader = rgb_loader
        elif mode == 'L':
            self.loader = l_loader

    def __getitem__(self, index):
        path, target = self.imgs[index]
        img = self.loader(path)
        if self.transform is not None:
            img = self.transform(img)
        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return len(self.imgs)


def load_source(source_path):
    transform = transforms.Compose([
        transforms.Scale(256),
        transforms.RandomHorizontalFlip(),
        transforms.RandomCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
         ])
    data = ImageList(open(source_path).readlines(), transform=transform)
    src_loader = torch.utils.data.DataLoader(data, batch_size=len(data), shuffle=False, drop_last=False)
    return src_loader


def load_target(target_path, timestamp):
    transform = transforms.Compose([
        TimestampTransform(timestamp=timestamp),
        transforms.Scale(256),
        transforms.RandomHorizontalFlip(),
        transforms.RandomCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
         ])
    data = ImageList(open(target_path).readlines(), transform=transform)
    tar_loader = torch.utils.data.DataLoader(data, batch_size=len(data), shuffle=False, drop_last=False)
    return tar_loader


def load_test(test_path, timestamp):
    transform = transforms.Compose([
        TimestampTransform(timestamp=timestamp),
        transforms.Scale(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
         ])
    data = ImageList(open(test_path).readlines(), transform=transform)
    test_loader = torch.utils.data.DataLoader(data, batch_size=len(data), shuffle=False, drop_last=False)
    return test_loader

