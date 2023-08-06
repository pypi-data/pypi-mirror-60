from numba import jit
import numpy as np

@jit(nopython=True)
def pool2D(n_ex,out_rows,out_cols, out_ch,X_pad,s,fr,fc,Y,mode):

    for m in range(n_ex):
        for i in range(out_rows):
            for j in range(out_cols):
                for c in range(out_ch):
                    # calculate window boundaries, incorporating stride
                    i0, i1 = i * s, (i * s) + fr
                    j0, j1 = j * s, (j * s) + fc

                    xi = X_pad[m, i0:i1, j0:j1, c]
                    if mode == "max":
                        Y[m, i, j, c] = np.max(xi)
                    elif mode == "average":
                        Y[m, i, j, c] = np.mean(xi)
    return Y
