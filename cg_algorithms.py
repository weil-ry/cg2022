#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        if x0 == x1:
            y0, y1 = (y1, y0) if y0 > y1 else (y0, y1)
            for y in range(y0, y1+1):
                result.append((x0, y))
        else:
            m = (y1 - y0) / (x1 - x0)
            if abs(m) <= 1:
                if x0 > x1:  # left
                    x0, y0, x1, y1 = x1, y1, x0, y0
                for x in range(x0, x1 + 1):
                    result.append((x, int(y0 + m * (x - x0))))
            else:
                if y0 > y1:  # up
                    x0, y0, x1, y1 = x1, y1, x0, y0
                for y in range(y0, y1 + 1):
                    result.append((int(x0 + (1/m) * (y - y0)), y))
    elif algorithm == 'Bresenham':
        if x0 == x1:
            y0, y1 = (y1, y0) if y0 > y1 else (y0, y1)
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            dy = (y1 - y0) if (y1 - y0) > 0 else -1 * (y1 - y0)
            dx = (x1 - x0) if (x1 - x0) > 0 else -1 * (x1 - x0)
            m = dy / dx
            if m <= 1:
                if x0 > x1:  # left
                    x0, y0, x1, y1 = x1, y1, x0, y0
                yk = y0
                p = 2 * dy - dx
                t = 1 if y0 < y1 else -1
                for x in range(x0, x1 + 1):
                    result.append((x, yk))
                    if p >= 0:
                        yk = yk + t
                        p = p + 2 * dy - 2 * dx
                    else:
                        p = p + 2 * dy
            else:
                if y0 > y1:  # left
                    x0, y0, x1, y1 = x1, y1, x0, y0
                xk = x0
                p = 2 * dx - dy
                t = 1 if x0 < x1 else -1
                for y in range(y0, y1 + 1):
                    result.append((xk, y))
                    if p >= 0:
                        xk = xk + t
                        p = p + 2 * dx - 2 * dy
                    else:
                        p = p + 2 * dx
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list) - 1):
        line = draw_line([p_list[i], p_list[i + 1]], algorithm)
        result += line
    if ((p_list[-1][0] - p_list[0][0]) ** 2 + (p_list[-1][1] - p_list[0][1]) ** 2) <= 64:
        result += draw_line([p_list[-1], p_list[0]], algorithm)
    return result


def draw_circle(p_list, algorithm):
    """绘制圆（采用中点圆生成算法）
    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 圆的圆心坐标和半径[0,r]
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    r = p_list[1][1]  # int
    p = 5/4 - r
    result = []
    yk = r
    for x in range(0, r):
        if x > yk:
            break
        result.append([x, yk])
        if p < 0:
            p = p + 2*(x+1) + 1
        else:
            p = p + 2 * (x + 1) + 1 - 2 * (yk - 1)
            yk = yk - 1
    # x,y取反，关于y=x对称
    temp = []
    for i in result:
        temp += [[i[1],i[0]]]
    result += temp
    # y取反，关于x轴对称
    temp = []
    for i in result:
        temp += [[i[0], -1 * i[1]]]
    result += temp
    # x取反，关于y轴对称
    temp = []
    for i in result:
        temp += [[-1 * i[0], i[1]]]
    result += temp
    for i in range(len(result)):
        result[i][0] += x0
        result[i][1] += y0
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）
    :param p_list: (list of list of int: [[x0, y0], [a, b]]) 椭圆的中心点和长短半轴
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    rx, ry = p_list[1]
    # 区域一绘制（切线斜率小于1）
    p1 = ry**2 - (rx**2)*ry + (rx**2)/4
    result = []
    xk = 0
    yk = ry
    for x in range(0, rx):
        if (ry**2)*x >= (rx**2)*yk:
            xk = x
            break
        result.append([x, yk])
        if p1 < 0:
            p1 = p1 + 2*(ry**2)*(x+1) + (ry**2)
        else:
            p1 = p1 + 2*(ry**2)*(x+1) + (ry**2) - 2*(rx**2)*(yk-1)
            yk = yk - 1
    # 区域二绘制（切线斜率大于1）
    p2 = (ry**2)*((xk+1/2)**2) + (rx**2)*((yk-1)**2) - (rx**2)*(ry**2)
    while yk > 0:
        result.append([xk, yk])
        if p2 > 0:
            p2 = p2 - 2*(rx**2)*(yk-1) + (rx**2)
        else:
            p2 = p2 - 2*(rx**2)*(yk-1) + (rx**2) + 2*(ry**2)*(xk+1)
            xk = xk + 1
        yk -= 1
    result.append([rx, 0])
    # y取反，关于x轴对称
    temp = []
    for i in result:
        temp += [[i[0], -1 * i[1]]]
    result += temp
    # x取反，关于y轴对称
    temp = []
    for i in result:
        temp += [[-1 * i[0], i[1]]]
    result += temp
    for i in range(len(result)):
        result[i][0] += x0
        result[i][1] += y0
    return result


def draw_curve(p_list, algorithm):
    """绘制曲线
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Bezier':
        pass
    elif algorithm == 'B_spline':
        pass
    return result


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for i in p_list:
        p = [i[0], i[1]]
        result.append([p[0] + dx, p[1] + dy])
    return result


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    pass


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    pass
