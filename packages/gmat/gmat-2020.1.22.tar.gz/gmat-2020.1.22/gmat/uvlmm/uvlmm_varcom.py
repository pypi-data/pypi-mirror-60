import numpy as np
from functools import reduce
import gc
import logging


def em_mme(y, xmat, gmat_inv, init=None, maxiter=100, cc=1.0e-8):
    var_com = [1.0, 1.0]
    if init is not None:
        var_com = init[:]
    var_com_new = var_com[:]
    # 准备不含方差组分的系数矩阵
    xmat_df, gmat_inv_df = xmat.shape[1], gmat_inv.shape[0]
    y_df = len(y)
    coef_pre = np.identity(xmat_df+gmat_inv_df)
    coef_pre[:xmat_df, :xmat_df] = np.dot(xmat.T, xmat)
    coef_pre[:xmat_df, xmat_df:] = xmat.T
    coef_pre[xmat_df:, :xmat_df] = xmat
    w_mat = np.concatenate((xmat, np.identity(gmat_inv_df)), axis=1)
    # 开始迭代
    iter = 0
    cc_val = 100.0
    while iter < maxiter:
        iter += 1
        print('Round: ', iter)
        # 系数矩阵
        coef = coef_pre/var_com[1]
        coef[xmat_df:, xmat_df:] = coef[xmat_df:, xmat_df:] + gmat_inv/var_com[0]
        # 右手项
        rhs_mat = np.dot(w_mat.T, y)/var_com[1]
        coef_inv = np.linalg.inv(coef)
        eff = np.dot(coef_inv, rhs_mat)
        var_com_new[0] = np.dot(eff[xmat_df:], np.dot(gmat_inv, eff[xmat_df:])) + \
                     np.trace(np.dot(gmat_inv, coef_inv[xmat_df:, xmat_df:]))
        var_com_new[0] = var_com_new[0]/gmat_inv_df
        e_hat = y - np.dot(xmat, eff[:xmat_df]) - eff[xmat_df:]
        var_com_new[1] = np.dot(e_hat, e_hat) + np.trace(np.dot(w_mat, np.dot(coef_inv, w_mat.T)))
        var_com_new[1] = var_com_new[1]/y_df
        print('Updated variances:', var_com_new)
        delta = np.array(var_com_new) - np.array(var_com)
        cc_val = np.sum(delta*delta)/np.sum(np.array(var_com_new)*np.array(var_com_new))
        cc_val = np.sqrt(cc_val)
        var_com = var_com_new[:]
        if cc_val < cc:
            break
    if cc_val < cc:
        print('Variances converged.')
    else:
        print('Variances not converged.')
    return var_com


def pxem_mme(y, xmat, gmat_inv, init=None, maxiter=100, cc=1.0e-8):
    var_com = [1.0, 1.0]
    if init is not None:
        var_com = init[:]
    var_com_new = var_com[:]
    # 准备不含方差组分的系数矩阵
    xmat_df, gmat_inv_df = xmat.shape[1], gmat_inv.shape[0]
    y_df = len(y)
    coef_pre = np.identity(xmat_df+gmat_inv_df)
    coef_pre[:xmat_df, :xmat_df] = np.dot(xmat.T, xmat)
    coef_pre[:xmat_df, xmat_df:] = xmat.T
    coef_pre[xmat_df:, :xmat_df] = xmat
    w_mat = np.concatenate((xmat, np.identity(gmat_inv_df)), axis=1)
    # 开始迭代
    iter = 0
    cc_val = 100.0
    while iter < maxiter:
        iter += 1
        print('Round: ', iter)
        # 系数矩阵
        coef = coef_pre/var_com[1]
        coef[xmat_df:, xmat_df:] = coef[xmat_df:, xmat_df:] + gmat_inv/var_com[0]
        # 右手项
        rhs_mat = np.dot(w_mat.T, y)/var_com[1]
        coef_inv = np.linalg.inv(coef)
        eff = np.dot(coef_inv, rhs_mat)
        var_com_new[0] = np.dot(eff[xmat_df:], np.dot(gmat_inv, eff[xmat_df:])) + \
                     np.trace(np.dot(gmat_inv, coef_inv[xmat_df:, xmat_df:]))
        var_com_new[0] = var_com_new[0]/gmat_inv_df
        e_hat = y - np.dot(xmat, eff[:xmat_df]) - eff[xmat_df:]
        var_com_new[1] = np.dot(e_hat, e_hat) + np.trace(np.dot(w_mat, np.dot(coef_inv, w_mat.T)))
        var_com_new[1] = var_com_new[1]/y_df
        gamma1 = np.dot(eff[xmat_df:], y - np.dot(xmat, eff[:xmat_df])) - np.trace(np.dot(xmat, coef_inv[:xmat_df, xmat_df:]))
        gamma2 = np.dot(eff[xmat_df:], eff[xmat_df:]) + np.trace(coef_inv[xmat_df:, xmat_df:])
        gamma = gamma1/gamma2
        var_com_new[0] = var_com_new[0]*gamma*gamma
        print('Updated variances:', var_com_new)
        delta = np.array(var_com_new) - np.array(var_com)
        cc_val = np.sum(delta*delta)/np.sum(np.array(var_com_new)*np.array(var_com_new))
        cc_val = np.sqrt(cc_val)
        var_com = var_com_new[:]
        if cc_val < cc:
            break
    if cc_val < cc:
        print('Variances converged.')
    else:
        print('Variances not converged.')
    return var_com


