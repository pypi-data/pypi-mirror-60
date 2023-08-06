import gc
import numpy as np
import pandas as pd
from ctypes import *
from ctypes.util import find_library
from .libpath import find_lib_path
from .LiteMORT_preprocess import *
from .LiteMORT_problems import *
from sklearn import preprocessing
import os
import warnings
import matplotlib.pyplot as plt
import psutil

def _check_not_tuple_of_2_elements(obj, obj_name='obj'):
    """Check object is not tuple or does not have 2 elements."""
    if not isinstance(obj, tuple) or len(obj) != 2:
        raise TypeError('%s must be a tuple of 2 elements.' % obj_name)


def _float2str(value, precision=None):
    return ("{0:.{1}f}".format(value, precision)
            if precision is not None and not isinstance(value, string_type)
            else str(value))
'''
BUG
    1 predict和predict_raw 参见case_poct.py
    
'''
class MORT_exception(Exception):
    """Error throwed by LiteMORT"""
    pass
def _check_call(ret,normal_value=0x0):
    """Check the return value of C API call
    Parameters
    ----------
    ret : int
        return value from API calls
    """
    if ret != normal_value:
        raise MORT_exception("_check_call failed at {}-{}".format(ret,normal_value))
'''
    sklearn style
'''

class LiteMORT_profile(object):
    def __init__(self):
        self.memory_info={}
        self.params = {}
        self.shots = {}
        self.memory_info['virtual memory'] = 0
        self.memory_info['physical memory'] = 0

    def Snapshot(self, title,params=None):
        process = psutil.Process(os.getpid())
        dic_mem = process.memory_info()
        dic_mem =dic_mem._asdict()
        #dic_mem=dict(dic_mem)
        self.shots[title] = dic_mem
        #print(process.memory_info().rss)

    def Stat(self,shot0,shot1,dump=True):
        assert (shot0 in self.shots)
        if shot1 not in self.shots:
            self.Snapshot(shot1)
        assert (shot1 in self.shots)
        mem_0 = self.shots[shot0]
        mem_1 = self.shots[shot1]
        self.memory_info['virtual memory']=a=(mem_1['vms']-mem_0['vms'])/1.0e6
        self.memory_info['physical memory']=b=(mem_1['rss']-mem_0['rss'])/1.0e6
        v0=mem_0['vms']/1.0e6
        if dump:
            print(f"\n{'-'* 120}\nMEMORY@[{shot0}-{shot1}]: physical={a:.2f}(M) virtual={b:.2f}(M) begin={v0:.2f}(M)")
            if "peak_pagefile" in mem_1 and "peak_wset" in mem_1:
                peak_info=f"PEAK=[{mem_1['peak_pagefile']/1.0e6:.1f},{mem_1['peak_wset']/1.0e6:.1f}](M)"
                print(f"\t{peak_info}")
            print(f"{'-'* 120}")

        return

