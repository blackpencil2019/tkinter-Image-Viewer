# coding:utf8
# author:blackpencil2019@github

import tkinter as tk
from PIL import Image, ImageTk

class GV:
    IMGx = 720  # 3:2    非奇数, 图像窗口尺寸
    IMGy = 480
    IMGsx = 240  # 3:2   非奇数, 缩略图窗口尺寸
    IMGsy = 160
    PAD = 5
    pic_1 = r'sample.jpg'  # 需要显示的图片路径/名称--> IMAGE_1 & IMAGE_2
    IMAGE_1 = 1  # 更新到canvas的图像
    IMAGE_2 = 2  # 更新到canvas的缩略图
    origin_x0, origin_y0, originx, originy = 0, 0, 3000, 2000  # 鼠标点击时坐标（窗口坐标），显示窗口的中心点在原图上的坐标
    mapx, mapy = IMGsx / 2, IMGsy / 2  # 缩略图中心坐标
    errx, erry = 0, 0  # 记录相对运动引起的累积误差
    DRAG_GAIN = 2


class LargeImageViewer:
    def __init__(self, frame):
        self.sub1 = self.creatSubFrame(frame, GV.IMGx, GV.IMGy, 0, 0)
        self.updateCanvas(self.sub1)  # 便于更新图像，将其作为方法调用

    def creatSubFrame(self, frame, w=50, h=50, Row=0, Column=0, Rs=1, Cs=1):
        subframe = tk.Frame(frame, bg='white', height=h, width=w)
        subframe.propagate(False)
        subframe.grid(row=Row, column=Column, rowspan=Rs, columnspan=Cs)
        return subframe

    def updateCanvas(self, frame):
        self.cv1 = tk.Canvas(frame)
        self.cv1.configure(width=GV.IMGx, height=GV.IMGy)
        self.cv1.configure(bg='AliceBlue')
        self.cv1.grid(row=0, column=0, padx=GV.PAD, pady=GV.PAD)
        self.cv1.bind("<ButtonPress-1>", self.scroll_start)
        self.cv1.bind("<B1-Motion>", self.scroll_move)

        self.cv2 = tk.Canvas(frame)
        self.cv2.configure(width=GV.IMGsx, height=GV.IMGsy)
        self.cv2.configure(bg='gray')
        self.cv2.grid(row=0, column=0, padx=GV.PAD, pady=GV.PAD, sticky=tk.S + tk.E)
        self.cv2.bind("<ButtonPress-1>", self.map_scroll_move)
        self.cv2.bind("<B1-Motion>", self.map_scroll_move)

        if isinstance(GV.pic_1, str):
            img = Image.open(GV.pic_1)
        else:
            img = GV.pic_1
        GV.IMAGE_1 = ImageTk.PhotoImage(img, Image.ANTIALIAS)
        # print(type(GV.IMAGE_1))
        self.w, self.h, self.n, GV.IMAGE_2 = self.imageResize(img, GV.IMGsx, GV.IMGsy)
        width, height = int(self.w * self.n), int(self.h * self.n)
        self.mapa, self.mapb = int(width * GV.IMGx / (2 * self.w)), int(height * GV.IMGy / (2 * self.h))
        # print(GV.IMAGE_1)
        self.img1 = self.cv1.create_image(GV.IMGx / 2, GV.IMGy / 2, anchor="center", image=GV.IMAGE_1,
                                          state="disabled")
        print(GV.pic_1)
        self.img2 = self.cv2.create_image(GV.IMGsx / 2, GV.IMGsy / 2, anchor="center", image=GV.IMAGE_2,
                                          state="disabled")
        self.rect = self.cv2.create_rectangle((GV.IMGsx / 2 - self.mapa, GV.IMGsy / 2 - self.mapb,
                                               GV.IMGsx / 2 + self.mapa, GV.IMGsy / 2 + self.mapb),
                                              outline="yellow")

        GV.origin_x0, GV.origin_y0, GV.originx, GV.originy = 0, 0, self.w / 2, self.h / 2
        GV.errx, GV.erry, GV.mapx, GV.mapy = 0, 0, GV.IMGsx / 2, GV.IMGsy / 2

    def imageResize(self, pil_image, winw, winh):
        w, h = pil_image.size
        # print(w,h)
        n1 = 1.0 * winw / w
        n2 = 1.0 * winh / h
        n = min([n1, n2])
        width = int(w * n)
        height = int(h * n)
        # print(width, height)
        return w, h, n, ImageTk.PhotoImage(pil_image.resize((width, height), Image.ANTIALIAS))

    def map_scroll_move(self, event):
        map_dx, map_dy = GV.mapx - event.x, GV.mapy - event.y
        GV.mapx, GV.mapy = event.x, event.y
        self.cv2.move(self.rect, -map_dx, -map_dy)

        k1 = 1 / self.n
        # 消除累积误差
        x, y = int(map_dx * k1), int(map_dy * k1)
        x, GV.errx = int(x + GV.errx), x + GV.errx - int(x + GV.errx)
        y, GV.erry = int(y + GV.erry), y + GV.erry - int(y + GV.erry)

        GV.originx, GV.originy = GV.originx - map_dx * k1, GV.originy - map_dy * k1
        self.cv1.move(self.img1, x, y)
        # self.cv1.coords(self.img1, int(GV.originx), int(GV.originy))

    def scroll_start(self, event):
        self.cv1.scan_mark(event.x, event.y)
        # print(event.x,event.y)
        GV.origin_x0, GV.origin_y0 = event.x, event.y

    def scroll_move(self, event):
        self.cv1.scan_dragto(event.x, event.y, gain=GV.DRAG_GAIN)
        # print(event.x,event.y)
        origin_dx = (GV.origin_x0 - event.x) * GV.DRAG_GAIN
        origin_dy = (GV.origin_y0 - event.y) * GV.DRAG_GAIN
        GV.originx, GV.originy = GV.originx + origin_dx, GV.originy + origin_dy
        GV.origin_x0, GV.origin_y0 = event.x, event.y

        k2 = self.n
        GV.mapx, GV.mapy = GV.mapx + origin_dx * k2, GV.mapy + origin_dy * k2
        self.cv2.coords(self.rect, int(GV.mapx) - self.mapa, int(GV.mapy) - self.mapb, int(GV.mapx) + self.mapa,
                        int(GV.mapy) + self.mapb)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Large Image Viewer")
    root.resizable(0, 0)
    root.configure(background='white')

    LIV = LargeImageViewer(root)
    root.mainloop()