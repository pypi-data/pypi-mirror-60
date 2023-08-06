# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 23:59:12 2019

@author: zhedashen
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def tworegCI(data, data0, xlim = None, ylim = None, legloc = 'best', xlab = None
             ,ylab = None, leglab = ['a', 'b'], figsz = None):
    
    """Data preparation1"""
    #data = [[0, 1, 2, 3],  # x variable (quantile)
    #        [2, 3, 4, 5],  # y variable (x effect)
    #        [1.5, 2, 3, 3],  #  low CI
    #        [2.5, 4, 5, 7]]  #  upper CI
    data = np.array(data).T
    predict_mean_ci_low, predict_mean_ci_upp = data[:, 2:].T  #summary_table
    
    # 创建置信区间DataFrame，上下界
    CI_df = pd.DataFrame(columns = ['x_data', 'low_CI', 'upper_CI'])
    CI_df['x_data'] = data[:, 0]  
    CI_df['low_CI'] = predict_mean_ci_low
    CI_df['upper_CI'] = predict_mean_ci_upp
    CI_df.sort_values('x_data', inplace = True) # 根据x_data进行排序
    
    x_data = data[:, 0]  
    y_data = data[:, 1] 
    sorted_x = CI_df['x_data']
    low_CI = CI_df['low_CI']
    upper_CI = CI_df['upper_CI']


    """Data preparation2"""
    #data0 = [[0, 1, 2, 3],  # x variable (quantile)
    #         [3, 3, 3, 3],  # y variable (x effect)
    #         [2, 2, 2, 2],  #  low CI
    #         [4, 4, 4, 4]]  #  upper CI
    data0 = np.array(data0).T
    predict_mean_ci_low0, predict_mean_ci_upp0 = data0[:, 2:].T  #summary_table
    CI_df0 = pd.DataFrame(columns = ['x_data', 'low_CI', 'upper_CI'])
    CI_df0['x_data'] = data0[:, 0]  
    CI_df0['low_CI'] = predict_mean_ci_low0
    CI_df0['upper_CI'] = predict_mean_ci_upp0
    CI_df0.sort_values('x_data', inplace = True) # 根据x_data进行排序
    
    x_data0 = data0[:, 0]  
    y_data0 = data0[:, 1] 
    sorted_x0 = CI_df0['x_data']
    low_CI0 = CI_df0['low_CI']
    upper_CI0 = CI_df0['upper_CI']
    
    #########Figure        
    try:
        plt.figure(figsize=(figsz[0], figsz[1]), dpi=figsz[2])
    except:
        pass

    '''Plot'''
    plt.plot(x_data, y_data, lw = 1, color = '#0257cc', alpha = 1, label = leglab[0])
    # 绘制置信区间，顺序填充
    plt.fill_between(sorted_x, low_CI, upper_CI, color = '#539caf', alpha = 0.4)   
    
    # 绘制预测曲线
    plt.plot(x_data0, y_data0, lw = 1, color = '#815d07', alpha = 1, label = leglab[1])
    # 绘制置信区间，顺序填充
    plt.fill_between(sorted_x0, low_CI0, upper_CI0, color = '#c99d49', alpha = 0.4) 
    
    ftsize = 14
    fam = 'Times New Roman'
    plt.xlabel(xlab, fontsize = ftsize, family = fam)
    plt.ylabel(ylab, fontsize = ftsize, family = fam)
    plt.xticks(10 * np.arange(1, 10, 2))
    plt.xlim(xlim[0], xlim[1])
    try:
        plt.ylim(ylim[0], ylim[1])
    except:
       pass
    plt.xticks(fontsize = ftsize, family = fam)  # 设置刻度字体大小
    plt.yticks(fontsize = ftsize, family = fam)
    
    font1 = {'family' : 'Times New Roman',
    'weight' : 'normal',
    'size'   : 14}
    plt.legend(loc = legloc, fontsize = ftsize, prop = font1)
    plt.show()    
    

import seaborn as sns
import scipy

from matplotlib import gridspec