def ai_mme(y, xmat, gmat_inv, init=None, maxiter=100, cc=1.0e-8):
    var_com = [1.0, 1.0]
    if init is not None:
        var_com = init[:]
    var_com = np.array(var_com)
    # 准备不含方差组分的系数矩阵
    xmat_df, gmat_inv_df = xmat.shape[1], gmat_inv.shape[0]
    y_df = len(y)
    coef_pre = np.identity(xmat_df + gmat_inv_df)
    coef_pre[:xmat_df, :xmat_df] = np.dot(xmat.T, xmat)
    coef_pre[:xmat_df, xmat_df:] = xmat.T
    coef_pre[xmat_df:, :xmat_df] = xmat
    w_mat = np.concatenate((xmat, np.identity(gmat_inv_df)), axis=1)
    # 开始迭代
    iter = 0
    cc_val = 100.0
    fd_mat = np.zeros(2)
    # ai_mat = np.zeros((2, 2))
    while iter < maxiter:
        iter += 1
        print('Round: ', iter)
        # 系数矩阵
        coef = coef_pre/var_com[1]
        coef[xmat_df:, xmat_df:] = coef[xmat_df:, xmat_df:] + gmat_inv/var_com[0]
        # 右手项
        rhs_mat = np.dot(w_mat.T, y)/var_com[1]
        coef_inv = np.linalg.inv(coef)
        eff = np.dot(coef_inv, rhs_mat)
        e_hat = y - np.dot(xmat, eff[:xmat_df]) - eff[xmat_df:]
        fd_mat[0] = gmat_inv_df/var_com[0] - np.trace(np.dot(coef_inv[xmat_df:, xmat_df:], gmat_inv))/(var_com[0]*var_com[0]) - \
            np.dot(eff[xmat_df:], np.dot(gmat_inv, eff[xmat_df:]))/(var_com[0]*var_com[0])
        fd_mat[1] = y_df/var_com[1] - np.trace(np.dot(np.dot(coef_inv, w_mat.T), w_mat))/(var_com[1]*var_com[1]) - \
            np.dot(e_hat, e_hat)/(var_com[1]*var_com[1])
        fd_mat = -0.5*fd_mat
        h_mat1 = np.array(eff[xmat_df:]/var_com[0]).reshape(gmat_inv_df, 1)
        h_mat2 = np.array(e_hat / var_com[1]).reshape(y_df, 1)
        h_mat = np.concatenate((h_mat1, h_mat2), axis=1)
        qrq = np.divide(np.dot(h_mat.T, h_mat), var_com[-1])
        left = np.divide(np.dot(w_mat.T, h_mat), var_com[-1])
        eff_h_mat = np.dot(coef_inv, left)
        ai_mat = np.subtract(qrq, np.dot(left.T, eff_h_mat))
        ai_mat = 0.5 * ai_mat
        ai_mat_inv = np.linalg.inv(ai_mat)
        var_com_new = var_com + np.dot(ai_mat_inv, fd_mat)
        print('Updated variances:', var_com_new)
        delta = np.array(var_com_new) - np.array(var_com)
        cc_val = np.sum(delta * delta) / np.sum(np.array(var_com_new) * np.array(var_com_new))
        cc_val = np.sqrt(cc_val)
        var_com = var_com_new[:]
        if cc_val < cc:
            break
    if cc_val < cc:
        print('Variances converged.')
    else:
        print('Variances not converged.')
    return var_com