class LiteMORT_params(object):
    def alias_param(self,key,default_value,dict_param,alia_list):
        for alias in alia_list:
            if alias not in dict_param:
                continue
            if alias!=key and self.verbose>0:
                print(f"Found `{alias}`(alias of {key}) in params. Will use it instead of argument")
                #warnings.warn("Found `{}`(alias of {}) in params. Will use it instead of argument".format(alias,key))
            value = (type(default_value))(dict_param[alias])
            return value
        return default_value

    def OnArgs(self,dict_param):
        self.isOK = False
        self.verbose = self.alias_param('verbose', 0, dict_param, ['verbosity', "verbose"])
        if 'metric' in dict_param:
            if(dict_param['metric'] in ['regression_l2', 'mse', 'l2'] ):
                self.metric = 'mse'
            elif (dict_param['metric'] in ['regression_l1','mean_absolute_error', 'mae', 'l1']):
                self.metric = 'mae'
            elif (dict_param['metric'] in ['mean_squared_error', 'l2_root','root_mean_squared_error', 'rmse'] ):
                self.metric = 'rmse'
            else:
                self.metric = dict_param['metric']
        if 'num_leaves' in dict_param:
            self.num_leaves = dict_param['num_leaves']
        if 'feat_factor' in dict_param:
            self.feat_factor = dict_param['feat_factor']
            self.feat_factor = self.feat_factor.astype(np.float32)
        if 'max_depth' in dict_param:
            self.max_depth = dict_param['max_depth']
        if 'learning_rate' in dict_param:
            self.learning_rate = dict_param['learning_rate']
        if 'prune' in dict_param:
            self.prune = dict_param['prune']
        if 'learning_schedule' in dict_param:
            self.learning_schedule = dict_param['learning_schedule']
        if 'adaptive' in dict_param:
            self.adaptive = dict_param['adaptive']
        if 'debug' in dict_param:
            self.debug = dict_param['debug']
        self.lambda_l2 = self.alias_param('lambda_l2', 0.0, dict_param, ['lambda_l2', 'reg_lambda'])

        if 'bagging_fraction' in dict_param:
            self.subsample = dict_param['bagging_fraction']
        #if 'subsample' in dict_param:
        #    self.subsample = dict_param['subsample']
        self.subsample = self.alias_param('subsample',1.0,dict_param,['subsample','bagging_fraction','sub_row'])
        #if 'feature_fraction' in dict_param:
        #    self.feature_sample = dict_param['feature_fraction']
        self.feature_sample = self.alias_param('sub_feature', 1.0, dict_param, ['feature_sample', 'feature_fraction', 'sub_feature', 'colsample_bytree'])
        if 'max_bin' in dict_param:
            self.feature_quanti = dict_param['max_bin']
        if 'cascade' in dict_param:
            self.cascade = dict_param['cascade']
        if 'salp_bins' in dict_param:
            self.salp_bins = dict_param['salp_bins']
        if 'elitism' in dict_param:
            self.elitism = dict_param['elitism']
        if 'verbose_eval' in dict_param:
            self.verbose_eval = dict_param['verbose_eval']
        if 'min_data_in_leaf' in dict_param:
            self.min_child_samples = dict_param['min_data_in_leaf']
        if 'boost_from_average' in dict_param:
            self.boost_from_average = dict_param['boost_from_average']
        if 'iter_refine' in dict_param:
            self.iter_refine = dict_param['iter_refine']
        if 'representive' in dict_param:
            self.representive = dict_param['representive']
        self.n_threads = self.alias_param('n_threads', 0, dict_param, ['n_threads', "n_jobs", "num_threads"])

        #if 'early_stop' in dict_param:
        #    self.early_stopping_rounds = dict_param['early_stop']
        self.early_stopping_rounds = self.alias_param('early_stop',50,dict_param,['early_stop',"early_stopping_round", "early_stopping_rounds", "early_stopping"])
        self.n_estimators = self.alias_param('num_trees',self.n_estimators,dict_param,
            ["num_boost_round", "num_iterations", "num_iteration", "num_tree", "num_trees", "num_round", "num_rounds", "n_estimators"] )


    def __init__(self,objective,fold=5,lr=0.1,round=50,early_stop=50,subsample=1,feature_sample=1,leaves=31,
                 max_bin=256,metric='mse',min_child=20,max_depth=-1,subsample_for_bin=200000,argv=None):
        #objective='outlier'
        self.isOK = False
        self.env = 'default'
        self.use_gpu = True
        self.version = 'v1'
        self.feature_quanti=max_bin
        self.feature_sample = feature_sample
        self.min_child_samples = min_child
        self.subsample = subsample
        self.NA = -1
        self.normal = 0
        self.histo_bin_map = 1       #1,      #0-quantile,1-frequency 3 dcrimini on Y
        self.node_task=0         #0:histo(X) split(X),     1:histo(X) split(Y) 2:REGRESS_X
        self.objective=objective
        self.metric=metric
        self.k_fold = fold
        self.learning_rate = lr
        self.n_estimators = round
        self.num_leaves = leaves
        self.early_stopping_rounds = early_stop
        self.verbose = 1
        #self.boost_from_average = 0,

        self.OnArgs(argv)

