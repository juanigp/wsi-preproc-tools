BINARIZATION_FUNCTIONS = {}
PATCH_FILTER_FUNCTIONS = {}

def register_binarization_function(fun):
    fun_name = fun.__name__
    BINARIZATION_FUNCTIONS[fun_name] = fun
    return fun

def register_patch_filter_function(fun):
    fun_name = fun.__name__
    PATCH_FILTER_FUNCTIONS[fun_name] = fun
    return fun