def emai_mme(y, xmat, gmat_inv, init=None, maxiter=100, cc=1.0e-8):
    var_com = [1.0, 1.0]
    if init is not None:
        var_com = init[:]
    var_com = np.array(var_com)
    var_com_new = var_com[:]
    # 准备不含方差组分的系数矩阵
    xmat_df, gmat_inv_df = xmat.shape[1], gmat_inv.shape[0]
    y_df = len(y)
    coef_pre = np.identity(xmat_df + gmat_inv_df)
    coef_pre[:xmat_df, :xmat_df] = np.dot(xmat.T, xmat)
    coef_pre[:xmat_df, xmat_df:] = xmat.T
    coef_pre[xmat_df:, :xmat_df] = xmat
    w_mat = np.concatenate((xmat, np.identity(gmat_inv_df)), axis=1)
    # 开始迭代
    iter = 0
    cc_val = 100.0
    fd_mat = np.zeros(2)
    em_mat = np.zeros((2, 2))
    while iter < maxiter:
        iter += 1
        print('Round: ', iter)
        # 系数矩阵
        coef = coef_pre/var_com[1]
        coef[xmat_df:, xmat_df:] = coef[xmat_df:, xmat_df:] + gmat_inv/var_com[0]
        # 右手项
        rhs_mat = np.dot(w_mat.T, y)/var_com[1]
        coef_inv = np.linalg.inv(coef)
        eff = np.dot(coef_inv, rhs_mat)
        e_hat = y - np.dot(xmat, eff[:xmat_df]) - eff[xmat_df:]
        fd_mat[0] = gmat_inv_df/var_com[0] - np.trace(np.dot(coef_inv[xmat_df:, xmat_df:], gmat_inv))/(var_com[0]*var_com[0]) - \
            np.dot(eff[xmat_df:], np.dot(gmat_inv, eff[xmat_df:]))/(var_com[0]*var_com[0])
        fd_mat[1] = y_df/var_com[1] - np.trace(np.dot(np.dot(coef_inv, w_mat.T), w_mat))/(var_com[1]*var_com[1]) - \
            np.dot(e_hat, e_hat)/(var_com[1]*var_com[1])
        fd_mat = -0.5*fd_mat
        h_mat1 = np.array(eff[xmat_df:]/var_com[0]).reshape(gmat_inv_df, 1)
        h_mat2 = np.array(e_hat / var_com[1]).reshape(y_df, 1)
        h_mat = np.concatenate((h_mat1, h_mat2), axis=1)
        qrq = np.divide(np.dot(h_mat.T, h_mat), var_com[-1])
        left = np.divide(np.dot(w_mat.T, h_mat), var_com[-1])
        eff_h_mat = np.dot(coef_inv, left)
        ai_mat = np.subtract(qrq, np.dot(left.T, eff_h_mat))
        ai_mat = 0.5 * ai_mat
        print(fd_mat, ai_mat)
        em_mat[0, 0] = gmat_inv_df / (var_com[0] * var_com[0])
        em_mat[1, 1] = y_df / (var_com[1] * var_com[1])
        for j in range(0, 51):
            weight = j * 0.1
            wemai_mat = (1 - weight) * ai_mat + weight * em_mat
            delta = np.dot(np.linalg.inv(wemai_mat), fd_mat)
            var_com_new = var_com + delta
            if min(var_com_new) > 0:
                print('EM weight value:', weight)
                break
        print('Updated variances:', var_com_new)
        delta = np.array(var_com_new) - np.array(var_com)
        cc_val = np.sum(delta * delta) / np.sum(np.array(var_com_new) * np.array(var_com_new))
        cc_val = np.sqrt(cc_val)
        var_com = var_com_new[:]
        if cc_val < cc:
            break
    if cc_val < cc:
        print('Variances converged.')
    else:
        print('Variances not converged.')
    return var_com


