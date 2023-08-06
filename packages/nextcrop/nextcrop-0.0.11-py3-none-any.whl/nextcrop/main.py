from nextcrop import Control


# def crop_image(image):
#     bkg = crop.Background()
#
#     window_name = 'Background'
#     cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
#     cv2.createTrackbar('Spread', window_name, bkg.spread, 50,
#                        lambda pos: crop.onchange_threshold(pos, image, bkg, window_name))
#     cv2.createTrackbar('Gaussian', window_name, bkg.gaussian_filter, 50,
#                        lambda pos: crop.onchange_gaussian_filter(pos, image, bkg, window_name))
#
#     # cv2.imshow('input', im)
#
#     # initial
#     cv2.imshow(window_name, bkg.run(image.copy()))
#
#     # resize_window(im, 'input')
#     crop.resize_window(image, window_name)
#     cv2.waitKey(0)


def main():
    ctrl = Control()
    ctrl.run()


main()