class M_argument(Structure):
    _fields_ = [    ('Keys',c_char_p),
                    ('Values',c_float),
                    ('text', c_char_p),
                    ('array', c_void_p),
               ]


class LiteMORT(object):
    #problem = None
    #preprocess = None
    #hEDA=None

    def load_dll(self):
        lib_path = find_lib_path()
        if len(lib_path) == 0:
            return None
        # lib_path.append( 'F:/Project/LiteMORT/LiteMORT.dll' )

        self.dll_path = lib_path[0]
        CWD = os.path.abspath('.')
        #os.environ['PATH'] = CWD + ";" + os.environ['PATH']
        theDll = find_library(self.dll_path)
        if theDll is None:
            print(f"ctyped failed to find {self.dll_path},SO STRANGE!!!\tCWD={CWD}")
        self.dll = cdll.LoadLibrary(self.dll_path)
        print("======Load LiteMORT library @{}".format(self.dll_path))
        self.mort_init = self.dll.LiteMORT_init
        self.mort_init.argtypes = [POINTER(M_argument), c_int,POINTER(M_DATASET_LIST), c_size_t]
        self.mort_init.restype = c_void_p

        self.C_set_mergesets = self.dll.LiteMORT_set_mergesets
        self.C_set_mergesets.argtypes = [c_void_p,POINTER(M_DATASET_LIST), c_size_t]
        self.C_set_mergesets.restype = None

        #self.mort_fit = self.dll.LiteMORT_fit
        #self.mort_fit.argtypes = [c_void_p,POINTER(c_float), POINTER(c_double), c_size_t, c_size_t,POINTER(c_float), POINTER(c_double), c_size_t, c_size_t]
        #self.mort_fit.restype = None
        self.mort_fit_1 = self.dll.LiteMORT_fit_1
        self.mort_fit_1.argtypes = [c_void_p, POINTER(M_DATASET_LIST), POINTER(M_DATASET_LIST), c_size_t]
        self.mort_fit_1.restype = None

        self.cpp_test = self.dll.cpp_test
        self.cpp_test.argtypes = [c_void_p, POINTER(M_DATASET)]
        self.cpp_test.restype = None

        #self.mort_predcit = self.dll.LiteMORT_predict
        #self.mort_predcit.argtypes = [c_void_p,POINTER(c_float), POINTER(c_double), c_size_t, c_size_t, c_size_t]
        self.mort_predcit_1 = self.dll.LiteMORT_predict_1
        self.mort_predcit_1.argtypes = [c_void_p,POINTER(M_DATASET_LIST), c_size_t]

        #self.mort_eda = self.dll.LiteMORT_EDA
        #self.mort_eda.argtypes = [c_void_p,POINTER(c_float), POINTER(c_double), c_size_t, c_size_t, c_size_t,
        #                          POINTER(M_argument), c_int, c_size_t]
        #self.mort_eda.restype = c_void_p

        self.mort_imputer_f = self.dll.LiteMORT_Imputer_f
        self.mort_imputer_f.argtypes = [POINTER(c_float), POINTER(c_double), c_size_t, c_size_t, c_size_t]

        self.mort_imputer_d = self.dll.LiteMORT_Imputer_d
        self.mort_imputer_d.argtypes = [POINTER(c_double), POINTER(c_double), c_size_t, c_size_t, c_size_t]

        self.mort_clear = self.dll.LiteMORT_clear
        self.mort_clear.argtypes = [c_void_p]

    def __init__(self, params,merge_infos=None,fix_seed=None):
        self.problem = None
        self.preprocess = None
        self.hLIB = None
        self.load_dll()
        self._n_classes = None
        self.best_iteration_ = 0
        self.best_iteration = 0
        self.best_score = 0
        self.profile = LiteMORT_profile()

        self.init_params_cpp(params)
        if self.params.objective == "binary":
            self.problem = Mort_BinaryClass(self.params.__dict__)
        elif self.params.objective == "regression":
            self.problem = Mort_Regressor(self.params.__dict__)

        self.hLIB = self.mort_init(self.ca_array, len(self.ca_array),None,0x0)
        self.MergeDataSets(merge_infos)

    def __del__(self):
        try:
            #print("LiteMORT::__del__...".format())
            if self.hLIB is not None:
                self.mort_clear(self.hLIB)
            self.hLIB = None
        except AttributeError:
            pass

    # For DataFrames of mixed type calling .values converts multiple blocks (for each dtype) into one numpy array of a all-encompassing dtype.
    # This conversion can be slow for large frames!!!
    def X_t(self, X_train_0, target_type):
        # mort_fit需要feature优先
        if isinstance(X_train_0, pd.DataFrame):
            np_mat = X_train_0.values
        else:
            np_mat = X_train_0

        if np.isfortran(np_mat):
            np_fortran = np_mat
        else:
            print("X_t[{}] asfortranarray".format(np_mat.shape));
            np_fortran = np.asfortranarray(np_mat)
        # Transpose just changes the strides, it doesn't touch the actual array
        if np_fortran.dtype != target_type:
            print("X_t[{}] astype {}=>{}".format(np_fortran.shape,np_fortran.dtype,target_type));
            np_out = np_fortran.astype(target_type)  # .transpose()
            #del np_fortran;     gc.collect()
        else:
            np_out = np_fortran
        gc.collect()
        return np_out

    def init_params_cpp(self, params, flag=0x0):
        if not isinstance(params, LiteMORT_params):
            if isinstance(params,dict):
                pass
            else:
                return
            #self.objective = params["objective"]
            self.objective = LiteMORT_params.alias_param(None,'objective','XXX',params,['objective',"application"])
            self.params = LiteMORT_params(self.objective,argv=params)
        else:
            self.params = params

        if self.objective=="binary":
            self._n_classes = 2
        elif self.objective=="XXX":
            print(f"objective is \"XXX\". Please check the parameters!!!")
            exit(-666)
        else:
            pass

        ca_list = []
        for k, v in self.params.__dict__.items():
            ca = M_argument()
            ca.Keys = k.encode('utf8')  # Python 3 strings are Unicode, char* needs a byte string
            if isinstance(v, set):
                v=list(v)[0]

            if k is 'representive':
                pass
            elif isinstance(v, str):
                ca.text = v.encode('utf8')
            elif isinstance(v, bool):
                ca.Values = (c_float)(v==True)
            elif isinstance(v, np.ndarray):
                ca.array = v.ctypes.data_as(c_void_p)
            else:
                ca.Values = (c_float)(v)  # Interface unclear, how would target function know how many floats?

            # ca.Index = v[3]
            ca_list.append(ca)
        self.ca_array = (M_argument * len(ca_list))(*ca_list)

    def EDA(self,flag=0x0):
        '''

        :param flag:
        :return:
        '''
        return
        nFeat,nSamp,no=self.preprocess.nFeature,self.preprocess.nSample,0
        X, y = self.preprocess.train_X, self.preprocess.train_y
        categorical_feature = self.preprocess.categorical_feature
        ca_list = []
        for feat in self.preprocess.features:
            ca = M_COLUMN()
            ca.name = str(feat).encode('utf8')
            ca.values = (c_float)(0)
            if (categorical_feature is not None) and (feat in categorical_feature or no in categorical_feature):
                # ca.Values = (c_float)(1)
                ca.text = 'category'.encode('utf8')
            ca_list.append(ca)
            no=no+1
        self.column_array = (M_COLUMN * len(ca_list))(*ca_list)
        #self.EDA_000(self.mort_params, all_data, None, user_test.shape[0], ca_list)
        if False:
            self.mort_eda(self.hLIB,X,y, nFeat, nSamp,0,self.column_array, len(ca_list), 0)

    def fit_index(self, X, y,train_index, eval_set=None, feat_dict=None, categorical_feature=None, params=None, flag=0x0):
        gc.collect()
        self.preprocess = Mort_Preprocess("fit_index",X, y, self)

        if (eval_set is not None and len(eval_set) > 0):
            eval_index = eval_set[0]
        pass
        print("====== LiteMORT_fit_index X_={} y_={}......".format(X.shape, y.shape))

        self.EDA(flag)

        self.mort_fit_index(self.hLIB, self.preprocess.train_X, self.preprocess.train_y, nFeat, nTrain,
                      self.preprocess.eval_X, self.preprocess.eval_y, nTest, 0)  # 1 : classification
        return self

    def fit_v0(self, X_train_0, y_train, eval_set=None, feat_dict=None, categorical_feature=None, params=None, flag=0x0):
        gc.collect()
        # self.preprocess.fit(X_train_0, y_train)
        # self.preprocess.transform(eval_set)
        self.preprocess = Mort_Preprocess(X_train_0, y_train, categorical_feature=categorical_feature)

        if (eval_set is not None and len(eval_set) > 0):
            X_test, y_test = eval_set[0]
        #a0=X_train_0['id_trade'].min();       a1=X_train_0['id_trade'].max();
        print("====== LiteMORT_fit X_train_0={} y_train={}......".format(X_train_0.shape, y_train.shape))
        train_y = self.problem.OnY(y_train, np.float64)
        # train_y = self.Y_t(y_train, np.float64)
        train_X = self.X_t(X_train_0, np.float32)
        #b0 = train_X[:,3].min();        b1 = train_X[:,3].max();
        self.preprocess.train_X = train_X.ctypes.data_as(POINTER(c_float))
        self.preprocess.train_y = train_y.ctypes.data_as(POINTER(c_double))
        nTrain, nFeat, nTest = train_X.shape[0], train_X.shape[1], 0
        eval_X, eval_y = None, None
        if eval_set is not None:
            eval_y0 = self.problem.OnY(y_test, np.float64)
            eval_X0 = self.X_t(X_test, np.float32)
            nTest = eval_X0.shape[0]
            self.preprocess.eval_X, self.preprocess.eval_y = eval_X0.ctypes.data_as(
                POINTER(c_float)), eval_y0.ctypes.data_as(POINTER(c_double))
        else:
            self.preprocess.eval_X, self.preprocess.eval_y = None,None
        self.EDA(flag)

        self.mort_fit(self.hLIB, self.preprocess.train_X, self.preprocess.train_y, nFeat, nTrain,
                      self.preprocess.eval_X, self.preprocess.eval_y, nTest, 0)  # 1 : classification
        if not (train_X is X_train_0):
            del train_X;
            gc.collect()
        if not (train_y is y_train):
            del train_y;
            gc.collect()
        if eval_X is not None and not (eval_X is X_test):
            del eval_X;
            gc.collect()
        if eval_y is not None and not (eval_y is y_test):
            del eval_y;
            gc.collect()

        return self

	#v0.1
    def MergeDataSets(self,merge_infos,comment=""):
        assert self.hLIB is not None
        self.merge_infos = merge_infos
        self.cpp_merge_sets=None
        if merge_infos is None or len(merge_infos) == 0:
            self.C_set_mergesets(self.hLIB,self.cpp_merge_sets, 0x0)
            return None

        no = 0
        merge_sets = []
        for item in merge_infos:
            if True:
                last_row = item['dataset'][-1:]
                nValid = last_row.count().sum()
                if nValid==0:
                    pass
                else:
                    item['dataset'] = item['dataset'].append(pd.Series(), ignore_index=True)  # name='last_nan'
                df = item['dataset']
            else:
                df = item['dataset'].copy()
                df = df.append(pd.Series(), ignore_index=True)#name='last_nan'
            feat_info=item['feat_info'] if 'feat_info' in item else {}
            #df=item['dataset']
            cols_on = item['on']
            pos_on = list(df.columns).index(cols_on[0])
            feat_info["merge_right"]=cols_on
            assert (pos_on >= 0)
            title = item['desc'] if 'desc' in item else f"merge_{no}"+comment
            mort_set = Mort_Preprocess(title, df, None,self.params, feat_info=feat_info)
            merge_sets.append(mort_set.cpp_dat_)
            no = no+1
        self.cpp_merge_sets = M_DATASET_LIST("merge_list", merge_sets)
        self.C_set_mergesets(self.hLIB,self.cpp_merge_sets,0x0)

    '''
            # v0.2
            # v0.3
                feat_dict   cys@1/10/2019
    '''
    def fit(self,X_train_0, y_train,eval_set=None,categorical_feature=None,discrete_feature=None, params=None,flag=0x0):
        self.profile.Snapshot("fit_0")
        print("====== LiteMORT_fit X_train_0={} y_train={}......".format(X_train_0.shape, y_train.shape))
        #self.categorical_feature = categorical_feature
        #self.discrete_feature = discrete_feature
        gc.collect()
        isUpdate,y_train_1,y_eval_update = self.problem.BeforeFit([X_train_0, y_train], eval_set)
        if isUpdate:
            y_train=y_train_1
        self.feat_info={"categorical":categorical_feature,"discrete":discrete_feature}
        self.train_set = Mort_Preprocess( "train",X_train_0,y_train,self.params,feat_info=self.feat_info,merge_infos=self.merge_infos)
        self.cpp_train_sets = M_DATASET_LIST("train",[self.train_set.cpp_dat_])
        self.eval_sets = [];            self.cpp_eval_sets=None
        if(eval_set is not None):
            for X_test, y_test in eval_set:
                if isUpdate:
                    y_test = y_eval_update[0]
                eval_set = Mort_Preprocess("eval",X_test, y_test, self.params,feat_info=self.feat_info,merge_infos=self.merge_infos)
                self.eval_sets.append(eval_set.cpp_dat_)
                #self.eval_sets.append(eval_set.cpp_dat_)
                self.cpp_eval_sets = M_DATASET_LIST("eval",self.eval_sets)
        #self.EDA(flag)

        self.mort_fit_1(self.hLIB, self.cpp_train_sets,self.cpp_eval_sets, 0)
        self.profile.Stat("fit_0","fit_1")

        return self


    def predict(self, X_,pred_leaf=False, pred_contrib=False,raw_score=False,num_iteration=-1, flag=0x0):
        """Predict class or regression target for X.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape (n_samples, n_features)
            The input samples. Internally, it will be converted to
            ``dtype=np.float32`` and if a sparse matrix is provided
            to a sparse ``csr_matrix``.

        Returns
        -------
        y : array, shape (n_samples,)
            The predicted values.
        """
        self.profile.Snapshot("PRED_0")
        # print("====== LiteMORT_predict X_={} ......".format(X_.shape))
        Y_ = self.predict_raw(X_,pred_leaf, pred_contrib,raw_score,flag=flag)
        Y_ = self.problem.AfterPredict(X_,Y_)
        Y_ = self.problem.OnResult(Y_,pred_leaf,pred_contrib,raw_score)
        self.profile.Stat("PRED_0","PRED_1",dump=self.params.verbose>0)
        return Y_

    def predict_raw_v0(self, X_,pred_leaf=False, pred_contrib=False,raw_score=False,flag=0x0):
        dim, nFeat = X_.shape[0], X_.shape[1];
        Y_ = np.zeros(dim, dtype=np.float64)
        tY = Y_  # self.Y_t(Y_, np.float64)
        tX = self.X_t(X_, np.float32)
        self.mort_predcit(self.hLIB, tX.ctypes.data_as(POINTER(c_float)), tY.ctypes.data_as(POINTER(c_double)), nFeat,dim, 0)
        if not (tX is X_):
            del tX;
        gc.collect()
        return Y_

    def predict_raw(self, X_,pred_leaf=False, pred_contrib=False,raw_score=False,flag=0x0):
        dim, nFeat = X_.shape[0], X_.shape[1];
        Y_ = np.zeros(dim, dtype=np.float64)
        predict_set = Mort_Preprocess("predict_raw",X_, Y_, params=self.params, feat_info=self.feat_info,merge_infos=self.merge_infos)
        cpp_test_set = M_DATASET_LIST("predict_raw",[predict_set.cpp_dat_])
        #self.mort_predcit_1(self.hLIB, predict_set.cX,predict_set.cY, nFeat,dim, 0)
        self.mort_predcit_1(self.hLIB, cpp_test_set, 0)
        gc.collect()
        return Y_

    #奇怪的教训，会影响其它列,需要重写，暂时这样！！！
    def Imputer(self, params,X_, Y_,np_float, flag=0x0):
        # print("====== LiteMORT_EDA X_={} ......".format(X_.shape))
        dim, nFeat = X_.shape[0], X_.shape[1];
        if Y_ is None:
            Y_ = np.zeros(dim, dtype=np.float64)
        #print("head={}\ntail={}".format(X_.head(),X_.tail()))
        tX = self.X_t(X_, np_float)
        #tX = self.X_t(tX, np_float)
        if np_float==np.float32:
            self.mort_imputer_f(tX.ctypes.data_as(POINTER(c_float)),Y_.ctypes.data_as(POINTER(c_double)) , nFeat, dim, 0)
        elif np_float==np.float64:
            self.mort_imputer_d(tX.ctypes.data_as(POINTER(c_double)), Y_.ctypes.data_as(POINTER(c_double)), nFeat, dim, 0)
        else:
            assert(0)
        imputed_DF = pd.DataFrame(tX)
        imputed_DF.columns = X_.columns;        imputed_DF.index = X_.index
        X_ = imputed_DF
        #print("head={}\ntail={}".format(X_.head(), X_.tail()))
        return X_

    def feature_name(self):
        """Get names of features.
        """
        num_feature = self.num_feature()
        # Get name of features
        tmp_out_len = ctypes.c_int(0)
        string_buffers = [ctypes.create_string_buffer(255) for i in range_(num_feature)]
        ptr_string_buffers = (ctypes.c_char_p * num_feature)(*map(ctypes.addressof, string_buffers))
        (_LIB.LGBM_BoosterGetFeatureNames(
            self.handle,
            ctypes.byref(tmp_out_len),
            ptr_string_buffers))
        if num_feature != tmp_out_len.value:
            raise ValueError("Length of feature names doesn't equal with num_feature")
        return [string_buffers[i].value.decode() for i in range(num_feature)]

    def feature_importance(self, importance_type='split', iteration=None):
        """Get feature importances.

        Parameters
        ----------
        importance_type : string, optional (default="split")
            How the importance is calculated.
            If "split", result contains numbers of times the feature is used in a model.
            If "gain", result contains total gains of splits which use the feature.
        iteration : int or None, optional (default=None)
            Limit number of iterations in the feature importance calculation.
            If None, if the best iteration exists, it is used; otherwise, all trees are used.
            If <= 0, all trees are used (no limits).

        Returns
        -------
        result : numpy array
            Array with feature importances.
        """
        if iteration is None:
            iteration = self.best_iteration
        if importance_type == "split":
            importance_type_int = 0
        elif importance_type == "gain":
            importance_type_int = 1
        else:
            importance_type_int = -1
        result = np.zeros(self.num_feature(), dtype=np.float64)
        (_LIB.LGBM_BoosterFeatureImportance(
            self.handle,
            ctypes.c_int(iteration),
            ctypes.c_int(importance_type_int),
            result.ctypes.data_as(ctypes.POINTER(ctypes.c_double))))
        if importance_type_int == 0:
            return result.astype(int)
        else:
            return result

    def plot_importance(self,mort, ax=None, height=0.2,xlim=None, ylim=None,
            title='Feature importance',xlabel='Feature importance', ylabel='Features',importance_type='split',
            max_num_features=None, ignore_zero=True, figsize=None, grid=True,precision=None, **kwargs):
        """Plot model's feature importances.

        Parameters
        ----------
        booster : Booster or LGBMModel
            Booster or LGBMModel instance which feature importance should be plotted.
        ax : matplotlib.axes.Axes or None, optional (default=None)
            Target axes instance.
            If None, new figure and axes will be created.
        height : float, optional (default=0.2)
            Bar height, passed to ``ax.barh()``.
        xlim : tuple of 2 elements or None, optional (default=None)
            Tuple passed to ``ax.xlim()``.
        ylim : tuple of 2 elements or None, optional (default=None)
            Tuple passed to ``ax.ylim()``.
        title : string or None, optional (default="Feature importance")
            Axes title.
            If None, title is disabled.
        xlabel : string or None, optional (default="Feature importance")
            X-axis title label.
            If None, title is disabled.
        ylabel : string or None, optional (default="Features")
            Y-axis title label.
            If None, title is disabled.
        importance_type : string, optional (default="split")
            How the importance is calculated.
            If "split", result contains numbers of times the feature is used in a model.
            If "gain", result contains total gains of splits which use the feature.
        max_num_features : int or None, optional (default=None)
            Max number of top features displayed on plot.
            If None or <1, all features will be displayed.
        ignore_zero : bool, optional (default=True)
            Whether to ignore features with zero importance.
        figsize : tuple of 2 elements or None, optional (default=None)
            Figure size.
        grid : bool, optional (default=True)
            Whether to add a grid for axes.
        precision : int or None, optional (default=None)
            Used to restrict the display of floating point values to a certain precision.
        **kwargs
            Other parameters passed to ``ax.barh()``.

        Returns
        -------
        ax : matplotlib.axes.Axes
            The plot with model's feature importances.
        """

        importance = mort.feature_importance(importance_type=importance_type)
        feature_name = mort.feature_name()

        if not len(importance):
            raise ValueError("Booster's feature_importance is empty.")

        tuples = sorted(zip(feature_name, importance), key=lambda x: x[1])
        if ignore_zero:
            tuples = [x for x in tuples if x[1] > 0]
        if max_num_features is not None and max_num_features > 0:
            tuples = tuples[-max_num_features:]
        labels, values = zip(*tuples)

        if ax is None:
            if figsize is not None:
                _check_not_tuple_of_2_elements(figsize, 'figsize')
            _, ax = plt.subplots(1, 1, figsize=figsize)

        ylocs = np.arange(len(values))
        ax.barh(ylocs, values, align='center', height=height, **kwargs)

        for x, y in zip(values, ylocs):
            ax.text(x + 1, y,_float2str(x, precision) if importance_type == 'gain' else x,va='center')

        ax.set_yticks(ylocs)
        ax.set_yticklabels(labels)

        if xlim is not None:
            _check_not_tuple_of_2_elements(xlim, 'xlim')
        else:
            xlim = (0, max(values) * 1.1)
        ax.set_xlim(xlim)

        if ylim is not None:
            _check_not_tuple_of_2_elements(ylim, 'ylim')
        else:
            ylim = (-1, len(values))
        ax.set_ylim(ylim)

        if title is not None:
            ax.set_title(title)
        if xlabel is not None:
            ax.set_xlabel(xlabel)
        if ylabel is not None:
            ax.set_ylabel(ylabel)
        ax.grid(grid)
        return ax