def pxemai_mme(y, xmat, gmat_inv, init=None, maxiter=100, cc=1.0e-8):
    var_com = [1.0, 1.0]
    if init is not None:
        var_com = init[:]
    var_com = np.array(var_com)
    var_com_new = var_com[:]
    # 准备不含方差组分的系数矩阵
    xmat_df, gmat_inv_df = xmat.shape[1], gmat_inv.shape[0]
    y_df = len(y)
    coef_pre = np.identity(xmat_df + gmat_inv_df)
    coef_pre[:xmat_df, :xmat_df] = np.dot(xmat.T, xmat)
    coef_pre[:xmat_df, xmat_df:] = xmat.T
    coef_pre[xmat_df:, :xmat_df] = xmat
    w_mat = np.concatenate((xmat, np.identity(gmat_inv_df)), axis=1)
    # 开始迭代
    iter = 0
    cc_val = 100.0
    weight = 0.0
    fd_mat = np.zeros(2)
    em_mat = np.zeros((2, 2))
    while iter < maxiter:
        iter += 1
        print('Round: ', iter)
        # 系数矩阵
        coef = coef_pre/var_com[1]
        coef[xmat_df:, xmat_df:] = coef[xmat_df:, xmat_df:] + gmat_inv/var_com[0]
        # 右手项
        rhs_mat = np.dot(w_mat.T, y)/var_com[1]
        coef_inv = np.linalg.inv(coef)
        eff = np.dot(coef_inv, rhs_mat)
        e_hat = y - np.dot(xmat, eff[:xmat_df]) - eff[xmat_df:]
        fd_mat[0] = gmat_inv_df/var_com[0] - np.trace(np.dot(coef_inv[xmat_df:, xmat_df:], gmat_inv))/(var_com[0]*var_com[0]) - \
            np.dot(eff[xmat_df:], np.dot(gmat_inv, eff[xmat_df:]))/(var_com[0]*var_com[0])
        fd_mat[1] = y_df/var_com[1] - np.trace(np.dot(np.dot(coef_inv, w_mat.T), w_mat))/(var_com[1]*var_com[1]) - \
            np.dot(e_hat, e_hat)/(var_com[1]*var_com[1])
        fd_mat = -0.5*fd_mat
        h_mat1 = np.array(eff[xmat_df:]/var_com[0]).reshape(gmat_inv_df, 1)
        h_mat2 = np.array(e_hat / var_com[1]).reshape(y_df, 1)
        h_mat = np.concatenate((h_mat1, h_mat2), axis=1)
        qrq = np.divide(np.dot(h_mat.T, h_mat), var_com[-1])
        left = np.divide(np.dot(w_mat.T, h_mat), var_com[-1])
        eff_h_mat = np.dot(coef_inv, left)
        ai_mat = np.subtract(qrq, np.dot(left.T, eff_h_mat))
        ai_mat = 0.5 * ai_mat
        print(fd_mat, ai_mat)
        em_mat[0, 0] = gmat_inv_df / (var_com[0] * var_com[0])
        em_mat[1, 1] = y_df / (var_com[1] * var_com[1])
        for j in range(0, 51):
            weight = j * 0.1
            wemai_mat = (1 - weight) * ai_mat + weight * em_mat
            delta = np.dot(np.linalg.inv(wemai_mat), fd_mat)
            var_com_new = var_com + delta
            if min(var_com_new) > 0:
                print('EM weight value:', weight)
                break
        if weight > 0.001:
            gamma1 = np.dot(eff[xmat_df:], y - np.dot(xmat, eff[:xmat_df])) - np.trace(
                np.dot(xmat, coef_inv[:xmat_df, xmat_df:]))
            gamma2 = np.dot(eff[xmat_df:], eff[xmat_df:]) + np.trace(coef_inv[xmat_df:, xmat_df:])
            gamma = gamma1 / gamma2
            var_com_new[0] = var_com_new[0] * gamma * gamma
        print('Updated variances:', var_com_new)
        delta = np.array(var_com_new) - np.array(var_com)
        cc_val = np.sum(delta * delta) / np.sum(np.array(var_com_new) * np.array(var_com_new))
        cc_val = np.sqrt(cc_val)
        var_com = var_com_new[:]
        if cc_val < cc:
            break
    if cc_val < cc:
        print('Variances converged.')
    else:
        print('Variances not converged.')
    return var_com