def _ax_title(ax, title, subtitle):
	"""
	Prints title on figure.

	Parameters
	----------
	fig : matplotlib.axes.Axes
		Axes objet where to print titles.
	title : string
		Main title of figure.
	subtitle : string
		Sub-title for figure.
	"""
	ax.set_title(title + "\n" + subtitle)
	#fig.suptitle(subtitle, fontsize=10, color="#919191")

def _ax_labels(ax, xlabel, ylabel):
	"""
	Prints labels on axis' plot.

	Parameters
	----------
	ax : matplotlib.axes.Axes
		Axes object where to print labels.
	xlabel : string
		Label of X axis.
	ylabel : string
		Label of Y axis.
	"""
	ax.set_xlabel(xlabel)
	ax.set_ylabel(ylabel)
	

def _ax_quantiles(ax, quantiles, twin='x'):
	"""
	Plot quantiles of a feature over opposite axis.

	Parameters
	----------
	ax : matplotlib.Axis
		Axis to work with.
	quantiles : array-like
		Quantiles to plot.
	twin : string
		Possible values are 'x' or 'y', depending on which axis to plot quantiles.
	"""
	print("Quantiles :", quantiles)
	if twin == 'x':
		ax_top = ax.twiny()
		ax_top.set_xticks(quantiles)
		ax_top.set_xticklabels(["{1:0.{0}f}%".format(int(i / (len(quantiles) - 1) * 100 % 1 > 0), i / (len(quantiles) - 1) * 100) for i in range(len(quantiles))], color="#545454", fontsize=7)
		ax_top.set_xlim(ax.get_xlim())
	elif twin =='y':
		ax_right = ax.twinx()
		ax_right.set_yticks(quantiles)
		ax_right.set_yticklabels(["{1:0.{0}f}%".format(int(i / (len(quantiles) - 1) * 100 % 1 > 0), i / (len(quantiles) - 1) * 100) for i in range(len(quantiles))], color="#545454", fontsize=7)
		ax_right.set_ylim(ax.get_ylim())

def _ax_scatter(ax, points):
	print(points)
	ax.scatter(points.values[:,0], points.values[:,1], alpha=0.5, edgecolor=None)

def _ax_grid(ax, status):
	ax.grid(status, linestyle='-', alpha=0.4) 

#def _ax_labels(ax, label):


def _ax_boxplot(ax, ALE, cat, **kwargs):
	ax.boxplot(cat, ALE, **kwargs)

def _ax_hist(ax, x, **kwargs):
	sns.rugplot(x, ax=ax, alpha=0.2)


def _first_order_quant_plot(ax, quantiles, ALE, **kwargs):
	#ax.plot(quantiles, ALE, **kwargs)
	ax.plot((quantiles[1:] + quantiles[:-1]) / 2, ALE, **kwargs)
	#ax.scatter(quantiles, ALE, color="#1f77b4", s=12)

#def _first_order_cat_plot(ax, ALE, **kwargs):
#	"""
#
#	"""
#	ax.boxplot(

def _second_order_quant_plot(ax, quantiles, ALE, **kwargs):
	print(ALE)
	x = np.linspace(quantiles[0][0], quantiles[0][-1], 50)
	y = np.linspace(quantiles[1][0], quantiles[1][-1], 50)
	X, Y = np.meshgrid(x, y)
	#ax.imshow(ALE, interpolation="bilinear", cmap='viridis')
	ALE_interp = scipy.interpolate.interp2d(quantiles[0], quantiles[1], ALE)
	CF = ax.contourf(X, Y, ALE_interp(x, y), cmap='bwr', levels=30, alpha=0.7)
	plt.colorbar(CF)
	#CS = ax.contour(X, Y, ALE_interp(x, y), levels=30, cmap='inferno', alpha=0.99)
	#ax.clabel(CS, inline=1, fontsize=10)

