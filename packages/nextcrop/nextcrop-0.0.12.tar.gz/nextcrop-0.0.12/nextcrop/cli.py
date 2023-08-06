class CLI:
    def __init__(self, crop, image_loader, image_saver):
        self.crop = crop
        self.image_loader = image_loader
        self.image_saver = image_saver

    def run(self, crop_border):
        for input_image in self.image_loader:
            cropped_images, _, _ = self.crop.run(input_image)
            self.image_saver.save_images(cropped_images)



