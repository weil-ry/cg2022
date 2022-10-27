#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QDialog,
    QFormLayout,
    QSpinBox,
    QMessageBox,
    QDialogButtonBox)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPen
from PyQt5.QtCore import QRectF


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.my_color = QColor(0, 0, 0)
        self.temp_pos = None  # 用于平移等的临时坐标

    def set_my_color(self, r: int, g: int, b: int):
        # 颜色的Alpha通道指定透明效果，0表示完全透明的颜色，而255表示完全不透明的颜色
        self.my_color.setRgb(r, g, b, 255)

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_circle(self, algorithm, item_id):
        self.status = 'circle'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self, algorithm, item_id):
        self.status = 'ellipse'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_translate(self):
        self.status = 'translate'

    def finish_draw(self):  # finish后得到下一个图元对应id
        self.temp_id = self.main_window.get_id()

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        if selected == '':
            return
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        if self.status == 'translate':  # 图元平移部分
            self.main_window.statusBar().showMessage('图元平移： %s' % selected)
            self.selected_id = selected
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
            self.updateScene([self.sceneRect()])
            return
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.setMouseTracking(True)
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            if self.temp_item is None:
                temp_color = QColor(self.my_color)
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, None, temp_color)
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list[-1] = [x, y]
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
                self.temp_item = None
        elif self.status == 'polygon':
            if self.temp_item is None:
                temp_color = QColor(self.my_color)
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, None, temp_color)
                self.scene().addItem(self.temp_item)
            else:
                self.temp_item.p_list[-1] = [x, y]
                if ((y - self.temp_item.p_list[0][1]) ** 2 + (x - self.temp_item.p_list[0][0]) ** 2) <= 64:  # ? 多边形终点
                    self.temp_item.p_list[-1] = self.temp_item.p_list[0]
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
                    self.temp_item = None  # ?
                else:
                    self.temp_item.p_list += [[x, y]]
        elif self.status == 'circle':  # list[0]是圆心 list[1][1]是半径
            if self.temp_item is None:
                temp_color = QColor(self.my_color)
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [0, 0]], self.temp_algorithm, None, temp_color)
                self.scene().addItem(self.temp_item)
            else:
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
                self.temp_item = None
        elif self.status == 'ellipse':  # list[0]是椭圆中心 list[1][0]是长半轴 list[1][1]是短半轴
            if self.temp_item is None:
                temp_color = QColor(self.my_color)
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [0, 0]], self.temp_algorithm, None, temp_color)
                self.scene().addItem(self.temp_item)
            else:
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()
                self.temp_item = None

        if self.status == 'translate':
            if self.selected_id in self.item_dict.keys() and self.item_dict[self.selected_id].boundingRect().contains(x, y):  # 选中的矩形区域包含该点
                if self.temp_pos is None:  # 起始点
                    self.temp_pos = [x, y]
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' and self.temp_item is not None:
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon' and self.temp_item is not None:
            self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'circle' and self.temp_item is not None:
            r = int(((y - self.temp_item.p_list[0][1]) ** 2 + (x - self.temp_item.p_list[0][0]) ** 2) ** (1 / 2))
            self.temp_item.p_list[-1] = [0, r]
        elif self.status == 'ellipse' and self.temp_item is not None:
            rx = int(abs(x - self.temp_item.p_list[0][0]))
            ry = int(abs(y - self.temp_item.p_list[0][1]))
            self.temp_item.p_list[-1] = [rx,ry]

        if self.status == 'translate':
            if self.temp_pos is not None:  # 有起始点
                self.item_dict[self.selected_id].offset[0] += x - self.temp_pos[0]
                self.item_dict[self.selected_id].offset[1] += y - self.temp_pos[1]
                self.temp_pos = [x, y]  # 注意！在每次更新后起始点都应变更，否则会产生重复计算
                self.item_dict[self.selected_id].update()  # update paint
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """
        if self.status == 'line':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
            self.temp_item = None   # ?
        """
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'translate':
            if self.temp_pos is not None:  # 有起始点
                self.item_dict[self.selected_id].offset[0] += x - self.temp_pos[0]
                self.item_dict[self.selected_id].offset[1] += y - self.temp_pos[1]
                self.temp_pos = [x, y]
                self.item_dict[self.selected_id].update()  # update paint
                self.temp_pos = None
        super().mouseReleaseEvent(event)

    def clear_paint(self):
        self.scene().clear()
        self.item_dict.clear()
        self.selected_id = ''
        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', parent: QGraphicsItem = None,
                 mycolor: QColor = QColor(0, 0, 0)):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.Pencolor = mycolor
        self.offset = [0, 0]

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        # 自己的tips：在item调用update时，图元会自动再次调用paint函数，此时selected项就有意义了
        pen = QPen(self.Pencolor, 2)  # 画笔颜色/字体大小
        painter.setPen(pen)
        item_pixels = None
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
        elif self.item_type == 'circle':
            item_pixels = alg.draw_circle(self.p_list, self.algorithm)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
        for i in item_pixels:
            p = [i[0], i[1]]
            p[0] += self.offset[0]
            p[1] += self.offset[1]
            painter.drawPoint(*p)
        if self.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:  # 返回该项目所绘制区域的估计值
        x, y, w, h = None, None, None, None
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
        elif self.item_type == 'polygon':
            x_list = []
            y_list = []
            for i in self.p_list:
                x_list += [i[0]]
                y_list += [i[1]]
            x = min(x_list)
            y = min(y_list)
            w = max(x_list) - x
            h = max(y_list) - y
        elif self.item_type == 'circle':
            x = self.p_list[0][0]-self.p_list[1][1]
            y = self.p_list[0][1]-self.p_list[1][1]
            w = 2 * self.p_list[1][1]
            h = 2 * self.p_list[1][1]
        elif self.item_type == 'ellipse':
            x = self.p_list[0][0] - self.p_list[1][0]
            y = self.p_list[0][1] - self.p_list[1][1]
            w = 2 * self.p_list[1][0]
            h = 2 * self.p_list[1][1]
        elif self.item_type == 'curve':
            pass

        return QRectF(x - 1 + self.offset[0], y - 1 + self.offset[1], w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 1

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 600, 600)   # 对应窗口的坐标系统，宽高 ; 这是图在的实际窗口
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(600, 600)  # 这是框住画布的界面，要改fixed
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        circle_act = draw_menu.addAction('圆')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        exit_act.triggered.connect(qApp.quit)

        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)

        circle_act.triggered.connect(self.circle_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)

        translate_act.triggered.connect(self.translate_action)


        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(600, 600)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        self.item_cnt += 1
        _id = str(self.item_cnt)
        return _id

    def set_pen_action(self):
        dialog = QDialog(self)
        dialog.setFixedSize(350,200)  # 设置对话框固定大小
        dialog.setWindowTitle('Set Pen Color')  # 设置窗口标题
        int1_dia = QSpinBox(self)  # 计数器控件
        int1_dia.setRange(0, 255)
        int2_dia = QSpinBox(self)
        int2_dia.setRange(0, 255)
        int3_dia = QSpinBox(self)
        int3_dia.setRange(0, 255)
        formlayout = QFormLayout(dialog)  # 布局
        formlayout.addRow('R :', int1_dia)
        formlayout.addRow('G : ', int2_dia)
        formlayout.addRow('B : ', int3_dia)
        button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        formlayout.addWidget(button)
        dialog.show()
        button.accepted.connect(dialog.accept)
        button.rejected.connect(dialog.reject)
        # 调用exec时点ok返回1，取消返回0
        if dialog.exec() == QDialog.Accepted:
            r = int1_dia.value()
            g = int2_dia.value()
            b = int3_dia.value()
            print('R is ', r, '&& G is ', g, '&& B is ', b)
            self.canvas_widget.set_my_color(r, g, b)

    def reset_canvas_action(self):
        self.statusBar().showMessage('画布已重置')
        self.item_cnt = 1
        self.list_widget.clear()
        self.canvas_widget.clear_paint()
        # 重设画布大小
        dialog = QDialog(self)
        dialog.setFixedSize(550, 200)  # 设置对话框固定大小
        dialog.setWindowTitle('重设画布宽高(0-1000)(或保持默认)')  # 设置窗口标题
        width_ = QSpinBox(self)  # 计数器控件
        width_.setRange(0, 1000)
        width_.setValue(600)
        height_ = QSpinBox(self)
        height_.setRange(0, 1000)
        height_.setValue(600)
        formlayout = QFormLayout(dialog)  # 布局
        formlayout.addRow('width :', width_)
        formlayout.addRow('height : ', height_)
        button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        formlayout.addWidget(button)
        dialog.show()
        button.accepted.connect(dialog.accept)  # 将ok|cancel的点击与对应变量关联起来
        button.rejected.connect(dialog.reject)
        if dialog.exec() == QDialog.Accepted:  # 若点击的是ok
            w = width_.value()
            h = height_.value()
            print('width is ', w, '&& height is ', h)
            self.scene.setSceneRect(0, 0, w, h)
            self.canvas_widget.setFixedSize(w, h)
            if w > self.width():
                self.resize(w, self.height())
            if h > self.height():
                self.resize(self.width(), h)

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', str(self.item_cnt))
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', str(self.item_cnt))
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', str(self.item_cnt))
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', str(self.item_cnt))
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', str(self.item_cnt))
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def circle_action(self):
        self.canvas_widget.start_draw_circle('Circle', str(self.item_cnt))
        self.statusBar().showMessage('绘制圆形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse('Ellipse', str(self.item_cnt))
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        pass

    def curve_b_spline_action(self):
        pass

    def translate_action(self):
        QMessageBox.information(self,"平移功能提示","请先选中图元对应id，\n之后点击选中区域即可拖动进行平移",QMessageBox.Yes|QMessageBox.No)
        self.canvas_widget.start_translate()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