def _first_order_ale_quant(predictor, train_set, feature, quantiles):
	"""Computes first-order ALE function on single continuous feature data.

	Parameters
	----------
	predictor : function
		Prediction function.
	train_set : pandas DataFrame
		Training set on which model was trained.
	feature : string
		Feature's name.
	quantiles : array-like
		Quantiles of feature.
	"""
	ALE = np.zeros(len(quantiles) - 1)  # Final ALE function

	for i in range(1, len(quantiles)):
		subset = train_set[(quantiles[i - 1] <= train_set[feature]) & (train_set[feature] < quantiles[i])]

		# Without any observation, local effect on splitted area is null
		if len(subset) != 0:
			z_low = subset.copy()
			z_up = subset.copy()
			# The main ALE idea that compute prediction difference between same data except feature's one
			z_low[feature] = quantiles[i - 1]
			z_up[feature] = quantiles[i]
			ALE[i - 1] += (predictor(z_up) - predictor(z_low)).sum() / subset.shape[0]

	
	ALE = ALE.cumsum()  # The accumulated effect
	ALE -= ALE.mean()  # Now we have to center ALE function in order to obtain null expectation for ALE function
	return ALE

def _second_order_ale_quant(predictor, train_set, features, quantiles):
	"""Computes second-order ALE function on two continuous features data.

	

	"""
	quantiles = np.asarray(quantiles)
	ALE = np.zeros((quantiles.shape[1], quantiles.shape[1]))  # Final ALE function
	print(quantiles)

	for i in range(1, len(quantiles[0])):
		for j in range(1, len(quantiles[1])):
			# Select subset of training data that falls within subset
            subset = train_set[(quantiles[0,i-1] <= train_set[features[0]]) &
                               (quantiles[0,i] > train_set[features[0]]) &
                               (quantiles[1,j-1] <= train_set[features[1]]) &
                               (quantiles[1,j] > train_set[features[1]])]

			# Without any observation, local effect on splitted area is null
			if len(subset) != 0:
				z_low = [subset.copy() for _ in range(2)]  # The lower bounds on accumulated grid
				z_up = [subset.copy() for _ in range(2)]  # The upper bound on accumulated grid
				# The main ALE idea that compute prediction difference between same data except feature's one
				z_low[0][features[0]] = quantiles[0, i - 1]
				z_low[0][features[1]] = quantiles[1, j - 1]
				z_low[1][features[0]] = quantiles[0, i]
				z_low[1][features[1]] = quantiles[1, j - 1]
				z_up[0][features[0]] = quantiles[0, i - 1]
				z_up[0][features[1]] = quantiles[1, j]
				z_up[1][features[0]] = quantiles[0, i]
				z_up[1][features[1]] = quantiles[1, j]

				ALE[i, j] += (predictor(z_up[1]) - predictor(z_up[0]) - (predictor(z_low[1]) - predictor(z_low[0]))).sum() / subset.shape[0]

	
	ALE = np.cumsum(ALE, axis=0) # The accumulated effect
	ALE -= ALE.mean()  # Now we have to center ALE function in order to obtain null expectation for ALE function
	return ALE

def _first_order_ale_cat(predictor, train_set, feature, features_classes, feature_encoder=None):
	"""Computes first-order ALE function on single categorical feature data.

	Parameters
	----------
	predictor : function
		Prediction function.
	train_set : pandas DataFrame
		Training set on which model was trained.
	feature : string
		Feature's name.
	features_classes : list or string
		Feature's classes.
	feature_encoder : function or list
		Encoder that was used to encode categorical feature. If features_classes is not None, this parameter is skipped.
	"""
	num_cat = len(features_classes)
	ALE = np.zeros(num_cat)  # Final ALE function

	for i in range(num_cat):
		subset = train_set[train_set[feature] == features_classes[i]]

		# Without any observation, local effect on splitted area is null
		if len(subset) != 0:
			z_low = subset.copy()
			z_up = subset.copy()
			# The main ALE idea that compute prediction difference between same data except feature's one
			z_low[feature] = quantiles[i - 1]
			z_up[feature] = quantiles[i]
			ALE[i] += (predictor(z_up) - predictor(z_low)).sum() / subset.shape[0]

	
	ALE = ALE.cumsum()  # The accumulated effect
	ALE -= ALE.mean()  # Now we have to center ALE function in order to obtain null expectation for ALE function
	return ALE
	


