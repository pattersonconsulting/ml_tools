import numpy as np

import pandas as pd 
from pandas import Series


import os
import sys

from sklearn.metrics import confusion_matrix


def standard_confusion_matrix(y_true, y_pred):
	'''
		Reformat confusion matrix output from sklearn for plotting profit curve.
	'''
	[[tn, fp], [fn, tp]] = confusion_matrix(y_true, y_pred)
	return np.array([[tp, fp], [fn, tn]])



'''
	Takes a [2, 2] np.array as input with the format: [[tp, fp], [fn, tn]]
	

	# this function calculates the
	# conditional probabilities of each cell in our confusion matrix 
	# given the probability of in our population

'''
def calc_confusion_matrix_conditional_probabilities(standard_cmatrix):

	[[tp, fp], [fn, tn]] = standard_cmatrix

	tp_rate = tp / (tp + fn)
	fp_rate = fp / (fp + tn)
	fn_rate = fn / (fn + tp)
	tn_rate = tn / (tn + fp)

	return np.array([[tp_rate, fp_rate], [fn_rate, tn_rate]])


'''
	Takes a [2, 2] np.array as input with the format: [[tp, fp], [fn, tn]]
	

	# this function calculates the
	# ESTIMATED probabilities of each cell in our confusion matrix 
	# given the TOTAL RECORDS in our population

'''
def calc_confusion_matrix_estimated_probabilities(standard_cmatrix):

	total_records = calc_total_records(standard_cmatrix)

	[[tp, fp], [fn, tn]] = standard_cmatrix

	tp_est_prob = tp / total_records
	fp_est_prob = fp / total_records
	fn_est_prob = fn / total_records
	tn_est_prob = tn / total_records

	return np.array([[tp_est_prob, fp_est_prob], [fn_est_prob, tn_est_prob]])


def calc_total_records(standard_cmatrix):

	[[tp, fp], [fn, tn]] = standard_cmatrix

	return tp + fp + fn + tn


def calc_class_priors(standard_cmatrix):

	[[tp, fp], [fn, tn]] = standard_cmatrix

	total_instances = tp + fp + fn + tn

	positive_class_prior = (tp + fn) / total_instances

	negative_class_prior = (fp + tn) / total_instances

	return positive_class_prior, negative_class_prior


'''
	Calculating Expected Profit (binary classifier)

		* this is the naive version that doesnt not take into account class priors
		* here we use "estimates of probabilities": p(h,a) == count(h,a) / TotalInstances (NOT the TP Rate, etc)


'''
def expected_value_calculation_naive(standard_cmatrix, cost_benefit_matrix):


	cm_est_prob = calc_confusion_matrix_estimated_probabilities( standard_cmatrix )

	[[tp_est_prob, fp_est_prob], [fn_est_prob, tn_est_prob]] = cm_est_prob


	[[tp_value, fp_value], [fn_value, tn_value]] = cost_benefit_matrix

	#print("\ntpr: " + str(tpr))
	#print("tp_value: " + str(tp_value))

	#print("fpr: " + str(fpr))
	#print("fp_value: " + str(fp_value))

	# calculate "naive" expected value (expected value without the class priors)
	expected_value = (tp_est_prob * tp_value + fn_est_prob * fn_value) + (tn_est_prob * tn_value + fp_est_prob * fp_value)


	return expected_value



'''
	Calculating Expected Profit (binary classifier) with class priors

		* the p(Y|p) correspondes directly to the *true positive rate* (from confusion matrix) -- as do the other associated values
		* this is foundationally different than the "naive"-version where we use "estimates of probabilities": p(h,a) == count(h,a) / TotalInstances


'''
def expected_value_calculation_with_class_priors(standard_cmatrix, cost_benefit_matrix):

	

	#std_cmatrix = standard_confusion_matrix(y_test, y_pred)
	
	[[tp, fp], [fn, tn]] = standard_cmatrix

	#total_instance_count = calc_total_records( standard_cmatrix )

	cm_cond_prob = calc_confusion_matrix_conditional_probabilities( standard_cmatrix )

	[[tpr, fpr], [fnr, tnr]] = cm_cond_prob

	pos_class_prior, neg_class_prior = calc_class_priors( standard_cmatrix )

	[[tp_value, fp_value], [fn_value, tn_value]] = cost_benefit_matrix

	# formula == class_prior(positive) * [tpr * tp_value + fnr * fn_value]
	#				+ class_prior(negative) * [tnr * tn_value + fpr * fp_value]

	expected_value = ( pos_class_prior * (tpr * tp_value + fnr * fn_value) ) \
		+ ( neg_class_prior * (tnr * tn_value + fpr * fp_value) )


	return expected_value



'''
Analyze a model's performance and threshold optimal point based on a cost-benefit matrix

INPUTS:
	- cost benefit matrix in the same format as the confusion matrix above
	- predicted probabilities
	- actual labels

OUTPUT
	{ max_profit, best_confusion_matrix }

'''
def calculate_optimal_model_threshold( costbenefit_mat, y_proba, y_test ):
   
	profits = [] # one profit value for each threshold
	confusion_matrices = []
	thresholds = sorted(y_proba, reverse=True)

	# For each threshold, calculate profit - starting with largest threshold
	for thresh in thresholds:
		
		y_pred = (y_proba > thresh).astype(int)

		cmatrix = confusion_matrix(y_test, y_pred)
		
		confusion_matrices.append( cmatrix )

		tn, fp, fn, tp = cmatrix.ravel()
		
		confusion_mat = np.array([[tp, fp], [fn, tn]])

		# Calculate total profit for this threshold
		# note: the multiplication below is a element-wise multiplication, not a matrix-multiplication (this got me one time)
		profit = sum(sum(confusion_mat * costbenefit_mat)) / len(y_test)
		profits.append(profit)

	
	max_profit = max(profits)

	max_profit_index = profits.index(max(profits))

	print("total profit entries: " + str(len(profits)))
	print("total confusion_matrices entries: " + str(len(confusion_matrices)))

	cfmtx_max = confusion_matrices[max_profit_index]

	return max_profit, cfmtx_max





