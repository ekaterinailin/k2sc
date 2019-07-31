from numpy import isfinite, nan, median, abs, ones_like, where, rint, sqrt

def fold(time, period, origo=0.0, shift=0.0, normalize=True):
    """Folds the given data over a given period.
    """
    tf = ((time - origo)/period + shift) % 1.
    return tf if normalize else tf*period


def medsig(a):
    """Return median and outlier-robust estimate of standard deviation
       (1.48 x median of absolute deviations).
    """
    l = isfinite(a)
    nfinite = l.sum()
    if nfinite == 0:
        return nan, nan
    if nfinite == 1:
        return a[l], nan
    med = median(a[l])
    sig = 1.48 * median(abs(a[l] - med))
    return med, sig


def sigma_clip(a, max_iter=10, max_sigma=5, separate_masks=False, mexc=None):
    """Iterative sigma-clipping routine that separates not finite points, and down- and upwards outliers.
    """
    
    # perform sigma-clipping on finite points only, or custom indices given by mexc
    mexc  = isfinite(a) if mexc is None else isfinite(a) & mexc
    
    #init different masks for up- and downward outliers
    mhigh = ones_like(mexc)
    mlow  = ones_like(mexc)
    mask  = ones_like(mexc)
    
    # iteratively (with i) clip outliers above(below) (-)max_sigma *sig
    i, nm = 0, None
    while (nm != mask.sum()) and (i < max_iter):
        mask = mexc & mhigh & mlow
        nm = mask.sum()
        med, sig = medsig(a[mask])
        mhigh[mexc] = a[mexc] - med <  max_sigma*sig #indices of okay values above median
        mlow[mexc]  = a[mexc] - med > -max_sigma*sig #indices of okay values below median
        i += 1
        mask = mexc & mhigh & mlow
        print("iteration {} at normalized median flux{:.5f} \pm {:.5f}".format(i, med, sig))
        mhigh = expand_mask(mhigh)
    if separate_masks:
        return mlow, mhigh
    else:
        return mlow & mhigh

def expand_mask(a, divval=3):
    """Expand the mask if multiple outliers occur in a row."""
    i,j,k = 0, 0, 0
    while i<len(a):
        v=a[i]
        
        if (v==0) & (j==0):
            k += 1
            j = 1
            i += 1

        elif (v==0) & (j==1):
            k += 1
            i += 1

        elif (v==1) & (j==0):
            i += 1
        
        elif (v==1) & (j==1):
            if k >= 3:
                addto = int(rint(sqrt(k/divval)))
                a[i - k - addto : i - k] = 0
                a[i : i + addto] = 0
                i += addto
            else:
                i += 1
            j = 0
            k = 0
                  
    return a