def ale_plot(model, train_set, features, bins=10, monte_carlo=False, predictor=None, features_classes=None, **kwargs):
	"""Plots ALE function of specified features based on training set.

	Parameters
	----------
	model : object or function
		A Python object that contains 'predict' method. It is also possible to define a custom prediction function with 'predictor' parameters that will override 'predict' method of model.
	train_set : pandas DataFrame
		Training set on which model was trained.
	features : string or tuple of string
		A single or tuple of features' names.
	bins : int
		Number of bins used to split feature's space.
	monte_carlo : boolean
		Compute and plot Monte-Carlo samples.
	predictor : function
		Custom function that overrides 'predict' method of model.
	features_classes : list of string
		If features is first-order and is a categorical variable, plot ALE according to discrete aspect of data.
	monte_carlo_rep : int
		Number of Monte-Carlo replicas.
	monte_carlo_ratio : float
		Proportion of randomly selected samples from dataset at each Monte-Carlo replica.

	"""
	fig = plt.figure()
	if not isinstance(features, (list, tuple, np.ndarray)):
		features = np.asarray([features])

	if len(features) == 1:
		quantiles = np.percentile(train_set[features[0]], [1. / bins * i * 100 for i in range(0, bins + 1)])  # Splitted areas of feature

		if monte_carlo:
			mc_rep = kwargs.get('monte_carlo_rep', 50)
			mc_ratio = kwargs.get('monte_carlo_ratio', 0.1)
			mc_replicates = np.asarray([[np.random.choice(range(train_set.shape[0])) for _ in range(int(mc_ratio * train_set.shape[0]))] for _ in range(mc_rep)])
			for k, rep in enumerate(mc_replicates):
				train_set_rep = train_set.iloc[rep, :]
				if features_classes is None:
					mc_ALE = _first_order_ale_quant(model.predict if predictor is None else predictor, train_set_rep, features[0], quantiles)
					_first_order_quant_plot(fig.gca(), quantiles, mc_ALE, color="#1f77b4", alpha=0.06)

		if features_classes is None:
			ALE = _first_order_ale_quant(model.predict if predictor is None else predictor, train_set, features[0], quantiles)
			_ax_labels(fig.gca(), "Feature '{}'".format(features[0]), "")
			_ax_title(fig.gca(), "First-order ALE of feature '{0}'".format(features[0]),
				"Bins : {0} - Monte-Carlo : {1}".format(len(quantiles) - 1, mc_replicates.shape[0] if monte_carlo else "False"))
			_ax_grid(fig.gca(), True)
			_ax_hist(fig.gca(), train_set[features[0]])
			_first_order_quant_plot(fig.gca(), quantiles, ALE, color="black")
			_ax_quantiles(fig.gca(), quantiles)
		else:
			_ax_boxplot(fig.gca(), quantiles, ALE, color="black")
	elif len(features) == 2:
		quantiles = [np.percentile(train_set[f], [1. / bins * i * 100 for i in range(0, bins + 1)]) for f in features]

		if features_classes is None:
			ALE = _second_order_ale_quant(model.predict if predictor is None else predictor, train_set, features, quantiles)
			#_ax_scatter(fig.gca(), train_set.loc[:, features])
			_second_order_quant_plot(fig.gca(), quantiles, ALE)
			_ax_labels(fig.gca(), "Feature '{}'".format(features[0]), "Feature '{}'".format(features[1]))
			_ax_quantiles(fig.gca(), quantiles[0], twin='x')
			_ax_quantiles(fig.gca(), quantiles[1], twin='y')
			_ax_title(fig.gca(), "Second-order ALE of features '{0}' and '{1}'".format(features[0], features[1]),
				"Bins : {0}x{1}".format(len(quantiles[0]) - 1, len(quantiles[1]) - 1))

	plt.show()

	
