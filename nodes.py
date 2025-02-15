import torch
from PIL import Image

# FUNCTIONS

def to_tensor(image):
    if isinstance(image, Image.Image):
        return torch.from_numpy(np.array(image)) / 255.0
    if isinstance(image, torch.Tensor):
        return image
    if isinstance(image, np.ndarray):
        return torch.from_numpy(image)
    raise ValueError(f"Cannot convert {type(image)} to torch.Tensor")

def crop_image(image, crop_region):
    x1 = int(crop_region[0])
    y1 = int(crop_region[1])
    x2 = int(crop_region[2])
    y2 = int(crop_region[3])

    cropped = image[:, y1:y2, x1:x2, :]

    return cropped

def empty_pil_tensor(w=64, h=64):
    return torch.zeros((1, h, w, 3), dtype=torch.float32)


# NODES

class StringWrapper:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prepend": ("STRING", {
                    "multiline": True, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": "",
 #                   "lazy": True
                }),
                "body": ("STRING", {
                    "multiline": True, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": "",
 #                   "lazy": True
                }),
                "append": ("STRING", {
                    "multiline": True, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": "",
 #                   "lazy": True
                }),
                "delimiter": ("STRING", {
                    "multiline": False, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": ", ",
                    # "lazy": True
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    #RETURN_NAMES = ("image_output_name",)

    FUNCTION = "execute"

    #OUTPUT_NODE = False

    CATEGORY = "TSKNodes"

    def execute(self, prepend, body, append, delimiter):
        output = prepend + delimiter + body + delimiter + append
        return (output,)

class SEGSToImageList:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "segs": ("SEGS", ),
                "image": ("IMAGE", ),
                "squared": ("BOOLEAN", {
                    "default": False,
                }),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    #RETURN_NAMES = ("image_output_name",)
    OUTPUT_IS_LIST = (True,)

    FUNCTION = "execute"

    #OUTPUT_NODE = False

    CATEGORY = "TSKNodes"

    # def check_lazy_status(self, prepend, body, append, delimiter):
    #     """
    #         Return a list of input names that need to be evaluated.

    #         This function will be called if there are any lazy inputs which have not yet been
    #         evaluated. As long as you return at least one field which has not yet been evaluated
    #         (and more exist), this function will be called again once the value of the requested
    #         field is available.

    #         Any evaluated inputs will be passed as arguments to this function. Any unevaluated
    #         inputs will have the value None.
    #     """
    #     return ["prepend", "body", "append", "delimiter"]

    def execute(self, segs, image, squared):
        results = list()
        max_image_crop = min(image.shape[2], image.shape[1])
        for seg in segs[1]:
            if (not squared) and (seg.cropped_image is not None):
                cropped_image = to_tensor(seg.cropped_image)
            elif (not squared) and (seg.cropped_image is None):
                cropped_image = to_tensor(crop_image(image, seg.crop_region))
            elif (squared):
                crop_region = seg.crop_region
                crop_region_width = crop_region[2] - crop_region[0]
                crop_region_height = crop_region[3] - crop_region[1]
                side_length = min(max(crop_region_width, crop_region_height), max_image_crop)
                new_x = max(crop_region[0] + crop_region_width/2 - side_length/2, 0)
                new_y = max(crop_region[1] + crop_region_height/2 - side_length/2, 0)
                new_x = new_x if (new_x + side_length < image.shape[2]) else 0
                new_y = new_y if (new_y + side_length < image.shape[1]) else 0
                crop_region[0] = new_x
                crop_region[1] = new_y
                crop_region[2] = new_x + side_length
                crop_region[3] = new_y + side_length
                cropped_image = to_tensor(crop_image(image, crop_region))
            else:
                cropped_image = empty_pil_tensor()

            results.append(cropped_image)

        if len(results) == 0:
            results.append(empty_pil_tensor())

        return (results,)
        #do some processing on the image, in this example I just invert it

TSK_CLASS_MAPPINGS = {
    "TSKStringWrapper": StringWrapper,
    "TSKSEGSToImageList": SEGSToImageList
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
TSK_DISPLAY_NAME_MAPPINGS = {
    "TSKStringWrapper": "TSK StringWrapper",
    "TSKSEGSToImageList": "TSK SEGSToImageList"
}
