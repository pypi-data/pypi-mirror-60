zimpute:A scRNA imputation method base on low rank complemetion 
Author<ZHOUSIHAN>
Structure and function composition：
Zimpute：
       |——Command():Command-line interactive functions
       |——Load_Matrix(infile_path):Import observation matrix (no row and column names),the return value is a two-dimensional matrix
       |——Data_Filtering(Data_matrix_M) :Delete the genes,which expressed in less than three cells, and the expression value is less than 3,the return value is a filtered matrix and deleted genes
       |——Data_Normlization(Filtering_M):Normalizing the observation matrix,the return value is normzlized matrix ,the median of rows(int) and the sum of rows(list)
       |——Select_r(Data_matrix_M):Calculate the most suitable r value，the return value is a truncated value(int)
       |——Truncated_QR(X,r):An improved QR singular value decomposition method,X is a two-dimentional matrix ,r is truncated value.the return value is L,S,R.The L,R is left singular vector and right singular vector,S is a singular value list
       |——Impute(M,r=1,lamda=0.01,F_flag="F",N_flag="F"):scRNA-seq imputation method.M is observation matrix,r is truncated value,F_flag represents the flag of filter,the default value is "F".N_flag represents the flag of normalize,the default value is "F".The return value is a imputed matrix
       |——Save_result(outfile_path,W):Save result at outfile_path.no return value.
       |——Example_lambda_pic():Show the relative error of example dataset with different lambda,no return value
       |——Example_mu_pic():Show the relative error of example dataset with different mu,no return value
       |——Relative_error(M_pred,M_obes):compute the relative error.M_pred is prediction matrix,M_obes is observation matrix.The return value is relative error(float)
       |——tSNE_Visualize(Matrix_raw,Matrix_impute,Target_group,celltype_list,n_components=2):Visualize the results.The format of Target_group is a list with 1 column.like:[0 0 1 1 2 2 1 0] ,different numbers mean different cell types,celltype_list:["cell A","cell B","cell C"],0=cell A,1=cell B,2=cell C.
       |——Example_sigma_pic(Matrix):Draw the trend of singular value,no return value.
       |——Sample(M,sample_rate):Random sampling function, input dropout rate and raw matrix,the return value is sampled matrix.
       |——Show_error_plot():Draw the relative error with diferent methods,no return value.
