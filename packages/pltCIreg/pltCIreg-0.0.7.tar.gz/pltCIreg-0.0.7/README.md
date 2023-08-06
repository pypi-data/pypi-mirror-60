# pltCIreg
## plot confidence interval
In this package, there is only one function named tworegCI.
 
tworegCI的调用方法为：import pltCIreg as pltc; pltc.tworegCI()


e.g. pltc.tworegCI(data, data0, xlim=[.8, 7.2], xlab='Quantile',  ylab='SBT coefficient', 
        leglab = ['China', 'the U.S.'], figsz=[6,5,90])