def wemai_multi_gmat(y, xmat, zmat, gmat_lst, init=None, maxiter=100, cc=1.0e-8):
    """
    # 单性状多关系矩阵利用EM和AI加权方法估计方差组分
    :param y: 表型向量
    :param xmat: 固定效应设计矩阵
    :param gmat_lst: 关系矩阵列表
    :param zmat: 随机效应设计矩阵，csr稀疏矩阵
    :param init: 初始值
    :param maxiter: 迭代次数
    :param cc: 收敛标准
    :return: 方差组分估计值
    """
    logging.info("预处理")
    var_com = [1.0]*(len(gmat_lst)+1)
    if init is not None:
        var_com = init[:]
    var_com = np.array(var_com)
    var_com_new = var_com[:]
    y = np.array(y).reshape(-1, 1)
    n = y.shape[0]
    xmat = np.array(xmat).reshape(n, -1)
    logging.info("设置迭代初值")
    for val in range(len(gmat_lst)):
        gmat_lst[val] = zmat.dot((zmat.dot(gmat_lst[val])).T)
    iter = 0
    delta = 1000.0
    cc_val = 1000.0
    logging.info("开始迭代")
    while iter < maxiter:
        iter += 1
        logging.info('Round: ' + str(iter))
        # 计算V和其逆
        vmat = np.diag([var_com[-1]]*n)
        for val in range(len(gmat_lst)):
            vmat += gmat_lst[val]*var_com[val]
        vmat = np.linalg.inv(vmat)
        # 计算P矩阵
        vxmat = np.dot(vmat, xmat)
        xvxmat = np.dot(xmat.T, vxmat)
        xvxmat = np.linalg.inv(xvxmat)
        pmat = reduce(np.dot, [vxmat, xvxmat, vxmat.T])
        pmat = vmat - pmat
        pymat = np.dot(pmat, y)
        del vmat, vxmat, xvxmat
        gc.collect()
        # 计算一阶偏导、工具变量
        fd_mat = []
        wv_mat = []
        for val in range(len(gmat_lst)):
            fd_mat_val = -np.trace(np.dot(pmat, gmat_lst[val])) + reduce(np.dot, [pymat.T, gmat_lst[val], pymat])
            fd_mat.append(0.5*np.sum(fd_mat_val))
            wv_mat.append(np.dot(gmat_lst[val], pymat))
        fd_mat_val = -np.trace(pmat) + np.dot(pymat.T, pymat)
        fd_mat.append(0.5 * np.sum(fd_mat_val))
        fd_mat = np.array(fd_mat)
        wv_mat.append(pymat)
        wv_mat = np.concatenate(wv_mat, axis=1)
        del pymat
        gc.collect()
        # AI矩阵
        ai_mat = 0.5*reduce(np.dot, [wv_mat.T, pmat, wv_mat])
        del wv_mat, pmat
        gc.collect()
        em_mat = []
        for val in var_com:
            em_mat.append(n/(val*val))
        em_mat = np.diag(em_mat)
        for j in range(0, 51):
            weight = j * 0.02
            wemai_mat = (1 - weight) * ai_mat + weight * em_mat
            delta = np.dot(np.linalg.inv(wemai_mat), fd_mat)
            var_com_new = var_com + delta
            if min(var_com_new) > 0:
                logging.info('EM weight value: ' + str(weight))
                break
        logging.info('Updated variances: ' + ' '.join(list(np.array(var_com_new, dtype=str))))
        cc_val = np.sum(delta * delta) / np.sum(var_com_new * var_com_new)
        cc_val = np.sqrt(cc_val)
        var_com = var_com_new[:]
        if cc_val < cc:
            break
    if cc_val < cc:
        logging.info('Variances converged.')
    else:
        logging.info('Variances not converged.')
    return var_com