def plot_fltraj(Coordinates, figr=0, NumOfDvdInEdge = 14, sign = '.', text_clr = 'k'):
    """
    This function is used for drawing flight trajectory in the map
    Coordinates is a pandas-type dataframe, which incorporates longs and lats
    e.g. m(Coordinates['Long'].values, Coordinates['Lat'].values)
    """
#    plt.figure(figsize=(27, 20))
#    fig, ax = plt.subplots(figsize=(27, 20))
    m = Basemap(projection='merc', llcrnrlon=110, llcrnrlat=20.1,
    		        urcrnrlon=122, urcrnrlat=41.2,
    		        lat_ts=0, resolution='l', suppress_ticks=True)
    ###分割地图
    lons, lats, x, y = m.makegrid(int(NumOfDvdInEdge/2), NumOfDvdInEdge, returnxy = True)
    m.drawparallels(lats[:, 0], labels = [False, True, True, False])
    m.drawmeridians(lons[0], labels = [True, False, False, True])
    
    ### 常规配置
    coast_color = (10.0/255.0, 10.0/255.0, 10/255.0, 0.7)
    bg_color = (1.0, 1.0, 1.0, 0.8)
    m.drawcoastlines(color = coast_color, linewidth = 1.0)
    m.fillcontinents(color = bg_color, lake_color = bg_color)
    m.drawmapboundary(fill_color = bg_color)
    m.drawcoastlines(linewidth = 0.5)
    m.drawcountries(linewidth = 2)
    m.drawstates(linewidth = 0.2)
    m.fillcontinents(alpha = 0.1)
    
    # draw nodes and overly on basemap   
    mx, my = m(Coordinates['Long'].values, Coordinates['Lat'].values)
    
    plt.plot(mx, my, sign)
    
#    x, y = m(113.841778, 34.516833)
#    plt.text(x, y, 'CGO')
    
    if figr != 0:
        ax = figr.add_subplot(111)
        for i in range(Coordinates.shape[0]):
#            plt.text(mx[i], my[i], Coordinates['IDENTIFIER'][i])  # 效果和下面一行代码 一样！
            ax.annotate('{}'.format(Coordinates['ID'][i]), xy=(mx[i], my[i]), color = text_clr)
            
def generate_coords(lon1, lat1, lon2, lat2, NumOfInsert = 2):

    lat1 = radians(lat1)
    lat2 = radians(lat2)
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    
    x1 = cos(lat1) * cos(lon1)
    y1 = cos(lat1) * sin(lon1)
    z1 = sin(lat1)
    
    x2 = cos(lat2) * cos(lon2)
    y2 = cos(lat2) * sin(lon2)
    z2 = sin(lat2)
    
    PtLst_Insert = []
    
    delta_x = (x2 - x1) / (NumOfInsert + 1)
    delta_y = (y2 - y1) / (NumOfInsert + 1)
    delta_z = (z2 - z1) / (NumOfInsert + 1)
    
    for i in range(NumOfInsert):
    
        x_N1 = x1 + delta_x * (i+1)
        y_N1 = y1 + delta_y * (i+1)
        z_N1 = z1 + delta_z * (i+1)
        
        lon_N1 = atan2(y_N1, x_N1);
        hyp_N1 = sqrt(x_N1 * x_N1 + y_N1 * y_N1)
        lat_N1 = atan2(z_N1, hyp_N1)
        
        lat_N1 = lat_N1 * 180 / pi;
        lon_N1 = lon_N1 * 180 / pi;

        PtLst_Insert.append((lon_N1, lat_N1))

    return PtLst_Insert

####### Reference ######### 
    
#Calculate the center point of multiple latitude/longitude coordinate pairs
#https://stackoverflow.com/questions/6671183/calculate-the-center-point-of-multiple-latitude-longitude-coordinate-pairs?noredirect=1&lq=1
#https://stackoverflow.com/questions/35645423/how-to-get-center-pointlatlng-between-some-locations 

 